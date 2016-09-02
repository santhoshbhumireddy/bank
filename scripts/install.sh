#!/usr/bin/env bash

## Install python packages
sudo apt-get update
sudo apt-get install mysql-server
sudo apt-get install -y python python-pip
sudo pip install -r scripts/requirements.txt --upgrade

# Install front-end packages
sudo apt-get install nodejs npm
sudo update-alternatives --install /usr/bin/node node /usr/bin/nodejs 10
sudo npm install -g bower grunt grunt-cli
#npm install
bower install


