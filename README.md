# Recipe Wiki

## Overview
![Screenshot]( https://i.snag.gy/F9CdIt.jpg)

### What it the website for? 
Sharing and saving recipes 

### What does it do?
Users upload recipes to share. Users can also view, save, and rate the recipes of others.  They can search the database of recipes using filters such as categories (e.g. Mexican, vegetarian)  or time required to cook. A data visualization page presents users with interactive charts, displaying counts of recipe categories, difficulties, and review scores. Users can set up an account, enabling them to submit, save, and rate recipes. 

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
-	None

## Database Schema:
### Developing the Database Schema
The database schema was initially planned out using the Entity Relationship Diagram(ERD) below:
![ERD]( https://i.snag.gy/xephD3.jpg)

The diagram was created before the decision to commit to using an SQL database, rather than a NoSQL database. However, the diagram confirmed that an SQL schema was feasible.  While the SQL design limited the amount that the schema could change throughout development, the final database schema still had some deviations from the initial outline. Most notably, the ‘Allegories/Suitable For’ table was removed, as this data could instead be included in the ‘Categories’ table. 

### Current Database Schema
The current database schema is found in the [database_schema](https://github.com/Paddywc/milestone-project -4/blob/master/database_schema/database_schema.txt) directory. 
Note that there are currently two MySQL databases. The original/testing Cloud9 database, and the ClearDB database used in the live Heroku app. However, as the MongoDB database was initially created as a clone of the Cloud9 database, they have identical schemas. 

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

## Credits
### Code
- The sources for all non-original code are displayed in comments above the relevant code
- Code from [Pretty Printed]( https://www.youtube.com/watch?v=2dEM-s3mRLE#%20for%20uploading%20images), [Treehouse]( https://teamtreehouse.com/community/how-usermixin-and-class-inheritance-work), and the [Flask-Login Documentation]( https://flask-login.readthedocs.io/en/latest/#how-it-works) were used  for creating account functions.  They are referenced above the code whenever used.  Any alterations from the source code is original work. Password removed from the UserMixin class because this information is stored in the Users table, and is therefore not required when initializing the object
- [PyCharm]( https://www.jetbrains.com/pycharm/download/) software was used for separating out the python code into separate files. Therefore, much of the code for importing functions from python files within the project directory was generated using PyCharm. PyCharm was also used to identify dependencies that were installed, but never used. These dependencies were then removed from requirements.txt, and therefore PyCharm played a role in developing this file
- The redirect_url function was taken from the [Flask Documentation](http://flask.pocoo.org/docs/1.0/reqcontext/)
- The code for converting a string into a datatime.time object was taken from [Martijn Pieters on stackoverflow](https://stackoverflow.com/questions/14295673/convert-string-into-datetime-time-object)
- Code for sorting dictionaries in python is from [Mario F on stackoverflow]( https://stackoverflow.com/questions/72899/how-do-i-sort-a-list-of-dictionaries-by-values-of-the-dictionary-in-python)
- MySQL code for inserting values into a table if they do not already exist in that table is from [user5505982 on stackoverflow]( https://stackoverflow.com/questions/3164505/mysql-insert-record-if-not-exists-in-table). Code was changed to reflect the data and tables of the application
- Code for displaying flask flash messages is from the [Flask Documentation](http://flask.pocoo.org/docs/1.0/patterns/flashing/)
- Using SQL data to generate charts required replacing single quotation marks with double quotation marks before parsing. The line of code used to do so was taken from [RafH  on stackoverflow](https://stackoverflow.com/questions/16450250/javascript-replace-single-quote-with-double-quote)
- Code for creating  and rendering charts on data visualization page is from [DJ Martin on stackoverflow]( https://stackoverflow.com/questions/21114336/how-to-add-axis-labels-for-row-chart-using-dc-js-or-d3-js), the [dc-js Github repository](https://github.com/dc-js/dc.js/blob/master/web/examples/row.html), [Kostya Marchenko on stackoverflow](https://stackoverflow.com/questions/17524627/is-there-a-way-to-tell-crossfilter-to-treat-elements-of-array-as-separate-record?noredirect=1&lq=1) and [cssndrx  on stackoverflow](https://stackoverflow.com/questions/13576906/d3-tick-marks-on-integers-only). The sources are referenced as comments above where the code is used. 
- Code for implementing Materialize styles and functions are from the [Materialize documentation]( https://materializecss.com/)

### Additional Credits
- Some of the initial recipes and categories used to populate the database are from [BBC Recipes]( https://www.bbcgoodfood.com/recipes)
- Star icons used to represent average user review scores are from [icons8]( https://icons8.com/icon/new-icons/all)
