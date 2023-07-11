import shelve
import os
import json
from typing import Mapping
from confluent_kafka import Consumer, Producer


KAFKA_SERVER = os.getenv("KAFKA_SERVER")
TOPICS = ["topic1", "topic2", "topic3"]
ACK_TOPIC = "ack"


class Acknowledger:
    """Event integrity reporter

    Listens to subsribed topics, collecting information on event ids.
    When events with the same id arrive in all feature topics,
    acknowledger sends an ack event to a special topic.

    Parameters
    ----------
    cache
        Cache storage interface (e.g. dict or shelve)
    """

    def __init__(self, cache: Mapping[str, set[str]]) -> None:
        self.consumer = Consumer(
            {"bootstrap.servers": KAFKA_SERVER, "group.id": "acker", "auto.offset.reset": "earliest"}
        )
        self.producer = Producer({"bootstrap.servers": KAFKA_SERVER})
        self.cache = cache

        self.consumer.subscribe(TOPICS)

    def check_update_cache(self, id: str, topic: str) -> bool:
        """Add info about event id arriving in particular topic and check data completeness

        Parameters
        ----------
        id
            Event id
        topic
            Topic in which the event arrived

        Returns
        -------
            This event id has arrived in all topics
        """
        record = self.cache.get(id) or set()
        record.add(topic)
        self.cache[id] = record

        return record == set(TOPICS)

    def ack_complete(self, id: str) -> None:
        self.producer.poll(0)

        data = {"id": id}
        self.producer.produce(ACK_TOPIC, json.dumps(data).encode())

        self.producer.flush()

    def run(self) -> None:
        """Consume events and produce acknowledgements"""

        while True:
            message = self.consumer.poll(1.0)

            if message is None:
                continue

            print(message, message.value())
            event_id = str(int(json.loads(message.value()).get("id")))

            if event_id is None:
                print("Malformed event")
                continue

            if self.check_update_cache(event_id, message.topic()):
                self.ack_complete(event_id)

    def __exit__(self, *exc):
        self.consumer.close()


if __name__ == "__main__":
    with shelve.open("ack_cache.db") as storage:
        with Acknowledger(storage) as acknowledger:
            acknowledger.run()
