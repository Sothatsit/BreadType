What's your Bread Type?
-----------------------

What's your Bread Type is a quiz platform for creating heuristic based quizzes.

A user's answers to a quiz are scored for each category setup in the quiz,
and then the highest scoring category is considered to be the category they belong to.

In this site we use this as a fun method of grouping people into silly categories,
such as the question "What type of bread best fits you?". However, heuristic based quizzes
are also used for serious quizzes that group people based on psychological factors, such as
the famous Myers Briggs personality test. Heuristic based quizzes can also be a fun way
to structure surveys to make them more appealing for users.

To get the project running, check out the Quick Start section related to your operating system.

<br/>

Mac and Linux Quick Start
-----------
This section will help you to quickly get the server started for production or development
on a Mac or Linux environment.

1. You will first need to install Anaconda, a Python environment manager.
   Anaconda (conda) will be used to load all the dependencies for running the server,
   as defined in the `environment.yml` file.

2. The setup script should then be called so that it can create the Anaconda environment for you,
   ```./setup.sh```

3. Once the setup script has successfully run, you can now run the server using:
   
   a) `./run.sh dev` to run in development mode.
   
   b) `./run.sh prod` to run in production mode.

4. The server should now be running at http://localhost:5000
   
   Note, if running in `dev` mode, the sever will automatically detect changes to the server code and reload for you.

5. The default database has an example user that can be logged into using the credentials:
   
   Email: "example_user@example.com", Password: "example"
   
   However, feel free to create your own user through the Sign Up page.

<br/>

Windows Quick Start
-------------------

Sam pls?

Scripts
--------

**./setup.sh** - Creates and updates the Anaconda environment used to run the server.

**./run.sh dev** - Runs the server in development mode.

**./run.sh prod** - Runs the server in production mode.

**./test.sh** - Runs the tests for the server.

**./run.sh list-users** - Lists all of the registered users.

**./run.sh set-role \<email\> \<role\>** - Sets the role for the given user.<br/>
Roles are used to restrict functionality for just users with the correct role.

**./run.sh clear-role \<email\>** - Clears the role of the given user.

**./run.sh get-role \<email\>** - Prints the role of the user with the given email.


<br/>

Structure of this Project
-------------------------

### Config Files

**/config.yml** - Stores configuration for the server, such as the Flask secret key.

**/environment.yml** - The Anaconda environment specification.

**/.gitignore** - Lists all files that should be excluded from git.
<br/><br/>


### Script Files

**/setup.sh** - The script that creates the Anaconda environment to run the server.

**/run.sh** - The script that manages running and interacting with the web server.

**/test.sh** - The script that runs the tests of the server code.
<br/><br/>


### Website Files

**/client/** - The HTML pages, stylesheets, javascript, as well as other resources that are sent to the client.

**/client/static/** - The resources that are sent without modification to the client.

**/client/static/res/** - Holds all non-stylesheet and non-javascript files, such as images.

**/client/templates/** - The HTML templates that are modified before being sent to the client.

**/server/** - The Flask server code that controls the back-end of the server.

**/server/tests/** - Testing scripts for the server code.
<br/><br/>


### Generated Files

**/env/** - The Anaconda environment that contains the dependencies needed to run the server.

**/db.sqlite** - The SQLite database that stores the users and quizzes of the website.
<br/><br/>


### Unit Testing 

**/server/tests/test_user_quiz** - Testing scripts to ensure that users can register, login, create, and take a test.
!!! Note that for this test, chromedriver, geckodriver, and IEdriver must be in path for full functionality. If they are not, it will ignore them.

<br/>

Credits
-------
This project was created by **Sam Joyner**, **Maddy Sommer**, and **Paddy Lamont**.
