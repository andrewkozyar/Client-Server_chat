#!/bin/bash

#install tkinter
sudo apt-get install python-tk

#install pip3
sudo apt install python3-pip

#install pipenv
pip3 install pipenv

#install depencences
cd ../client/
pipenv install

#run client.py
python3 client.py