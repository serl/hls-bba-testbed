#!/bin/bash

schedule_file=$1
vagrant ssh server --command '/vagrant/code/master_scheduler.sh' < $schedule_file

