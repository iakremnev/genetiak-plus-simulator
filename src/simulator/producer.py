import argparse
import functools
import os
import random
import time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from confluent_kafka import Producer

MAX_THREADS = 3


def delivery_report(err, msg):
    """Called once for each message produced to indicate delivery result.
    Triggered by poll() or flush()."""
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} at offset {msg.offset()}")


def get_topic(filename: os.PathLike) -> str:
    """Generates Kafka topic name for particular data source file"""
    return os.path.splitext(os.path.basename(filename))[0]


def stream_events(source: os.PathLike, topic: str, broker_address: str, max_delay: int = 0) -> None:
    """Streams feature rows from source table as event to Kafka

    Parameters
    ----------
    source
        Xlsx spreadsheet with data
    topic
        Destination Kafka topic
    broker_address
        Destination Kafka server address
    max_delay, optional
        Maximum delay between events (ms), by default 0
    """
    df = pd.read_excel(source, na_values="NA")
    producer = Producer({"bootstrap.servers": broker_address})

    for _, row in df.iterrows():
        time.sleep(random.randint(0, max_delay) / 1000)
        producer.poll(0)

        data = row.to_json().encode()
        producer.produce(topic, data, callback=delivery_report)

    producer.flush()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Async message producer reading data from feature tables")
    parser.add_argument("--delay", type=int, default=0, help="Maximum delay between messages (ms)")
    parser.add_argument("data", nargs="+", help="Feature table in xlsx format")

    args = parser.parse_args()

    for file in args.data:
        if not os.path.exists(file):
            print(f"{file} doesn't exist")
            exit(1)

    with ThreadPoolExecutor(MAX_THREADS) as pool:
        pool.map(
            functools.partial(stream_events, broker_address=os.getenv("KAFKA_SERVER"), max_delay=args.delay),
            args.data,
            [get_topic(file) for file in args.data],
        )
