#!/bin/bash

#install pip3
sudo apt install python3-pip

#install pipenv
pip3 install pipenv

#install depencences
cd ../server/
pipenv install

#run server.py
python3 server.py