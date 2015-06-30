#!/bin/bash

# This script will tarball just specific files and directories listed below 
# and scp the tarball to the remote Nectar instance.  
# Versions: 
# 2014.01.07: first version
# 2014.04.22: changed ip address to a production server; 
#             changed $dest to separate login and directory vars.

# Private key for access to Nectar
key="/home/mlake/.ssh/keys/uts-choice.pem"

# Destination i.e. Nectar instance 
#dest="ec2-user@115.146.85.135:/home/ec2-user/public_html"
dest_login="ec2-user@130.56.248.113"
dest_dir="/home/ec2-user/public_html"

# Todays date
today=`date +%Y.%m.%d`

# Name of tarball to create
tarball="choice_release_$today.tar"

# List of files and directories to tarball
files="choice.py choice_common.py process_choices.py static_choice views" 

# Tar em !
# Note we prefix the files/dirs with choice_$today.
tar --transform="s#^#choice_$today/#" --show-stored-names -cvf $tarball $files

# Send to Nectar
echo ""
echo "Copying tarball to $dest ..."
scp -i $key choice_release_$today.tar ${dest_login}:${dest_dir}

echo ""
echo "Now login to Nectar using this:"
echo "ssh -i $key $dest_login"
echo ""

