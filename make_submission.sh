#! /bin/bash

# The folder to create the submission in.
DEST=submission

# Remove the last generated submission.
rm -rf "${DEST}"
rm -f "${DEST}.zip"

# Create the new submission directory.
mkdir "${DEST}"

# Copy all of the required resources to the submission.
cp -rf ./migrations ".//${DEST}/"
cp -rf ./server ".//${DEST}/"
cp -rf ./client ".//${DEST}/"
cp -f ./db.sqlite ".//${DEST}/"
cp -f ./config.yml ".//${DEST}/"
cp -f ./environment.yml ".//${DEST}/"
cp -f ./requirements.txt ".//${DEST}/"
cp -f ./README.md ".//${DEST}/"
find ./ -not \( -path ".//${DEST}" -prune \) -type f -name '*.sh'  -exec rsync -R '{}' "${DEST}" ";"
find ./ -not \( -path ".//${DEST}" -prune \) -type f -name '*.bat'  -exec rsync -R '{}' "${DEST}" ";"

# Remove files that are not required or wanted in the submission.
find "./${DEST}" -name '.*'  -exec rm -rf {} \;
find "./${DEST}" -name '__pycache__'  -exec rm -rf {} \;

# Output the git log to git_log.txt in the submission directory.
git log > "./${DEST}/git_log.txt"

# Create the VirtualEnv requirements.txt file.
pip freeze > "./${DEST}/requirements.txt"

# Zip the final submission directory.
zip -vr "${DEST}.zip" "${DEST}"
