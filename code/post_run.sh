#!/bin/bash

for rundir in "$@"; do
	if [[ $rundir =~ (.*)\.tar\.gz$ ]]; then
		rundir="${BASH_REMATCH[1]}"
	fi
	RUN_PATH="$rundir" /vagrant/code/run_dir.sh /vagrant/code/post_run.d
	echo
done

