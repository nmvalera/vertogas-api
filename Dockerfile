FROM python:3.6-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

ONBUILD COPY setup.py /usr/src/app/
ONBUILD RUN pip install --no-cache-dir -e .

ONBUILD COPY . /usr/src/app

EXPOSE 80
