# -*- mode: ruby -*-
# vi: set ft=ruby :

server_memory = 2048
server_cpus = 2
server_ip = '192.168.100.10'

routers_memory = 1024
routers_cpus = 2
routers = {
  "bandwidth" => ['192.168.100.50', '192.168.150.45'],
  "delay" => ['192.168.150.55', '192.168.200.5']
}

clients = 3
clients_memory = 1024
clients_cpus = 2
clients_ip = '192.168.200'

network_prefix = Dir.pwd[1..-1].gsub('/', '-')

Vagrant.configure(2) do |config|
  net_id = 1
  config.vm.box = "ubuntu/trusty32"
  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--ioapic", "on"]
  end
  config.vm.provision :shell, path: "scripts/bootstrap.sh"
  config.vm.provision :shell, inline: "ntpdate pool.ntp.org", run: "always"
  (0..2).each do |i|
    config.vm.provision :shell, inline: "ethtool -K eth#{i} tx off gso off sg off gro off || echo no eth#{i} here!", run: "always"
  end

  server_net_id = net_id
  config.vm.define "server" do |server|
    server.vm.hostname = "server"
    server.vm.network "private_network", ip: server_ip, virtualbox__intnet: "#{network_prefix}-hls-bba-#{server_net_id}"
    server.vm.provider "virtualbox" do |vb|
      vb.memory = server_memory
      vb.cpus = server_cpus
    end
    
    server.vm.provision "shell", inline: "sed -i '/client[0-9]\\+/d' /etc/hosts", run: "always"
    (0...clients).each do |i|
      hostname = "client#{i}"
      ip = "#{clients_ip}.#{10+i}"
      server.vm.provision :shell, inline: "echo #{ip} #{hostname} >> /etc/hosts", run: "always"
    end
    gateway = routers.values.first.first #ehm ok, that's the first ip of the first router
    routers.each do |hostname, ip_addresses|
      server.vm.provision :shell, inline: "echo #{ip_addresses.first} #{hostname} >> /etc/hosts"
      cidr = ip_addresses.last.gsub(/\.\d+$/, '.0/24') #last octet must be 0
      server.vm.provision :shell, inline: "ip route add #{cidr} via #{gateway} proto static", run: "always"
    end

    server.vm.provision :shell, path: "scripts/setup_ssh_keys.sh", privileged: false
    server.vm.provision :shell, path: "scripts/bootstrap_server.sh"
    server.vm.provision :shell, inline: "/vagrant/code/start_server.sh", run: "always", privileged: false
  end

  routers.each do |hostname, ip_addresses|
    router_net_id = net_id
    config.vm.define hostname do |router|
      router.vm.provider "virtualbox" do |vb|
        vb.memory = routers_memory
        vb.cpus = routers_cpus
      end
      router.vm.hostname = hostname
      ip_addresses.each_with_index do |ip, ip_idx|
        router.vm.network "private_network", ip: ip, virtualbox__intnet: "#{network_prefix}-hls-bba-#{router_net_id+ip_idx}"
      end
      #second interface of next routers and first interface of previous ones
      ips_net_idx = 0
      ips_gw_idx = 1
      routers.each do |h, ips|
        if h == hostname
          ips_net_idx = 1
          ips_gw_idx = 0
          next
        end
        cidr = ips[ips_net_idx].gsub(/\.\d+$/, '.0/24') #last octet must be 0
        gateway = ips[ips_gw_idx]
        #puts "on #{hostname} => ip route add #{cidr} via #{gateway} proto static"
        router.vm.provision :shell, inline: "ip route add #{cidr} via #{gateway} proto static", run: "always"
      end
      router.vm.provision :shell, inline: "sysctl -w net.ipv4.ip_forward=1", run: "always"
      router.vm.provision :shell, inline: "echo #{server_ip} server >> /etc/hosts"
      router.vm.provision :shell, inline: "cat /vagrant/scripts/ssh/id_rsa.pub >> ~/.ssh/authorized_keys", privileged: false
      router.vm.provision :shell, path: "scripts/disable_authlog.sh" #otherwise it will fill because of sudo in tc_helper (to monitor the buffer size)
    end
    net_id += 1
  end

  (0...clients).each do |i|
    hostname = "client#{i}"
    ip = "#{clients_ip}.#{10+i}"
    client_net_id = net_id
    config.vm.define hostname, autostart: false do |client|
      client.vm.provider "virtualbox" do |vb|
        vb.memory = clients_memory
        vb.cpus = clients_cpus
      end
      client.vm.hostname = hostname
      client.vm.network "private_network", ip: ip, virtualbox__intnet: "#{network_prefix}-hls-bba-#{client_net_id}"

      gateway = routers.values.last.last #and that's the last ip of the last router
      routers.each do |hostname, ip_addresses|
        client.vm.provision :shell, inline: "echo #{ip_addresses.last} #{hostname} >> /etc/hosts"
        cidr = ip_addresses.first.gsub(/\.\d+$/, '.0/24') #last octet must be 0
        client.vm.provision :shell, inline: "ip route add #{cidr} via #{gateway} proto static", run: "always"
      end

      client.vm.provision :shell, inline: "echo #{server_ip} server >> /etc/hosts"
      client.vm.provision :shell, inline: "cat /vagrant/scripts/ssh/id_rsa.pub >> ~/.ssh/authorized_keys", privileged: false
      client.vm.provision :shell, path: "scripts/compile_vlc.sh"
    end
  end

end

