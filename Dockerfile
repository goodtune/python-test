FROM python:3
MAINTAINER Gary Reynolds <gary@touch.asn.au>

RUN curl -s https://bootstrap.pypa.io/get-pip.py | python2.7
RUN pip2.7 install --no-cache-dir tox devpi-client bumpversion click

RUN apt-get update && apt-get install -y \
  libpython2.7-dev \
  && rm -rf /var/lib/apt/lists/*

COPY run-tests.py /usr/local/bin/run-tests

VOLUME /src
WORKDIR /src

ENTRYPOINT ["run-tests"]
