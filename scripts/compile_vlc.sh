#!/usr/bin/env bash

sudo apt-get -y build-dep vlc #we want the libraries, don't we?
sudo apt-get -y install libcurl4-gnutls-dev git libtool build-essential pkg-config autoconf

cd /vagrant/code

if [ "$1" == "update" ]; then
  cd vlc && make -j2
  exit $?
fi

if [ -e vlc/vlc ]; then
  exit 0
fi

if [ ! -d vlc ]; then
  echo "VLC source code not found!" >&2
  exit 1
fi
cd vlc

git submodule init && git submodule update

./bootstrap
./configure --disable-chromecast

git describe --tags --long --match '?.*.*' --always > src/revision.txt

make -j2

