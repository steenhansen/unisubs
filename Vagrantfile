# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  config.vm.host_name = "unisubs"
  config.vm.box = "lucid64"
  config.vm.box_url = "http://files.vagrantup.com/lucid64.box"
  config.vm.network :hostonly, "10.10.10.42"
  config.vm.customize ["modifyvm", :id, "--memory", 1024]
  config.vm.forward_port 80, 8000
  config.vm.forward_port 8983, 8983
  config.vm.forward_port 9000, 9000
  config.vm.share_folder "puppet", "/tmp/puppet", "./puppet"
  config.vm.share_folder "unisubs", "/opt/apps/vagrant/unisubs", "."
  config.vm.customize ["setextradata", :id, "VBoxInternal2/SharedFoldersEnableSymlinksCreate/unisubs", "1"]
  config.vm.provision :shell do |shell|
    shell.path = "vagrant.sh"
    # the following will allow a custom branch of amara-puppet ; whatever the value of the
    # environment variable PUPPET_BRANCH is, the vagrant.sh script will attempt to checkout
    # that branch ; i.e. PUPPET_BRANCH=dev vagrant provision
    if (ENV['PUPPET_BRANCH'])
      shell.args = "%{branch}" % { :branch => ENV['PUPPET_BRANCH']}
    end
  end
end
