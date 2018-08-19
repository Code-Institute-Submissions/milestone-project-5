# Recipe Wiki
## Overview
![Screenshot](https://i.snag.gy/Q1KT79.jpg)

### What it the website for? 
Sharing and saving recipes 

### What does it do?
Users upload recipes to share. Users can also view, save, and rate the recipes of others.  They can search the database of recipes using filters such as categories (e.g. Mexican, vegetarian) or time required to cook. A data visualization page presents users with interactive charts, displaying counts of recipe categories, difficulties, and review scores. Users can set up an account, enabling them to submit, save, and rate recipes. 

### How does it work? 
Recipes are stored in a MySQL database. Users upload recipes using a HTML POST form. Python and PyMySQL are used to store their submissions in the SQL tables.  These tables hold all the recipe data, except for images, which are stored in the project repository. Flask is used to supplement Python and render HTML templates. Flask Login Is used to manage accounts, while sha256 is used to encrypt user passwords.  JavaScript (supplemented by JQuery) enhances the feel of the website by allowing users to freely add and remove form rows.  JavaScript also interacts with MySQL (via Flask, Python, and PyMySQL) to enable autocompletion of form values based on existing table data. Similarly, Flask imports SQL data to the data visualization page, which then is rendered as charts using D3 and DC.

## Features

### Existing Features
-	Users can add recipe details to the database, including images, difficulty, preparation and cooking time, ingredients, and instructions.
-	Forms autocomplete category and ingredient names based on existing data
-	Users can quickly edit their previously submitted recipes
-	Users can create their own account. This is required for certain features 
-	Database encrypts passwords using sha256
-	Users can save their favourite recipes and rate other recipes 
-	A user page for each user that displays their submitted and favorited recipes
-	Ability for users to search the database using a number of filters. Search results are sorted by average review score
-	A visualize data page with interactive charts displaying recipe data

### Features Left to Implement
-	A more expensive ClearDB plan that will increase the hourly query limit. The current query limit may cause the live version of the app to crash.

## Database Schema

### Developing the Database Schema
The database schema was initially planned out using the Entity Relationship Diagram(ERD) below:
![ERD](https://i.snag.gy/xephD3.jpg)

The diagram was created before the decision to commit to using an SQL database, rather than a NoSQL database. However, the diagram confirmed that an SQL schema was feasible.  While the SQL design limited the amount that the schema could change throughout development, the final database schema still had some deviations from the initial outline. Most notably, the ‘Allegories/Suitable For’ table was removed, as this data could instead be included in the ‘Categories’ table. 

### Current Database Schema
The current database schema is found in the [database_schema](https://github.com/Paddywc/milestone-project-4/tree/testing/database_schema) directory. 
Note that there are currently two MySQL databases. The original/testing Cloud9 database, and the ClearDB database used in the live Heroku app. However, as the ClearDB database was initially created as a clone of the Cloud9 database, they have identical schemas. 

## Tech Used

### Some of the tech used includes:
-	**MySQL**  
    *	To store the recipe data
    *	Users read table rows that meet certain conditions when they search recipes and apply filters 
    *	To create and read user ids, usernames, and (encrypted) passwords. This enables Flask login/user functionality
-	**Python3** and  [**PyMySQL**](https://pymysql.readthedocs.io/en/latest/)
    *	Together retrieve the user’s form submission and upload this data to the SQL table(s)
    *	For validating login information by checking user data against existing values in the Users table
    *	To quickly populate SQL tables with data during testing
    *	For aggregating database values. E.g. average recipe review score
    *	Majority of application was built using Python3 and Flask
-	[**Flask**](http://flask.pocoo.org/)
    *	For binding functions to URLs using routing 
    *	To render HTML templates and include Python programming within these templates. This included inserting python variables into JavaScript scripts 
    *	To trigger functions on GET or POST requests
    *	Flask Login used for user profiles and login functionality 
- [**Materialize**](https://materializecss.com/)
    *	Grid system used for page layout
    *	Used to style website, including forms, navbar and sidebar
    *	Autocomplete functionality used in forms 
-	**JavaScript** and  [**jQuery**](https://jquery.com/)
    *	Used to enable Materialize functionality, including select forms, sidenavs, character counter, and tabs 
    *	For adding and removing form rows
    *	D3 and DC code for visualizing data written using JavaScript
-	[**DC**](https://dc-js.github.io/dc.js/) and  [**D3**](https://d3js.org/)
    *	For creating and rendering the interactive charts on the data visualization page 
- [**Heroku**](https://paddywc-recipe-wiki.herokuapp.com/)
    *	The live version of the web app is hosted on Heroku
- [**ClearDB**](https://elements.heroku.com/addons/cleardb)
    *	A Heroku add on used to enable MySQL on Heroku
- [**Amazon S3**](https://aws.amazon.com/s3/)
    *	Used to host user-uploaded recipe images

## Contributing 

### Getting the project running locally
1.	Clone or download this GitHub repository using the ‘Clone or Download’ button found on [the main page](https://github.com/Paddywc/milestone-project-4) . Note that **you must use the default branch (‘testing’)**.  All pull requests to other branches will be ignored. 
2.	Open the project directory using an integrated development environment (IDE) software application, such as Eclipse or Visual Code Studio
3.	Ensure you have Python3 installed on your computer. Install it if you do not. How you should do this depends on which operating system you are using.  See the [Python Documentation](https://docs.python.org/3.4/using/index.html) for instructions 
4.	Next, you’ll need to install Flask. Detailed documentation can be found on the [Flask Website](http://flask.pocoo.org/docs/1.0/installation/#installation). The simplest way to install Flask is to:
    *	Create a project folder 
    *	Create a python3 venv folder within this project folder
    *	Activate the environment using either _. venv/bin/activate_ or _venv\Scripts\activate_
    *	Within this activated environment, install Flask by using the following command : _pip install Flask_. Note that you will need to have pip installed.  If you do not, install pip by following [these instructions]( https://pip.pypa.io/en/stable/installing/)
5.  Ensure that you are running the MySQL database.  The username and password for this database are found at the top of the [sql_functions.py file](https://github.com/Paddywc/milestone-project-4/blob/testing/sql_functions.py). If you encounter any problems, follow [these instructions](https://stackoverflow.com/questions/6885164/pymysql-cant-connect-to-mysql-on-localhost) for troubleshooting. 
6.	Run the code in run.py
7.	Well done! The project is now up and running. Click the link in your terminal to view the web app. If you are missing any dependencies, check the requirments.txt file.

### Using the Testing Database
The default branch in the GitHub repository is the [testing branch](https://github.com/Paddywc/milestone-project-4). As detailed in the [deployment section of this readme](https://github.com/Paddywc/milestone-project-4#deployment), the live version of the app instead uses the [heroku branch](https://github.com/Paddywc/milestone-project-4/tree/heroku). The heroku branch uses a different database.  The password to this database and the app secret key are both hidden. When contributing to this site, you must use the testing branch.  Neither the secret key nor the testing database password are hidden in this branch. However, you will not be able to save photos to the S3 bucket, as the password is hidden as an environ value. This is due to pricing limitations. 

## Testing

### Unit Tests
Unit tests are found in [tests.py](https://github.com/Paddywc/milestone-project-4/blob/testing/tests.py). 

### Important Note for Testing
The tests are designed to work with the current version of the testing database. If you change these values, or use a different database, some of the tests may fail. It may also cause unintended changes to your database. As such, it is highly recommended that you run these tests using the testing database. 

## Deployment
The app is hosted on [Heroku](https://paddywc-recipe-wiki.herokuapp.com/). The code used is from the [heroku branch](https://github.com/Paddywc/milestone-project-4/tree/heroku) of the GitHub repository. The code is identical to the [default (testing) branch]( https://github.com/Paddywc/milestone-project-4/tree/testing), except for the following changes:
- The secret key is changed and hidden from the code. It is set as an environ value.
- The Database is changed to the ClearDB database. This is so that it works with Heroku. The password for this database is set as an environ value and hidden from the code. Note that while earlier commits in the heroku GitHub branch have a visible secret key and database password, both these values have since been changed.
-  Debug mode is set to False at the end of the app.py file

### ClearDB Query Limits
There is an hourly limit to the database queries that a user can make on the live Heroku app. This is a limitation of the current ClearDB plan. The $10 monthly plan allows for [18,000 queries per hour](http://w2.cleardb.net/faqs/). However, exceeding this limit may cause the app to crash. These will normally be TypeErrors, caused by a NoneType object. It will work correctly again once the limit resets. 

## Credits

### Code
- The sources for all non-original code are displayed in comments above the relevant code
- Code from [Pretty Printed](https://www.youtube.com/watch?v=2dEM-s3mRLE#%20for%20uploading%20images), [Treehouse](https://teamtreehouse.com/community/how-usermixin-and-class-inheritance-work), and the [Flask-Login Documentation]( https://flask-login.readthedocs.io/en/latest/#how-it-works) were used  for creating account functions.  They are referenced above the code whenever used.  Any alterations from the source code is original work. Password removed from the UserMixin class because this information is stored in the Users table, and is therefore not required when initializing the object
- [PyCharm](https://www.jetbrains.com/pycharm/download/) software was used for separating out the python code into separate files. Therefore, much of the code for importing functions from python files within the project directory was generated using PyCharm. PyCharm was also used to identify dependencies that were installed, but never used. These dependencies were then removed from requirements.txt, and therefore PyCharm played a role in developing this file
- The redirect_url function was taken from the [Flask Documentation](http://flask.pocoo.org/docs/1.0/reqcontext/)
- The code for converting a string into a datatime.time object was taken from [Martijn Pieters on stackoverflow](https://stackoverflow.com/questions/14295673/convert-string-into-datetime-time-object)
- Code for sorting dictionaries in python is from [Mario F on stackoverflow]( https://stackoverflow.com/questions/72899/how-do-i-sort-a-list-of-dictionaries-by-values-of-the-dictionary-in-python)
- MySQL code for inserting values into a table if they do not already exist in that table is from [user5505982 on stackoverflow](https://stackoverflow.com/questions/3164505/mysql-insert-record-if-not-exists-in-table). Code was changed to reflect the data and tables of the application
- Much of the code used to upload images to S3 was taken from [zabana.me](http://zabana.me/notes/upload-files-amazon-s3-flask.html). The code was changed in the add_recipe_image_and_return_filename() function in app_recipe.py to allow for custom file names   
- Using SQL data to generate charts required replacing single quotation marks with double quotation marks before parsing. The line of code used to do so was taken from [RafH  on stackoverflow](https://stackoverflow.com/questions/16450250/javascript-replace-single-quote-with-double-quote)
- Code for creating  and rendering charts on data visualization page is from [DJ Martin on stackoverflow](https://stackoverflow.com/questions/21114336/how-to-add-axis-labels-for-row-chart-using-dc-js-or-d3-js), the [dc-js Github repository](https://github.com/dc-js/dc.js/blob/master/web/examples/row.html), [Kostya Marchenko on stackoverflow](https://stackoverflow.com/questions/17524627/is-there-a-way-to-tell-crossfilter-to-treat-elements-of-array-as-separate-record?noredirect=1&lq=1) and [cssndrx  on stackoverflow](https://stackoverflow.com/questions/13576906/d3-tick-marks-on-integers-only). The sources are referenced as comments above where the code is used. 
- Code for implementing Materialize styles and functions are from the [Materialize documentation](https://materializecss.com/)

### Additional Credits
- Some of the initial recipes and categories used to populate the database are from [BBC Recipes](https://www.bbcgoodfood.com/recipes)
- Star icons used to represent average user review scores are from [icons8]( https://icons8.com/icon/new-icons/all)
- The background of the homepage header is from  [galonamission.com](https://icons8.com/icon/new-icons/all) https://www.galonamission.com/creamy-white-chicken-chili/)

