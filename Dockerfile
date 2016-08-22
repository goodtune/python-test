FROM python:3-slim
MAINTAINER Gary Reynolds <gary@touch.asn.au>

RUN pip install tox
RUN pip install devpi-client

VOLUME /src
WORKDIR /src

ENTRYPOINT ["tox"]
