FROM python:3.11 AS base

WORKDIR /usr/src/app

COPY pyproject.toml ./
RUN pip install .
COPY src ./

CMD ["echo", "Please use specific script to run this image"]