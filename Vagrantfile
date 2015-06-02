# -*- mode: ruby -*-
# vi: set ft=ruby :

clients = 1

Vagrant.configure(2) do |config|
  base_ip = '192.168.199'
  server_ip = 5
  clients_ip = 10

  config.vm.box = "ubuntu/trusty32"
  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--ioapic", "on"]
  end
  config.vm.provision :shell, path: "scripts/bootstrap.sh"
  config.vm.provision :shell, path: "scripts/install_nodejs.sh"
  config.vm.provision :shell, path: "scripts/compile_vlc.sh"
  config.vm.provision :shell, inline: "ntpdate pool.ntp.org", run: "always"
  config.vm.provision :shell, inline: "ethtool -K eth1 tx off gso off sg off gro off", run: "always"

  config.vm.define "server" do |server|
    server.vm.hostname = "server"
    server.vm.network "private_network", ip: "#{base_ip}.#{server_ip}", virtualbox__intnet: true
    server.vm.provider "virtualbox" do |vb|
      vb.memory = 1024
      vb.cpus = 2
    end
    
    server.vm.provision "shell", inline: "sed -i '/client[0-9]\\+/d' /etc/hosts", run: "always"
    (0...clients).each do |i|
      hostname = "client#{i}"
      ip = "#{base_ip}.#{clients_ip+i}"
      server.vm.provision :shell, inline: "echo #{ip} #{hostname} >> /etc/hosts", run: "always"
    end
    
    server.vm.provision :shell, path: "scripts/setup_ssh_keys.sh", privileged: false
    server.vm.provision :shell, inline: "/vagrant/code/start_server.sh", run: "always", privileged: false
  end

  (0...clients).each do |i|
    hostname = "client#{i}"
    ip = "#{base_ip}.#{clients_ip+i}"
    config.vm.define hostname do |client|
      client.vm.hostname = hostname
      client.vm.network "private_network", ip: ip, virtualbox__intnet: true
      client.vm.provision :shell, inline: "echo #{base_ip}.#{server_ip} server >> /etc/hosts"
      client.vm.provision :shell, inline: "cat /vagrant/scripts/ssh/id_rsa.pub >> ~/.ssh/authorized_keys", privileged: false
    end
  end

end

