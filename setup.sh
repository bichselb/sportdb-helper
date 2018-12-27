#!/bin/bash

###########
# PURPOSE #
###########
# Setup the environment to run this script

#################
# PREREQUISITES #
#################
# Install firefox webdriver: https://selenium-python.readthedocs.io/installation.html#drivers

###############
# PREPARATION #
###############

# Any subsequent commands which fail will cause the shell script to exit immediately
set -e

ENVNAME=env

###########
# CLEANUP #
###########
if [ -d "$ENVNAME" ]; then
	echo "$ENVNAME already exists"
	read -p "Remove $ENVNAME and start from scratch? [y/N] " -n 1 -r
	echo "" # move to new line
	if [[ $REPLY =~ ^[Yy]$ ]]; then
		echo "Removing ..."
		rm -r $ENVNAME
	else
		echo "Aborting..."
		exit
	fi
fi

###############
# ENVIRONMENT #
###############
python3 -m venv $ENVNAME

###########
# INSTALL #
###########

# activate environment
source $ENVNAME/bin/activate

pip3 install selenium
pip3 install pandas
pip3 install xlrd