FROM debian:11

RUN apt-get update \
    && apt-get install -yq debhelper libncurses-dev \
        dh-python python3-all python3-setuptools python3-pillow python3-wheel

RUN mkdir -p /opt/src
