sudo apt-get update

# Install Python
sudo apt-get install -y \
    python3 \
    python3-pip \
    python-is-python3

# Install requirements
pushd /sumologic
make install
popd

# Install docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
apt-get install -y docker-ce docker-ce-cli containerd.io
usermod -aG docker vagrant

# start receiver-mock
sudo docker create -p 3000:3000 --name receiver-mock --restart=always sumologic/kubernetes-tools receiver-mock --print-metrics
sudo docker start receiver-mock

# Install collectd
sudo apt-get install -y \
    collectd

# Configure collectd
LIBPYTHON_PATH="$(find / -path '/usr/lib/python*' -name 'libpython*.so' 2>/dev/null)"
echo "LD_PRELOAD=${LIBPYTHON_PATH}" | sudo tee -a /etc/default/collectd

sudo ln -s /sumologic/vagrant/sumo.conf /etc/collectd/collectd.conf.d/sumo.conf
sudo systemctl restart collectd
