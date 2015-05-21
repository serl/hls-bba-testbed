#!/bin/bash

/vagrant/code/tc_helper.sh setup
/vagrant/code/tc_helper.sh watch_buffer_size >> /vagrant/log/router_buffer.log &

