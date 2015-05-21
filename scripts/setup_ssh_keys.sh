#!/bin/bash
ssh-keygen -t rsa -f /vagrant/scripts/ssh/id_rsa -q -N ''
cp /vagrant/scripts/ssh/id_rsa* $HOME/.ssh
cat /vagrant/scripts/ssh/id_rsa.pub >> ~/.ssh/authorized_keys

