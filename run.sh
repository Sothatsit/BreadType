#! /bin/bash

#
# A script that activates the conda environment
# and runs the flask web server.
#



# Set the working directory to the directory containing this script.
cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )" || exit

# Prints to stderr.
echoerr() { echo "$@" 1>&2; }



# Check whether to run in production or development mode.
if [ "$1" == "prod" ] || [ "$1" == "production" ]; then
  # Run Flask in production mode.
  RUN_MODE="prod"
  FLASK_ARGUMENTS=("${@:2}")

elif [ "$1" == "dev" ] || [ "$1" == "development" ]; then
  # Run Flask in development mode.
  RUN_MODE="dev"
  FLASK_ARGUMENTS=("${@:2}")

elif [ "$1" == "pre-run" ]; then
  # Setup the environment to run Flask, but don't actually run it.
  # This can be useful to run non-website scripts that require
  # the same environment using "source ./run.sh pre-run".
  RUN_MODE="pre-run"

  if [ "$2" != "" ]; then
    echoerr
    echoerr "Unrecognised additional arguments to pre-run: ${*:2}"
    echoerr
    exit
  fi

elif [ "$1" == "db" ] || [ "$1" == "list-users" ] || [ "$1" == "set-role" ]  || [ "$1" == "clear-role" ]|| [ "$1" == "get-role" ]; then
  # Run flask in production mode, and run a Flask sub-command.
  RUN_MODE="sub-command"
  FLASK_ARGUMENTS=("${@:1}")

else
  echoerr
  if [ "$1" == "" ]; then
    echoerr "Expected the run-mode to be specified."
    echoerr
  else
    echoerr "Unrecognised run-mode \"$1\"."
    echoerr
  fi
  echoerr "To run in production mode:"
  echoerr "  ./run.sh prod [arguments]"
  echoerr
  echoerr "To run in development mode:"
  echoerr "  ./run.sh dev [arguments]"
  echoerr
  echoerr "To pre-activate the conda environment:"
  echoerr "  source ./run.sh pre-run"
  echoerr
  exit
fi


# If there are no additional arguments to the command, call Flask run.
if [ ${#FLASK_ARGUMENTS[@]} -eq 0 ]; then
  FLASK_ARGUMENTS=("run")
fi


# Just a newline.
echo

# Only activate the environment if it is not already activated, as it can be slow.
if ! [[ "$CONDA_DEFAULT_ENV" -ef "./env" ]]; then

  # Make sure the environment has been created.
  if [ ! -d "./env" ]; then
    echo "Could not find the Anaconda environment to run the server."
    echo
    echo "Please create it using the following command:"
    echo "  ./setup.sh"
    echo
    exit
  fi

  # The environment directory exists, so try to activate it.
  echo "======================================"
  echo "  Activating Anaconda Environment...  "
  echo "======================================"
  echo

  # Make sure conda environments are available in this script.
  eval "$(conda shell.bash hook)"

  # Activate the Anaconda environment so that python and flask are available.
  conda activate ./env || exit

  echo
  echo "Activated the Anaconda Environment."
  echo
fi



# Set the python file that flask should run.
export FLASK_APP=./server

# Indicate to flask whether to run in development mode.
if [ "$RUN_MODE" == "dev" ]; then
  export FLASK_ENV=development
else
  export FLASK_ENV=""
fi



# If we're running in pre-run mode, we don't want to actually start the Flask server.
# (Note, we can't just do an early exit because when we call this using pre-run, we call it using source.)
if [ "$RUN_MODE" != "pre-run" ]; then
  # Run the webserver.
  flask "${FLASK_ARGUMENTS[@]}"
  echo
fi
