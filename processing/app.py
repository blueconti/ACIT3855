import connexion
import swagger_ui_bundle
from datetime import datetime
import json
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import requests
import yaml
import logging.config
import uuid
from apscheduler.schedulers.background import BackgroundScheduler
import os.path
import datetime
from stats import Stats
from base import Base
from flask_cors import CORS, cross_origin
import os
if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"



with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')
logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def populate_stats():
    logger.info("Start Periodic Processing")    

    session = DB_SESSION()
    results = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    session.close()

    if not results:
        stats = {
            "num_book": 0,
            "num_payment": 0,
            "sum_book_total": 0,
            "avg_book_total": 0,
            "last_updated": "2016-08-29T09:12:33"
        }
    else:
        stats = results.to_dict()
    
    start_timestamp = stats['last_updated']
    current_timestamp = datetime.datetime.now()
    end_timestamp = current_timestamp.strftime("%Y-%m-%dT%H:%M:%S")


    get_make_reservation = requests.get(app_config['eventstore1']['url'] + "?start_timestamp=" + start_timestamp + "&end_timestamp=" + end_timestamp)
    get_payments = requests.get(app_config['eventstore2']['url'] + "?start_timestamp=" + start_timestamp + "&end_timestamp=" + end_timestamp)

    stats['num_book'] = stats['num_book']

    stats['num_payment'] = stats['num_payment']  + len(get_payments.json())

    stats['sum_book_total'] = 0 + len(get_make_reservation.json())

    stats['avg_book_total'] = stats['avg_book_total']

    session = DB_SESSION()

    stats_new = Stats(stats["num_book"],
                  stats["num_payment"],
                  stats["sum_book_total"],
                  stats["avg_book_total"],
                  datetime.datetime.now())

    session.add(stats_new)

    session.commit()
    session.close()

    logger.debug("Updated stats values: {}".format(stats))

    logger.info("End Periodic Processing")


def get_stats():
    logger.info("Start Periodic Processing")

    session = DB_SESSION()
    results = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    session.close()

    if not results:
        stats = {
            "num_book": 0,
            "num_payment": 0,
            "sum_book_total": 0,
            "avg_book_total": 0,
            "last_updated": "2016-08-29T09:12:33"
        }

    else:
        stats = results.to_dict()    
    logger.debug(stats)
    logger.info("Reuqest has completed")
    return stats, 200


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()
def health():
    logger.info("Processing service is running")
    return NoContent, 200


app = connexion.FlaskApp(__name__, specification_dir='')
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml", base_path="/processing", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)
