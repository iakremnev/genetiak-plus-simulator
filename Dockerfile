FROM python:3.11 AS base

WORKDIR /usr/src/app

COPY pyproject.toml ./
COPY src ./
RUN pip install .

CMD ["echo", "Please use specific script to run this image"]