#!/bin/bash

# Private key for access to Nectar
key="/home/mlake/.ssh/keys/mikes_nectar"

# Destination i.e. Nectar instance 
dest="ec2-user@115.146.85.135:/home/ec2-user/"

# Todays date
today=`date +%Y.%m.%d`

# Name of tarball to create
tarball="choice_release_$today.tar"

# List of files and directories to tarball
files="choice.py choice_common.py process_choices.py static views" 

# Tar em !
# Note we prefix the files/dirs with public_html_today.
tar --transform="s#^#public_html_$today/#" --show-stored-names -cvf $tarball $files

# Send to Nectar
scp -i $key choice_release_$today.tar $dest

echo "Now login to Nectar:"
echo "ssh -i $key ec2-user@115.146.85.135"
echo ""

