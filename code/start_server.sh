#!/bin/bash

echo $(date +%s.%N) BOOT >> /vagrant/log/http_server.log
node /vagrant/code/http_server/index.js >> /vagrant/log/http_server.log 2>&1 &
SERVER_PID=$!
sleep 3

#echo HTTP server PID: $SERVER_PID

