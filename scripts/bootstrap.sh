#!/usr/bin/env bash
locale-gen en_US.UTF-8 fr_FR.UTF-8 it_IT.UTF-8

apt-get update
apt-get -y dist-upgrade
apt-get -y install htop iperf tcptrace traceroute

