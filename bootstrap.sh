#!/bin/sh

set -ex

rm -rf .Python bin lib include
virtualenv --python python .
bin/pip install setuptools==40.0.0
bin/pip install zc.buildout==2.13.1
./bin/buildout bootstrap