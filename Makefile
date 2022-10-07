#==========================================
#    Makefile: makefile for sl 5.1
#	Copyright 1993, 1998, 2014
#                 Toyoda Masashi
#		  (mtoyoda@acm.org)
#	Last Modified: 2014/03/31
#==========================================

.DEFAULT_GOAL := build

# Packaging variables
SL_VERSION = 5.1
DEB_ARCH = amd64
DEB_FILENAME = sl_$(SL_VERSION)-1_$(DEB_ARCH).deb

# Autotools compat
PREFIX = /usr
BINDIR = $(PREFIX)/bin
DESTDIR =

# Programs
INSTALL = install
FAKEROOT = fakeroot

DOCKER_IMAGE = sl-builder:latest

CC=gcc
CFLAGS=-O -Wall

all: sl
.PHONY: all

build: sl
.PHONY: build

# Create a docker image that can build our program and deb
docker-build:
	docker build -t $(DOCKER_IMAGE) .
.PHONY: docker-build

# Build a deb in our current directory using our docker image
docker-build-deb: docker-build
	docker run --rm \
		-v "$$PWD:/opt/src/sl-$(SL_VERSION)" \
		--workdir "/opt/src/sl-$(SL_VERSION)" \
		--user "$$(id -u):$$(id -g)" \
		$(DOCKER_IMAGE) \
		make deb
.PHONY: docker-build-deb

# Install our deb into a docker image and run it
docker-build-test: docker-build
	docker run --rm \
		-v "$$PWD:/opt/src/sl-$(SL_VERSION)" \
		--workdir "/opt/src/sl-$(SL_VERSION)" \
		--tty \
		$(DOCKER_IMAGE) \
		make root-test
.PHONY: docker-build-test

sl: sl.c sl.h
	$(CC) $(CFLAGS) -o sl sl.c -lncurses

# Install sl into our $PREFIX/bin so it can be invoked in $PATH
install:
	rm -f -- "$(DESTDIR)$(BINDIR)/sl"
	$(INSTALL) -s -m 0755 sl -D "$(DESTDIR)$(BINDIR)/sl"
.PHONY: install

clean:
	rm -f sl *.deb
	dh_clean
.PHONY: clean

# Build our deb file for sl
$(DEB_FILENAME):
	dh build
	$(FAKEROOT) dh binary

# Make `make deb` generate our deb
deb: $(DEB_FILENAME)
.PHONY: deb

# Run a test installing this program (invoked via docker-build-test)
root-test:
	# check if running as root
	test "$$(id -u)" -eq 0
	dpkg -i "$(DEB_FILENAME)"
	# Ensure docker is running with a pseudo tty (-t/--tty)
	test -t 1
	sl
.PHONY: root-test

distclean: clean
.PHONY: distclean
