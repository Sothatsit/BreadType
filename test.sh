#! /bin/bash

#
# A script that activates the conda environment
# and runs the website tests.
#



# Set the working directory to the directory containing this script.
cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )" || exit

# Activate the testing environment.
source ./run.sh pre-run

# Run the tests
python -m server.tests.test_user_quiz
