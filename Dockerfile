FROM debian:11

RUN apt-get update \
    && apt-get install -yq debhelper libncurses-dev

RUN mkdir -p /opt/src
