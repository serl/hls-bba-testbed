#!/bin/bash

if [ "$1" == "silent" ]; then
	silent="true"
	shift
fi

for rundir in "$@"; do
	if [[ $rundir =~ (.*)\.tar\.gz$ ]]; then
		rundir="${BASH_REMATCH[1]}"
	fi
	if [ "$silent" == "true" ]; then
		RUN_PATH="$rundir" /vagrant/code/run_dir.sh /vagrant/code/post_run.d >/dev/null
	else
		RUN_PATH="$rundir" /vagrant/code/run_dir.sh /vagrant/code/post_run.d
		echo
	fi
done

