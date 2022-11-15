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



with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def populate_stats():
    logger.info("Start Periodic Processing")    

    session = DB_SESSION()
    time = datetime.datetime.now
    results = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    session.close()

    if not results:
        stats = Stats(0,0,0,0,time)
    else:
        stats = results.to_dict()
    
        previous_datetime = stats['last_updated']

        get_make_reservation = requests.get(app_config['eventstore1']['url'] + "?timestamp=" + previous_datetime)
        get_payments = requests.get(app_config['eventstore2']['url'] + "?timestamp=" + previous_datetime)

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
    return NoContent, 201

    logger.debug("Updated stats values: {}".format(stats))

    logger.info("End Periodic Processing")


def get_stats():
    logger.info("Start Periodic Processing")

    session = DB_SESSION()
    time = datetime.datetime.now
    results = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    session.close()

    if not results:
        stats = Stats(0,0,0,0,time)
        session.add(stats)
        session.commit()
        session.close()
    else:
        logger.debug(stats)

        logger.info("Reuqest has completed")
        stats = results.to_dict()
        return stats, 200
    


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)
