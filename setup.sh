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

###############
# ENVIRONMENT #
###############
if [ -d "$ENVNAME" ]; then
	echo "$ENVNAME already exists"
else
	python3 -m venv $ENVNAME
fi


###########
# INSTALL #
###########

# activate environment
source $ENVNAME/bin/activate

pip3 install selenium
pip3 install pandas
pip3 install xlrd
