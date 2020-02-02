FROM python:3.7
MAINTAINER Eduard Asriyan <ed-asriyan@protonmail.com>

WORKDIR /application

RUN openssl genrsa -out private_key.pem 2048 && openssl rsa -in private_key.pem -outform PEM -pubout -out public_key.pem

ADD requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ADD . .

CMD python main.py --device $DEVICE --db-uri $DB_URI
