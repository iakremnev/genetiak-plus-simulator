# Genetika+ simulator

This project simulates data pipeline that interacts with Kafka to collect events into a database.

## Run

To run the simulation, launch docker compose cluster in the project root

```bash
$ docker compose up
```

The simulation will set up Kafka server, a single producer and several consumers, and perform data streaming and acquisition.
The simulation results can be monitored through [UI for Apache Kafka](https://github.com/provectus/kafka-ui), and the database can be inspected.

To access the UI, go to http://localhost:8080.

## Architecture

![](img/arch.png)

Kafka producer and consumers are implemented as Confluent Kafka Python clients. The data flow is following:

1. Producer reads rows from `data/sim_fileN.xlsx` and concurrently sends them to respective topic through Confluent Producer asynchronous API. Topics *topic1*, *topic2* and *topic3* are present.
1. Database consumer is subscribed to all three topics and reads messages in a single thread. Having read a message, the consumer maps its fields to respective relation through SQLAlchemy ORM. Then, using database engine, it writes single rows.
1. Ack consumer is also subscribed to the three topics and reads messages in a single thread. It maintains persistent cache to register occurrence of the same event id in the three topics. Once an event id is delivered to all three topics, the Ack consumer produces (doh!) an ack event to the *ack* topic.
1. UI for Apache Kafka can 

## Analysis

Below are time series measured from event creation timestamps:

![](img/timestamps.png)

Each data point represents an event with specific id created in the corresponding topic with its time of creation relative to the first created event.

It can be seen that the *ack* events go always after the latest occurrence this event in *topicN* topic but not with a long delay. Actually, the delays between the latest *topicN* occurrence and *ack* event are almost constant with the median value of 11.5 ms (see graph below).

![](img/delay.png)

## Point of interest

* Producer simulates data source concurrency through multithreading, which is a good mechanism even in presence of GIL.
* Data models are described with SQLAlchemy declarative ORMs, but [pydantic](https://github.com/tiangolo/pydantic-sqlalchemy) or [marshmallow](https://github.com/marshmallow-code/marshmallow-sqlalchemy) can be used to more precisely validate data integrity.
* SQLite database is chosen for the sake of simplicity, but can be easily substituted with Postresql thanks to SQLAlchemy engine. Database is stored on disk, expect SQL Integrity errors on second run of the simulator (try revert the DB to initial empty state).
* Acknowledger (ack consumer) uses persistent storage in form of Python shelve for its cache. This is an important precautionary measure to address unexpected service shutdown and loss of partially collected events. Redis can be used in place of the shelve.
* Kafka service takes some time to set up after starting Compose cluster, therefore all depended services were manually tweaked to sleep some time after start. If some services display unexpected behaviour (e.g. DB consumer receives messages only from a single topic), try increasing sleep time in `docker-compmose.yaml`
* For Kafka monitoring [kafka-exporter](https://github.com/danielqsj/kafka_exporter) can be used with the Prometheus & Graphana stack. It's very handy information for larger scale Kafka cluster, however impractical for analyzing individual message metrics on the scale of this simulator.