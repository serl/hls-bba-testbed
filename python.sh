#!/bin/bash

echo -n "Connecting to server..."
vagrant ssh server -- -X "cd /vagrant; echo ' ok'; exec python -u $@"

