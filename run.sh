#! /bin/bash

#
# A script that activates the conda environment
# and runs the flask web server.
#



# Set the working directory to the directory containing this script.
cd "${0%/*}" || exit
echo " "

# Check whether to run in production or development mode.
if [ "$1" == "prod" ] || [ "$1" == "production" ]; then
  DEV_MODE=0
elif [ "$1" == "dev" ] || [ "$1" == "development" ]; then
  DEV_MODE=1
else
  echo "Expected production or development mode to be specified."
  echo " "
  echo "Usage:"
  echo "  ./run.sh [prod|dev]"
  echo " "
  exit
fi



# Only activate the environment if it is not already activated, as it can be slow.
if ! [[ "$CONDA_DEFAULT_ENV" -ef "./env" ]]; then

  echo "==================================="
  echo "  Activating conda environment...  "
  echo "==================================="
  echo " "

  # Make sure conda environments are available in this script.
  eval "$(conda shell.bash hook)"

  # Activate the Anaconda environment so that python and flask are available.
  conda activate ./env || exit

  echo " "
  echo "Done!"
  echo " "
fi



echo "====================="
echo "  Starting Flask...  "
echo "====================="
echo " "

# Set the python file that flask should run.
export FLASK_APP=./server/server.py

# Indicate to flask whether to run in development mode.
if [ $DEV_MODE == 1 ]; then
  export FLASK_ENV=development
fi

# Run the webserver.
flask run
