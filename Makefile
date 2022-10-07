#==========================================
#    Makefile: makefile for sl 5.1
#	Copyright 1993, 1998, 2014
#                 Toyoda Masashi
#		  (mtoyoda@acm.org)
#	Last Modified: 2014/03/31
#==========================================

.DEFAULT_GOAL := build

SL_VERSION = 5.1
DEB_ARCH = amd64

INSTALL = install
PREFIX = /usr
BINDIR = $(PREFIX)/bin
DESTDIR =
FAKEROOT = fakeroot

DOCKER_IMAGE = sl-builder:latest

CC=gcc
CFLAGS=-O -Wall

all: sl
.PHONY: all

build: sl
.PHONY: build

docker-build:
	docker build -t $(DOCKER_IMAGE) .
.PHONY: docker-build

docker-build-deb: docker-build
	docker run --rm \
		-v "$$PWD:/opt/src/sl-$(SL_VERSION)" \
		--workdir "/opt/src/sl-$(SL_VERSION)" \
		--user "$$(id -u):$$(id -g)" \
		$(DOCKER_IMAGE) \
		make deb
.PHONY: docker-build-deb

sl: sl.c sl.h
	$(CC) $(CFLAGS) -o sl sl.c -lncurses

install:
	rm -f -- "$(DESTDIR)$(BINDIR)/sl"
	$(INSTALL) -s -m 0755 sl -D "$(DESTDIR)$(BINDIR)/sl"
.PHONY: install

clean:
	rm -f sl *.deb
	dh_clean
.PHONY: clean

sl_$(SL_VERSION)-1_$(DEB_ARCH).deb:
	dh build
	$(FAKEROOT) dh binary

deb: sl_$(SL_VERSION)-1_$(DEB_ARCH).deb
.PHONY: deb

distclean: clean
.PHONY: distclean
