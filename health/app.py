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
from base import Base
from flask_cors import CORS, cross_origin
import os
from health import Health
from time import sleep
import sqlite3
from pykafka import KafkaClient

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())


with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def populate_health():

    session = DB_SESSION()
    results = session.query(Health).order_by(Health.last_updated.desc()).first()
    session.close()

    if not results:
        health = {
            "receiver": "Running",
            "storage": "Down",
            "processing": "Running",
            "audit": "Running",
            "last_updated": "2016-08-29T09:12:33"
        }
    else:
        health = results.to_dict()

    retry_count = 0
    while retry_count < app_config["kafka_connect"]["retry_count"]:
        try:
            receiver_health = requests.get(app_config['receiver']['url'], timeout=5)
            print(receiver_health)
            if receiver_health.status_code == 200:
                receiver_status = "Running"
                health['receiver_status'] = receiver_status
        except:
            retry_count += 1
            receiver_status = "Down"
            health['receiver_status'] = receiver_status
            sleep(app_config["kafka_connect"]["sleep_time"])
        else:
            break

    while retry_count < app_config["kafka_connect"]["retry_count"]:
        try:
            storage_health = requests.get(app_config['storage']['url'], timeout=5)
            print(storage_health)
            if storage_health.status_code == 200:
                storage_status = "Running"
                health['storage_status'] = storage_status
        except:
            retry_count += 1
            storage_status = "Down"
            health['storage_status'] = storage_status
            sleep(app_config["kafka_connect"]["sleep_time"])
        else:
            break
    
    while retry_count < app_config["kafka_connect"]["retry_count"]:
        try:
            processing_health = requests.get(app_config['processing']['url'], timeout=5)
            print(processing_health)
            if processing_health.status_code == 200:
                processing_status = "Running"
                health['processing_status'] = processing_status
        except:
            retry_count += 1
            processing_status = "Down"
            health['processing_status'] = processing_status
            sleep(app_config["kafka_connect"]["sleep_time"])
        else:
            break

    while retry_count < app_config["kafka_connect"]["retry_count"]:
        try:
            audit_log_health = requests.get(app_config['audit_log']['url'], timeout=5)
            print(audit_log_health)
            if audit_log_health.status_code == 200:
                audit_log_status = "Running"
                health['audit_log_status'] = audit_log_status
        except:
            retry_count += 1
            audit_log_status = "Down"
            health['audit_log_status'] = audit_log_status
            sleep(app_config["kafka_connect"]["sleep_time"])
        else:
            break
    
    timestamp = datetime.datetime.now()

    session = DB_SESSION()

    health_new = Health(health["receiver_status"],
                      health["storage_status"],
                      health["processing_status"],
                      health["audit_status"],
                      timestamp)

    session.add(health_new)

    session.commit()
    session.close()

def get_health():
    logger.info("Request has started")

    session = DB_SESSION()
    results = session.query(Health).order_by(Health.last_updated.desc()).first()
    session.close()

    if not results:
        health = {
            "receiver": "Running",
            "storage": "Down",
            "processing": "Running",
            "audit": "Running",
            "last_updated": "2016-08-29T09:12:33"
        }
    else:
        health = results.to_dict()

    logger.debug(health)

    logger.info("Request has completed")

    return health, 200

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_health, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)



if __name__ == "__main__":
    init_scheduler()
    app.run(port=8120, use_reloader=False)