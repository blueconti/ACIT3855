import connexion
import swagger_ui_bundle
import datetime
import json
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from book_campsites import BookCampsite
from payments import Payment
import requests
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
import yaml
import logging.config

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())
logger.info(f'Connecting to DB, Hostname:{app_config["datastore"]["hostname"]}, Port:{app_config["datastore"]["port"]}')

DB_ENGINE = create_engine(
    f"mysql+pymysql://{app_config['datastore']['user']}:{app_config['datastore']['password']}@{app_config['datastore']['hostname']}:{app_config['datastore']['port']}/{app_config['datastore']['db']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def get_book_campsite(timestamp):
    """ Gets new campsite readings after the timestamp """
    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
    readings = session.query(BookCampsite).filter(BookCampsite.date_created >=
                                                  timestamp_datetime)
    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()

    logger.info("Query for Book campsite readings after %s returns %d results" %
                (timestamp, len(results_list)))
    return results_list, 200


def get_payment(timestamp):
    """ Gets new payment after the timestamp """
    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
    readings = session.query(Payment).filter(Payment.date_created >=
                                             timestamp_datetime)
    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()

    logger.info("Query for Payment readings after %s returns %d results" %
                (timestamp, len(results_list)))
    return results_list, 200

# Booking event
def book_campsite(body):
    # CREATE SESSION
    session = DB_SESSION()

    unique_book_campsite = body['book_id']

    book = BookCampsite(body['book_id'],
                        body['campsite'],
                        body['client_id'],
                        body['number_of_guests'],
                        body['timestamp'],
                        body['trace_id'])
    
    session.add(book)

    session.commit()
    session.close()

    logger.info(
        f"Stored event book_campsite request with a unique id of {unique_book_campsite}")

    logger.info(
        f"Connecting to DB. Hostname:{app_config['datastore']['hostname']}, Port:{app_config['datastore']['port']}"
    )
    
    
    return NoContent, 201

# Payment event
def payment(body):

    session = DB_SESSION()

    unique_payment = body['payment_id']


    book = Payment(body['payment_id'],
                   body['campsite'],
                   body['client_id'],
                   body['number_of_guests'],
                   body['timestamp'],
                   body['trace_id'])
    
    session.add(book)
    
    session.commit()
    session.close()

    logger.info(
        f"Stored event book_campsite request with a unique id of {unique_payment}")

    logger.info(
        f"Connecting to DB. Hostname:{app_config['datastore']['hostname']}, Port:{app_config['datastore']['port']}"
    )
    
    return NoContent, 201

def process_messages():
    hostname = "%s:%d" % (app_config["events"]["hostname"],app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(consumer_group=b'event_group',reset_offset_on_start=False, auto_offset_reset=OffsetType.LATEST)

    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)

        payload = msg["payload"]

        if msg["type"] == "Book":
            book_campsite(payload)
        elif msg["type"] == "Payment":
            payment(payload)

        consumer.commit_offsets()
        


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8090)
    t1 = Thread(target=process_messages())
    t1.setDaemon(True)
    t1.start()
