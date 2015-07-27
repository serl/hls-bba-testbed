#!/bin/bash

cd "$(dirname $0)"

git pull && git submodule update --init

read -p "Recompile VLC? (a VM will start, AVOID BOOTING MULTIPLE VMs IN PARALLEL. Do it in sequence!) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
	vagrant up client0 && vagrant ssh client0 -c 'bash /vagrant/scripts/compile_vlc.sh update'
fi

