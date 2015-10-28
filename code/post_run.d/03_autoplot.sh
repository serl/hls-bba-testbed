#!/bin/bash

cd /vagrant && python pylibs/autoplot.py --export=png "$RUN_PATH"

exit 0
