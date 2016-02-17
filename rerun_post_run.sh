#!/bin/bash

if [ -z "$1" -o ! -e "$1" ]; then
	echo "Usage: $0 <rundir|run.tar.gz> [rundir|run.tar.gz...]"
	exit 1
fi

vagrant up server

if [ $# -eq 1 ]; then
	vagrant ssh server --command "/vagrant/code/post_run.sh /vagrant/$1"
	exit $?
fi

for rundir in "$@"; do echo /vagrant/$rundir; done |
vagrant ssh server -- bash -c "'
	parallel --gnu -j2 --eta /vagrant/code/post_run.sh > /vagrant/rerun_post.log
	echo -e "\\\\n\$? jobs failed."
'"
