FROM python:3.10.7-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    build-essential

COPY ./compose/crawler/requirements.txt /
RUN pip3 install --upgrade pip
RUN pip3 install -r /requirements.txt --no-cache-dir

COPY ./src/ /app/src/

WORKDIR /app