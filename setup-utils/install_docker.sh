#!/bin/bash

#Uninstall old versions
apt-get remove docker docker-ce docker-engine docker-compose -y

#Set up docker repository
#Install packages to allow apt to use a repository over HTTPS
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common \
    git \
    htop

#Add Docker’s official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -

#Set up the stable repository
add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

#Install Docker
apt-get update

apt-get install -y docker-ce

#Create the docker group
groupadd -f docker

#Add user to the docker group
usermod -aG docker ${1:-$USER}

#Install docker-compose
curl -L https://github.com/docker/compose/releases/download/1.13.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

echo 'Done'
