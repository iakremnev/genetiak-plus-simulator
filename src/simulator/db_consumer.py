import json
import os

from confluent_kafka import Consumer
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from simulator.orm import Base as ORMBase
from simulator.orm import DataModel1, DataModel2, DataModel3

TOPIC_TO_ORM = {"topic1": DataModel1, "topic2": DataModel2, "topic3": DataModel3}
KAFKA_SERVER = os.getenv("KAFKA_SERVER")


def write_event_to_db(event: dict, topic: str) -> None:
    """Translates event to ORM instance and dumps it to the DB

    Parameters
    ----------
    event
        Deserialized Kafka event message
    topic
        Topic of origin
    """
    try:
        model = TOPIC_TO_ORM[topic]
        instance = model(**event)

        with Session(engine) as session:
            session.add(instance)
            session.commit()
    except TypeError:
        print("ERROR: Malformed event, skip dumping")
    except IntegrityError as e:
        print(f"ERROR: Skipping event dumping because of\n{e!r}")


def run(consumer: Consumer) -> None:
    """Consumes messages from pre-defined topics until stopped manually"""

    try:
        while True:
            message = consumer.poll(1.0)

            if message is None:
                continue
            if message.error():
                print(f"Consumer error: {message.error()}")
                continue

            print(f"Received message in topic {message.topic()} @ offset {message.offset()}")
            payload = json.loads(message.value())
            write_event_to_db(payload, message.topic())

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    # Set up database and connection
    engine = create_engine("sqlite:////opt/database/features.db", echo=True)
    ORMBase.metadata.create_all(engine)

    # Set up Kafka consumer
    consumer = Consumer({"bootstrap.servers": KAFKA_SERVER, "group.id": "db_dump", "auto.offset.reset": "earliest"})
    consumer.subscribe(list(TOPIC_TO_ORM.keys()))

    run(consumer)
    consumer.close()
