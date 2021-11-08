# pull the official base image
FROM python:3.9-slim-buster

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get -y install docker libmariadb-dev python-mysqldb

RUN pip3 install docker-compose

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/app

EXPOSE 8000

RUN mkdir /var/www && mkdir /var/www/static && mkdir /usr/src/app/static

ENTRYPOINT ["/usr/src/app/docker-entrypoint.sh"]
