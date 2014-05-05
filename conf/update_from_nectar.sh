#!/bin/bash

# This copies to here some of the configuration files that 
# we need at Nectar so we have a local backup of them. 

# Mikes private key for Nectar instance.
key='/home/mlake/.ssh/keys/uts-choice.pem'

# Login details for Nectar instance. 
src='ec2-user@130.56.248.113'

# Get nginx configuration files from /etc
# Note: we don't get everything from under /etc/nginx/ as many of the files
# there are just example files for other web applications. 
scp -i $key $src:/etc/nginx/nginx.conf nginx/
scp -i $key -r $src:/etc/nginx/conf.d nginx/

# Get uwsgi configuration files from /etc
scp -i $key $src:/etc/uwsgi.ini uwsgi/
scp -i $key -r $src:/etc/uwsgi.d uwsgi/

