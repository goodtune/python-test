FROM python:3-slim
MAINTAINER Gary Reynolds <gary@touch.asn.au>

RUN pip install --no-cache-dir tox devpi-client

VOLUME /src
WORKDIR /src

ENTRYPOINT ["tox"]
