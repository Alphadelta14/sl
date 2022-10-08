SL(1): Cure your bad habit of mistyping
=======================================

SL (Steam Locomotive) runs across your terminal when you type "sl" as
you meant to type "ls".
It's just a joke command, and not useful at all.

Copyright 1993,1998,2014 Toyoda Masashi (mtoyoda@acm.org)

## Install the Python Package

```
pip install .
```

## Build the Packages

### Locally

Install the dependencies:
```
sudo apt-get install -y debhelper dh-python python3-all python3-setuptools python3-pillow python3-wheel
```

Run the dh commands:
```
make deb
```

Run the wheel build:
```
make build-py-wheel
```

### Using Docker

```
make docker-build-deb
make docker-build-wheel
```

### Test It Out

```
make docker-build-test
```

## Usage

```
$ sl --help
usage: sl [-h] [-n NUMBER] [--term-colors] [--max-colors] [--grayscale] [--gif GIF]

optional arguments:
  -h, --help     show this help message and exit
  -n NUMBER      Select which train to use (default random)
  --term-colors  Use 8-color color palette
  --max-colors   Use 64-color color palette
  --grayscale    Use 64-color color palette
  --gif GIF      Path to gif to use for train
```
