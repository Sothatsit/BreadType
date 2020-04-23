#! /bin/bash

#
# A script that creates the anaconda environment for running flask.
#



# Set the working directory to the directory containing this script.
cd "${0%/*}" || exit



# Make sure the Anaconda environment is created.
if [ -d "./env" ]; then
  echo " "
  echo "The Anaconda environment ./env already exists."
  echo "If a fresh environment is needed, please delete ./env and run this command again."
  echo " "
  exit
else
  echo " "
  echo "===================================="
  echo "  Creating Anaconda Environment...  "
  echo "===================================="
  echo " "

  # Creates a conda environment based on environment.yml.
  conda env create -p ./env -f environment.yml

  echo " "
  echo "Created the Anaconda Environment $PWD/env"
  echo " "
fi
