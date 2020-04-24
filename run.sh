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
  # Run Flask in production mode.
  RUN_MODE="prod"
elif [ "$1" == "dev" ] || [ "$1" == "development" ]; then
  # Run Flask in development mode.
  RUN_MODE="dev"
elif [ "$1" == "pre-run" ]; then
  # Setup the environment to run Flask, but don't actually run it.
  RUN_MODE="pre-run"
else
  echo "Expected production or development mode to be specified."
  echo " "
  echo "To run in production mode:"
  echo "  ./run.sh prod"
  echo ""
  echo "To run in development mode:"
  echo "  ./run.sh dev"
  echo " "
  exit
fi



# Only activate the environment if it is not already activated, as it can be slow.
if ! [[ "$CONDA_DEFAULT_ENV" -ef "./env" ]]; then

  # Make sure the environment has been created.
  if [ ! -d "./env" ]; then
    echo "Could not find the Anaconda environment to run the server."
    echo " "
    echo "Please create it using the following command:"
    echo "  ./setup.sh"
    echo " "
    exit
  fi

  # The environment directory exists, so try to activate it.
  echo "======================================"
  echo "  Activating Anaconda Environment...  "
  echo "======================================"
  echo " "

  # Make sure conda environments are available in this script.
  eval "$(conda shell.bash hook)"

  # Activate the Anaconda environment so that python and flask are available.
  conda activate ./env || exit

  echo " "
  echo "Activated the Anaconda Environment."
  echo " "
fi


# If we're running in pre-run mode, we don't want to actually start the Flask server.
# (Note, we can't just do an early exit because when we call this using pre-run, we call it using source.)
if [ "$RUN_MODE" != "pre-run" ]; then
  echo "====================="
  echo "  Starting Flask...  "
  echo "====================="
  echo " "

  # Set the python file that flask should run.
  export FLASK_APP=./server

  # Indicate to flask whether to run in development mode.
  if [ "$RUN_MODE" == "dev" ]; then
    export FLASK_ENV=development
  fi

  # Run the webserver.
  flask run
fi
