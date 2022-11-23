
import connexion
import swagger_ui_bundle
import datetime
import json
from connexion import NoContent
from pykafka import KafkaClient
import yaml
import uuid
import logging.config
from time import sleep



with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())
    make_reservation_url = app_config['event1']['url']
    payment_url = app_config['event2']['url']
    kafka_server = app_config["events"]["hostname"]
    kafka_port = app_config["events"]["port"]
    kafka_topic = app_config["events"]["topic"]

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)


logger = logging.getLogger('basicLogger')

hostname = "%s:%d" % (app_config["events"]["hostname"],app_config["events"]["port"])

retry_count = 0
while retry_count < app_config["kafka_connect"]["retry_count"]:
    try:
        logger.info("trying to connect, attempt: %d" % (retry_count))
        print(hostname)
        client = KafkaClient(hosts=hostname)
        topic = client.topics[str.encode(app_config['events']['topic'])]
        producer = topic.get_sync_producer()
    except:
        logger.info("attempt %d failed, retry after 5 seconds" % (retry_count))
        retry_count += 1
        sleep(app_config["kafka_connect"]["sleep_time"])

# Booking event
def book_campsite(body):
    trace = str(uuid.uuid4())
    body['trace_id'] = trace

    server = f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}'
    client = KafkaClient(hosts=server)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    producer = topic.get_sync_producer()
    msg = { "type": "Book",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
        }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))


    return 201

# Payment event
def payment(body):
    trace = str(uuid.uuid4())
    body['trace_id'] = trace

    server = f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}'
    client = KafkaClient (hosts=server)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    producer = topic.get_sync_producer()
    msg = { "type": "Payment",
            "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "payload": body
            }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    return 201





app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
