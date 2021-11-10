# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure('2') do |config|
  config.vm.box = 'ubuntu/focal64'
  config.vm.box_check_update = false
  config.vm.host_name = 'sumologic-collectd-plugin'
  # Vbox 6.1.28+ restricts host-only adapters to 192.168.56.0/21
  # See: https://www.virtualbox.org/manual/ch06.html#network_hostonly
  config.vm.network :private_network, ip: "192.168.56.43"

  config.vm.provider 'virtualbox' do |vb|
    vb.gui = false
    vb.cpus = 8
    vb.memory = 16384
    vb.name = 'sumologic-collectd-plugin'
  end

  config.vm.provision 'shell', path: 'vagrant/provision.sh'

  config.vm.synced_folder ".", "/sumologic"
end
