FROM python:3-slim
MAINTAINER Gary Reynolds <gary@touch.asn.au>

RUN curl -s https://bootstrap.pypa.io/get-pip.py | python2.7
RUN pip2.7 install --no-cache-dir tox devpi-client

VOLUME /src
WORKDIR /src

ENTRYPOINT ["tox"]
