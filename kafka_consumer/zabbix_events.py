from confluent_kafka import Consumer, KafkaException
from db.config import events_collection
import json

conf = {
    'bootstrap.servers': 'localhost:9092', 
    'group.id': 'zabbix',
    'auto.offset.reset': 'latest'
}

consumer = Consumer(conf)
consumer.subscribe(['events'])

try:
    while True:
        msg = consumer.poll(1.0) 
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())
        else:
            if msg is None:
                continue
            print(f"Received message: {msg.value().decode('utf-8')} from {msg.topic()}")
            events_collection.insert_one(json.loads(msg.value().decode('utf-8')))
            print("Document inserted successfully ...")

except KeyboardInterrupt:
    print("Stopping consumer...")
finally:
    consumer.close()