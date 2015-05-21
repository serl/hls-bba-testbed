#!/usr/bin/env bash

apt-get -y build-dep vlc #we want the libraries, don't we?

ln -fs /vagrant/code/vlc/vlc /home/vagrant/vlc

cd /vagrant/code

if [ -e vlc/vlc ]; then
  exit 0
fi

if [ ! -d vlc ]; then
  echo "VLC source code not found!" >&2
  exit 1
fi
cd vlc

apt-get -y install git libtool build-essential pkg-config autoconf

git submodule init && git submodule update

./bootstrap
./configure --disable-chromecast

git describe --tags --long --match '?.*.*' --always > src/revision.txt

make -j2

