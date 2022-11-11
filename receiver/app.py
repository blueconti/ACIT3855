
import connexion
import swagger_ui_bundle
import datetime
import json
from connexion import NoContent
from pykafka import KafkaClient
import yaml
import uuid



with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())


# Booking event
def book_campsite(body):
    trace = str(uuid.uuid4())
    body['trace_id'] = trace

    server = f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}'
    client = KafkaClient(hosts=server)
    topic = client.topics[app_config["events"]["topic"]]
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
