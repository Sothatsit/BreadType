#! /bin/bash

#
# A script that creates the anaconda environment for running flask.
#



# Set the working directory to the directory containing this script.
cd "${0%/*}" || exit



echo " "
echo "===================================="
echo "  Creating Anaconda Environment...  "
echo "===================================="
echo " "

conda env create -p ./env -f environment.yml

echo " "
echo "Done!"
