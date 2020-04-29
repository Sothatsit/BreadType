What's your Bread Type?
-----------------------

What's your Bread Type is a quiz platform for creating heuristic based quizzes.

Users of the quiz are categorised based on their answer's
similarity to the answer weightings set for pre-defined groups.


Quick Start
-----------
This section will help you to quickly get the server started for production or development.

1. You will first need to install Anaconda, a Python environment manager.
   Anaconda (conda) will be used to load all the dependencies for running the server.

2. The setup script should then be called so that it can create the Anaconda environment for you,
   ```./setup.sh```

3. Once the setup script has successfully run, you can now run the server using:
   
   a) `./run.sh dev` to run in development mode.
   
   b) `./run.sh prod` to run in production mode.

4. The server should now be running at http://localhost:5000
   
   Note, if running in `dev` mode, the sever will automatically detect changes to the server code and reload for you.


Commands
--------

**./setup.sh** - Creates and updates the Anaconda environment used to run the server.

**./run.sh dev** - Runs the server in development mode.

**./run.sh prod** - Runs the server in production mode.

**./run.sh list-users** - Lists all of the registered users.

**./run.sh set-role \<email\> \<role\>** - Sets the role for the given user.<br/>
Roles are used to restrict functionality for just users with the correct role.

**./run.sh clear-role \<email\>** - Clears the role of the given user.

**./run.sh get-role \<email\>** - Prints the role of the user with the given email.


Structure of this Project
-------------------------

### Website Files

**/client/** - The HTML pages, stylesheets, javascript, as well as other resources that are sent to the client.

**/client/static/** - The resources that are sent without modification to the client.

**/client/static/res/** - Holds all non-stylesheet and non-javascript files, such as images.

**/client/templates/** - The HTML templates that are modified before being sent to the client.

**/server/** - The Flask server code that controls the back-end of the server.
<br/><br/>


### Scripts to Manage the Server

**/setup.sh** - The script that creates the Anaconda environment and the SQLite database.

**/run.sh** - The script that loads the Anaconda environment and runs the Flask server.
<br/><br/>


### Config Files

**/environment.yml** - The Anaconda environment specification.
<br/><br/>


### Generated Files

**/env/** - The Anaconda environment.

**/db.sqlite** - The SQLite database.


Credits
-------
This project was created by **Sam Joyner**, **Maddy Sommer**, and **Paddy Lamont**.
