#!/bin/bash

# Old SysV init methos
#sudo service httpd stop
#sudo service nginx start

# New dystewmd method. 
sudo systemctl stop httpd.service
sudo systemctl start nginx.service

./choice.py


