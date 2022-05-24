import json
from time import sleep
from time import time

from confluent_kafka import avro, Producer
from confluent_kafka.avro import AvroProducer
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import SerializingProducer
from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer

import random

import user_pb2

BOOTSTRAP_SERVERS = 'kafka:9092'
SCHEMA_REGISTRY_URL = 'http://schema-registry:8081'
TRANSFER_TOPIC_NAME = 'test.transfer'
RECIPIENT_TOPIC_NAME = 'test.recipient'
JSON_TRANSFER_TOPIC_NAME = 'test.json.transfer'
JSON_RECIPIENT_TOPIC_NAME = 'test.json.recipient'
USER_TOPIC_NAME = 'test.proto.user'
TRANSFER_AVRO_SCHEMA_FILE = '/test-data/transfer.avsc'
RECIPIENT_AVRO_SCHEMA_FILE = '/test-data/recipient.avsc'
RECIPIENTS_COUNT = 2000
RECIPIENTS_LIST = open('/test-data/recipients.csv')


def get_random_recipient():
    offset = random.randrange(RECIPIENTS_COUNT)
    RECIPIENTS_LIST.seek(offset)
    RECIPIENTS_LIST.readline()
    recipient_row = RECIPIENTS_LIST.readline()

    if len(recipient_row) == 0:
        RECIPIENTS_LIST.seek(0)
        recipient_row = RECIPIENTS_LIST.readline()
    return recipient_row


admin_client = AdminClient({
    'bootstrap.servers': BOOTSTRAP_SERVERS
})

admin_client.create_topics([NewTopic(TRANSFER_TOPIC_NAME, 1, 1),
                            NewTopic(RECIPIENT_TOPIC_NAME, 1, 1),
                            NewTopic(JSON_TRANSFER_TOPIC_NAME, 1, 1),
                            NewTopic(JSON_RECIPIENT_TOPIC_NAME, 1, 1),
                            NewTopic(USER_TOPIC_NAME, 1, 1)])

transfer_value_schema = avro.load(TRANSFER_AVRO_SCHEMA_FILE)
recipient_value_schema = avro.load(RECIPIENT_AVRO_SCHEMA_FILE)

key_schema = avro.loads('{"type": "string"}')

avro_producer = AvroProducer(
    {'bootstrap.servers': BOOTSTRAP_SERVERS, 'schema.registry.url': SCHEMA_REGISTRY_URL},
    default_key_schema=key_schema, default_value_schema=transfer_value_schema)

schema_registry_conf = {'url': SCHEMA_REGISTRY_URL}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

protobuf_serializer = ProtobufSerializer(user_pb2.User,
                                         schema_registry_client)

producer_conf = {'bootstrap.servers': BOOTSTRAP_SERVERS,
                 'key.serializer': StringSerializer('utf_8'),
                 'value.serializer': protobuf_serializer}

protobuf_producer = SerializingProducer(producer_conf)

json_producer = Producer({'bootstrap.servers': BOOTSTRAP_SERVERS})

while True:
    recipient = get_random_recipient().split(',')
    recipient_id = recipient[0]
    recipient_name = recipient[1]
    recipient_address = recipient[2]

    transfer_id = random.randrange(1000000)
    profile_id = random.randrange(100000)

    #   Avro events
    recipient_event = {'id': int(recipient_id), 'name': recipient_name, 'address': recipient_address}
    transfer_event = {'id': (transfer_id), 'profile_id': profile_id, 'amount': random.randrange(100000),
                      'transfer_time': round(time() * 1000),
                      'recipient_id': int(recipient_id),
                      'from_currency': str(random.randrange(10)), 'to_currency': str(random.randrange(10))}

    avro_producer.produce(topic=RECIPIENT_TOPIC_NAME,
                          value=recipient_event,
                          key=recipient_id,
                          key_schema=key_schema,
                          value_schema=recipient_value_schema)
    avro_producer.produce(topic=TRANSFER_TOPIC_NAME,
                          value=transfer_event,
                          key=str(transfer_id),
                          key_schema=key_schema,
                          value_schema=transfer_value_schema)

    avro_producer.flush()

    #   Protobuf events
    user = user_pb2.User(profile_id=profile_id, user_name=str(profile_id))
    protobuf_producer.produce(topic=USER_TOPIC_NAME, partition=0, key=str(profile_id), value=user)
    protobuf_producer.flush()

    #   Json events
    recipient_json = json.dumps(recipient_event)
    transfer_json = json.dumps(transfer_event)
    json_producer.produce(topic=JSON_RECIPIENT_TOPIC_NAME, key=recipient_id, value=recipient_json)
    json_producer.produce(topic=JSON_TRANSFER_TOPIC_NAME, key=str(transfer_id), value=transfer_json)
    json_producer.flush()

    sleep(0.3)
    print(str.format('Sending recipient event with id: {}, and transfer event with id: {}',
                     recipient_id, transfer_id))
