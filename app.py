import os
import requests
import pymysql
from  flask import Flask, Response, render_template, request, redirect, flash, url_for, jsonify
import datetime
import ast #for converting string to list

from random import choice #to avoid duplicates in file names
# for managing logins

from passlib.hash import sha256_crypt # https://pythonprogramming.net/password-hashing-flask-tutorial/
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user #https://www.youtube.com/watch?v=2dEM-s3mRLE


#for uploading images 
from werkzeug.utils import secure_filename #http://flask.pocoo.org/docs/1.0/patterns/fileuploads/



app = Flask(__name__) 
app.secret_key = 'some_secret'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' #from https://stackoverflow.com/questions/33724161/flask-login-shows-401-instead-of-redirecting-to-login-view
username = os.getenv("C9_USER")
connection = pymysql.connect(host='localhost', user= username, password = "", db="milestoneProjectFour")

#http://flask.pocoo.org/docs/1.0/patterns/fileuploads/
UPLOAD_FOLDER = 'static/images'
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER




"""
ACCOUNT FUNCTIONS
"""



class User(UserMixin):
    id = int
    username = str
    password= str
    
    is_enabled = False
    def __init__(self, id, username):
        self.id = id
        self.username = username,

    def is_active(self):
      return self.is_enabled
      
 
#https://flask-login.readthedocs.io/en/latest/#how-it-works
@login_manager.user_loader
def load_user(current_user):
    username = get_username_for_id(current_user)
    # print("Username: {0}, id: {1}".format(username, current_user))
    return User(current_user, username)
    
def get_username_for_id(userId):
    """
    returns the username from Users table that
    is on the same row as the argument userId
    """
    
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT Username FROM Users WHERE Id ="{}";'.format(userId))
            table_username_tuple = cursor.fetchone()
            table_username = table_username_tuple[0]
            return table_username
   
    except Exception as e:
        print("ERROR: {}".format(e))
        
    
        
        
def get_id_for_username(username):
    """
    returns the Id from Ssers that matches the 
    argument username
    """
    
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT Id FROM Users WHERE Username ="{}";'.format(username))
            table_id_tuple = cursor.fetchone()
            table_id = table_id_tuple[0]
            return table_id
   
    except Exception as e:
        print("GIFU ERROR: {}".format(e))
        
        


def get_encrypted_password():
    """
    returns the user password entered in the
    registration form encrypted using SHA256 
    """

    password = request.form["password"]
    encrypted_password =  sha256_crypt.encrypt(password)
    # print(encrypted_password)
    return encrypted_password
    



def add_form_values_to_users():
    """
    adds username and password entered in registration
    form to Users table
    """
    name = request.form["username"]
    password = get_encrypted_password()
    
    try:
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO Users(Username, Password) VALUES ("{0}", "{1}");'.format(name, password))
            connection.commit()
    except Exception as e:
        print("Error: {}".format(e))
    

@app.route("/register",  methods=["POST", "GET"] )
def register_user():

    if request.method == "POST":
        username = request.form["username"]
        already_exists = check_if_username_exists(username)
        
        if not already_exists:
            add_form_values_to_users()
            flash("You have successfully registered your account")
            flash("Please login now")
            return redirect(url_for("login"))
            
        
        else: 
            error_message = "ERROR: Username already exists. Please try a different username"
            return render_template("register.html", error=error_message)
           
    
    return render_template("register.html")
            
        
        
    
    


def check_if_username_exists(username):
    """
    checks if a username appears in the Users table
    returns True if username exists, False otherwise
    """
    
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT Username FROM Users WHERE Username="{}";'.format(username))
            username_tuple = cursor.fetchone()
            if username_tuple == None:
                return False
            return True
    except Exception as e:
        print("ERROR check_if_username_exists: {}".format(e))
        
        
def check_password_correct(username, password):
    """
    returns True if the password matches the username's password
    in Users table. Returns false otherwise
    """
    
    try:
        with connection.cursor() as cursor:
          cursor.execute('SELECT Password FROM Users WHERE Username="{}";'.format(username))
          table_password_tuple = cursor.fetchone()
          table_password = table_password_tuple[0]
          # below line of code from: https://pythonprogramming.net/password-hashing-flask-tutorial/
          password_correct = sha256_crypt.verify(password, table_password)
          return password_correct
          
    except Exception as e:
      print("ERROR check_password_correct: {}".format(e))
            

@app.route("/login", methods=["GET", "POST"])
def login():
    
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        
        existing_username = check_if_username_exists(username)
        if not existing_username:
            error = "ERROR: Username '{0}' not found in our database".format(username)
            return render_template("login.html", error=error)
        
        correct_password = check_password_correct(username, password)
        if not correct_password:
            error = "ERROR: Password incorrect"
            return render_template("login.html", error=error)
            
        user_id = get_id_for_username(username)
        user = User(user_id, username)
        login_user(user)
        
        # checks if /login is in the redirect_url()
        if request.path not in redirect_url():
            return redirect(redirect_url())
        else:
            return redirect(url_for("search_recipes"))
        
    else:
        return render_template("login.html")
    
    
@app.route("/logout")
# from https://www.youtube.com/watch?v=2dEM-s3mRLE
@login_required
def logout():
    logout_user()
    return redirect("/")

  
"""
HELPER FUNCTIONS
"""


def redirect_url(default='/'):
    """
    to enable request.referrer
    from: http://flask.pocoo.org/docs/1.0/reqcontext/
    """
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)


def convert_list_to_string_for_sql_search(argument_list):
    """
    XXX
    """
    list_as_string = "{}".format(argument_list)
    formatted_string = list_as_string.replace("[", "(").replace("]", ")").replace("{","(").replace("}", ")")
    
    return formatted_string


def check_if_string_contains_letters(string):
    """
    returns True if the string contains a letter,
    otherwise returns False
    """
    
    lower_string = string.lower()
    letters = ['a','b','c','d','e','f','g', 'h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    for letter in lower_string:
        if letter in letters:
            return True
    
    return False
    


def get_recipe_image():
    """
    returns the image that the user uploads 
    returns false if user didn't upload image
    """
    try:
        image_name = add_recipe_image_and_return_filename()
        image_added = True
    except Exception as e:
        image_added = False
        
    if image_added:
        return image_name
    else:
        return False
        
    
def get_prep_time():
    """
    returns prep time from the form in datetime format
    code partly from:  https://stackoverflow.com/questions/14295673/convert-string-into-datetime-time-object
    """
    prep_hours = request.form["prep-hours"]
    print(prep_hours)
    prep_mins = request.form["prep-mins"]
    prep_time =   datetime.datetime.strptime('{0}:{1}'.format(prep_hours, prep_mins), '%H:%M').time()
    
    return prep_time
    
def get_cook_time():
    """
    returns prep time from the form in datetime format
    code partly from:  https://stackoverflow.com/questions/14295673/convert-string-into-datetime-time-object
    """
    cook_hours = request.form["cook-hours"]
    cook_mins = request.form["cook-mins"]
    cook_time =   datetime.datetime.strptime('{0}:{1}'.format(cook_hours, cook_mins), '%H:%M').time()
    
    return cook_time
    
    
    
def get_categories_list():
    """
    returns a list of all categories entered 
    into the form
    """
    end_of_categories = False
    categories_list = []
    counter = 0
    
    while not end_of_categories:
        try:
            categories_list.append(request.form["category-{}".format(counter)])
        except Exception as e:
            end_of_categories = True
            
        counter+=1
    return categories_list
    
def get_instructions_list():
    """
    returns a list of all instructions 
    entered into the form
    """
    
    end_of_instructions = False
    instructions_list = []
    counter = 1
    
    while not end_of_instructions:
        try:
            instructions_list.append(request.form["instruction-{}".format(counter)])
        except Exception as e:
            end_of_instructions = True
            
        counter+=1
        
    return instructions_list
    
def get_ingredients_dictionary_list():
    """
    returns a list of dictionaries. Each dictionary
    represents an ingredient entered into the form with
    'Quantity' and 'Name" as keys
    """
    
    end_of_ingredients = False
    ingredients_dictionary_list = []
    counter = 0
    
    while not end_of_ingredients:
        try:
            ingredient_dictionary = {
                "Quantity" : request.form["quantity-{}".format(counter)],
                "Name": request.form["ingredient-{}".format(counter)]
            }
            ingredients_dictionary_list.append(ingredient_dictionary)
        except Exception as e:
            end_of_ingredients = True
            
        counter+=1
        
    return ingredients_dictionary_list
    
def get_value_from_recipes_table(column, recipe_id):
    
    """
    finds the recipe in the Recipes table that has
    the Id entered as argument. Returns the value for the
    column entered in argument 
    """
    
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT {0} FROM Recipes WHERE Id ="{1}";'.format(column, recipe_id))
            returned_tuple = cursor.fetchone()
            value = returned_tuple[0]
            return value
   
    except Exception as e:
        print("ERROR GVFRT: {}".format(e))
        
        
def get_recipe_categories(recipe_id):
    """
    returns a list the names of all categories in RecipeCategories
    that match the recipe_id. String names taken from Categories table
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(' SELECT Name FROM Categories INNER JOIN RecipeCategories on RecipeCategories.CategoryId = Categories.Id WHERE RecipeCategories.RecipeId = "{}";'.format(recipe_id))
            returned_tuples = cursor.fetchall()
            values_list = [individual_tuple[0] for individual_tuple in returned_tuples]
            return values_list
            
    except Exception as e:
        print("GRC ERROR: {}".format(e))
        
        
# print(get_recipe_categories(102))
        
        
def get_recipe_user(recipe_id):
    """
    returns the username of the user who submitted the
    recipe identified in the argument
    """
    try:
         with connection.cursor() as cursor:
            cursor.execute('SELECT Username FROM Users INNER JOIN Recipes on Users.Id = Recipes.UserId WHERE Recipes.Id = "{}";'.format(recipe_id))
            returned_tuple = cursor.fetchone()
            username = returned_tuple[0]
            return username
    
    except Exception as e:
        print("GRU ERROR: {}".format(e))
        
        
# print(get_recipe_user(102))

def get_converted_difficulty(recipe_id):
    """
    gets the difficulty of the argument recipe, 
    converted to the appropriate string
    """
    int_id = get_value_from_recipes_table("Difficulty", recipe_id)
    
    if int_id == 0:
        return "Easy"
    elif int_id == 1:
        return "Normal"
    else:
        return "Challenging"


def get_recipe_ingredients(recipe_id):
    """
    returns a list the dictionaries for all ingredients in RecipeIngredients
    that match the recipe_id. Each dictionary has Name and 
    Quantity keys. String names taken from Ingredients table
    """
    
   
    try:
         with connection.cursor() as cursor:
            cursor.execute('SELECT Ingredients.Name, Quantity FROM RecipeIngredients INNER JOIN Ingredients on Ingredients.Id = RecipeIngredients.IngredientId INNER JOIN Recipes on RecipeIngredients.RecipeId = Recipes.Id WHERE Recipes.Id = "{}";'.format(recipe_id))
            returned_tuples = cursor.fetchall()
            values_list = [{"Quantity": individual_tuple[1], "Ingredient" :individual_tuple[0]} for individual_tuple in returned_tuples]
            return values_list
    
    except Exception as e:
        print("GRI ERROR: {}".format(e))
        
        
# print(get_recipe_ingredients(103))
        
        


def get_recipe_instructions(recipe_id):
    """
    returns the argument recipe's instructions as list 
    """
    
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT Instructions FROM Recipes WHERE Id ="{}";'.format(recipe_id))
            returned_tuple = cursor.fetchone()
            list_as_string = returned_tuple[0]
            # below line from https://www.tutorialspoint.com/How-to-convert-string-representation-of-list-to-list-in-Python
            list_as_list = ast.literal_eval(list_as_string)
            return list_as_list
   
    except Exception as e:
        print("ERROR GRI: {}".format(e))
        
        
def get_recipe_reviews(recipe_id):
    """
    returns a list of all scores from the 
    Reviews table for the argument RecipeId
    """
    try:
         with connection.cursor() as cursor:
            cursor.execute('SELECT Score FROM Reviews INNER JOIN Recipes on Recipes.Id = Reviews.RecipeId  WHERE Recipes.Id = "{}";'.format(recipe_id))
            returned_tuples = cursor.fetchall()
            list_of_scores = [int(individual_tuple[0]) for individual_tuple in returned_tuples]
            return list_of_scores
    
    except Exception as e:
        print("GRR ERROR: {}".format(e))
        
        
def get_average_review_score(list_of_scores):
    """
    returns the average of all values in the argument
    """
    length_of_list = len(list_of_scores)
    if length_of_list == 0:
        return 0
    sum_count = 0
    for score in list_of_scores:
        sum_count += score
        
    average_of_scores = int((sum_count/length_of_list)+0.5)
    
    return average_of_scores
    
        

def get_all_categories_from_table():
    """
    returns a list of all category names
    from the Categories table
    """
    try:
         with connection.cursor() as cursor:
            cursor.execute('SELECT Name FROM Categories;')
            returned_tuples = cursor.fetchall()
            categories_list = [individual_tuple[0] for individual_tuple in returned_tuples]
            return categories_list
    
    except Exception as e:
        print("GACFT ERROR: {}".format(e))
        
        
def get_all_ingredients_from_table():
    """
    returns a list of all ingredient names
    from the Ingredients table
    """
    try:
         with connection.cursor() as cursor:
            cursor.execute('SELECT Name FROM Ingredients;')
            returned_tuples = cursor.fetchall()
            ingredients_list = [individual_tuple[0] for individual_tuple in returned_tuples]
            return ingredients_list
    
    except Exception as e:
        print("GAIFT ERROR: {}".format(e))
    
        
def create_recipe_values_without_image(values_dictionary):
    

    #must use double quotes inside values string 
    values = '("{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}")'.format( 
    values_dictionary["Name"], 
    current_user.id,
    values_dictionary["Difficulty"], 
    values_dictionary["Serves"], 
    values_dictionary["Blurb"], 
    values_dictionary["PrepTime"], 
    values_dictionary["CookTime"], 
    values_dictionary["Instructions"])
    
    return values
    
def create_recipe_values_with_image(values_dictionary):
    

    
    #must use double quotes inside values string 
    values = '("{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}", "{8}")'.format( 
    values_dictionary["Name"], 
    current_user.id, 
    values_dictionary["ImageName"],
    values_dictionary["Difficulty"], 
    values_dictionary["Serves"], 
    values_dictionary["Blurb"], 
    values_dictionary["PrepTime"], 
    values_dictionary["CookTime"], 
    values_dictionary["Instructions"])
    
    return values
    
    

""" 
OTHER FUNCTIONS
"""


def add_recipe_image_and_return_filename():
    """
    adds the image uploaded to the form to 
    static/images folder. Returns the image
    filename
    """
    
    
    file = request.files["recipe-img"]
    
    #three lines of code below are from: http://flask.pocoo.org/docs/1.0/patterns/fileuploads/
    #added random int to file name to avoid duplicate filenames
    filename = "{0}{1}".format(choice(range(1000)), secure_filename(file.filename))
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    print(filename)
    return filename
    
    
        
def get_form_values():
    """
    Returns a dictionary with all values entered into
    the add recipe form. Keys match their SQL names
    """

    values_dictionary = {
        "Name" : request.form["recipe-name"],
        "ImageName": get_recipe_image(),
        "Difficulty": request.form["difficulty-select"],
        "Serves" : request.form["serves"],
        "Blurb" : request.form["blurb"],
        "PrepTime": get_prep_time(),
        "CookTime": get_cook_time(),
        "Instructions": get_instructions_list(),
        "Categories" : get_categories_list(),
        "Ingredients" : get_ingredients_dictionary_list()
        
    }
    # print(values_dictionary["Ingredients"])
    return values_dictionary
    
    
def get_recipe_values(recipe_id):
    """
    returns a dictionary with all the values required 
    to render the recipe.html page. Recipe identified 
    by the Id in argument
    """
    
    values_dictionary = {
        "Name": get_value_from_recipes_table("Name", recipe_id),
        "Categories": get_recipe_categories(recipe_id),
        "ImageName" : get_value_from_recipes_table("ImageName", recipe_id),
        "Blurb" : get_value_from_recipes_table("Blurb", recipe_id),
        "Username": get_recipe_user(recipe_id),
        "Difficulty" :get_converted_difficulty(recipe_id),
        "PrepTime" : get_value_from_recipes_table("PrepTime", recipe_id),
        "CookTime" : get_value_from_recipes_table("CookTime", recipe_id),
        "Serves" : get_value_from_recipes_table("Serves", recipe_id),
        "Ingredients": get_recipe_ingredients(recipe_id),
        "Instructions":get_recipe_instructions(recipe_id),
        "Reviews" : get_recipe_reviews(recipe_id)
        
        }
    return values_dictionary
    



"""
VISUALIZING DATA
"""

def get_list_of_recipe_ids():
    """
    returns a list of all ids in the
    Recipes table
    """
    
    try:
         with connection.cursor() as cursor:
            cursor.execute('SELECT Id FROM Recipes;')
            returned_tuples = cursor.fetchall()
            list_of_ids = [int(individual_tuple[0]) for individual_tuple in returned_tuples]
            return list_of_ids
    
    except Exception as e:
        print("GLORID ERROR: {}".format(e))
        
        
def get_recipe_values_for_data_visualization(recipe_id):
    """
    A shorted version of get_recipe_values() that excludes
    the data not required for visualization. Adds ratings
    """
    values_dictionary = {
        "Name": get_value_from_recipes_table("Name", recipe_id),
        "Categories": get_recipe_categories(recipe_id),
        "Difficulty" :get_converted_difficulty(recipe_id),
        "Serves" : get_value_from_recipes_table("Serves", recipe_id),
        "Ingredients": get_recipe_ingredients(recipe_id),
        "Rating" :  get_average_review_score(get_recipe_reviews(recipe_id))
        
        }
    return values_dictionary
    
# print(get_recipe_values_for_data_visualization(105))
        
        
# print(get_list_of_recipe_ids())

def get_all_data_for_visualization():
    """
    returns a list of dictionaries. Each dictionary 
    represents a table and contains the information required 
    to visualize data
    """
    data_dictionary_list = []
    ids_list = get_list_of_recipe_ids()
    
    for recipe_id in ids_list:
        recipe_dictionary = get_recipe_values_for_data_visualization(recipe_id)
        data_dictionary_list.append(recipe_dictionary)
        
    return (data_dictionary_list)
    
    
# print(get_all_data_for_visualization())
        
@app.route("/visualizedata")
def visualize_data():
    data = get_all_data_for_visualization()
    for entry in data:
        print(entry["Rating"])
    return render_template("visualizedata.html", imported_data=data)
    

    
# @app.route("/data")
# def return_data():
#     data = get_all_data_for_visualization()
#     return data




"""
SEARCHING RECIPES
"""





def get_excluded_categories_list(filter_categories_list):
    """
    returns a list of category ids for all categories 
    not included in the argument list. Argument list is 
    list of category names
    """
    
    string_of_placeholders = ",".join(['%s']*len(filter_categories_list))

    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT Id FROM Categories INNER JOIN RecipeCategories ON Categories.Id = RecipeCategories.CategoryId  WHERE Categories.Name not in ({}) ;'.format(string_of_placeholders), filter_categories_list)
            returned_tuples = cursor.fetchall()
            category_id_set = {individual_tuple[0] for individual_tuple in returned_tuples}
            categories_id_list = [category_id for category_id in category_id_set]

            return category_id_set
    except Exception as e:
        print("GECL ERROR {}".format(e))
        
# print(get_excluded_categories_set(["Mexican", "Irish"]))

def filter_by_categories(recipe_ids_list, filter_categories_list):
    
    
    """ 
    removes ids from the argument list that are
    not matched with any of the filter categories in
    the RecipeCategories table
    """
   
    recipe_ids_string = convert_list_to_string_for_sql_search(recipe_ids_list)
    excluded_categories_id_list = get_excluded_categories_list(filter_categories_list)
    
    excluded_categories_string = convert_list_to_string_for_sql_search(excluded_categories_id_list)
    

    try:
        with connection.cursor() as cursor:
            
            cursor.execute('SELECT RecipeId FROM RecipeCategories INNER JOIN Categories ' +
            'ON Categories.Id = RecipeCategories.CategoryId '+
            'WHERE Categories.Id not in '+ excluded_categories_string +
            ' and RecipeId in ' + recipe_ids_string)
            
            returned_tuples = cursor.fetchall()
            id_list = [individual_tuple[0] for individual_tuple in returned_tuples]
            return id_list
    except Exception as e:
        print("FBC ERROR {}".format(e))
        

def get_excluded_ingredients_list(filter_ingredients_list):
    
    """
    returns a list of ingredient ids for all ingredients 
    not included in the argument list. Argument list
    is list of ingredient names
    """
    
    string_of_placeholders = ",".join(['%s']*len(filter_ingredients_list))

    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT Id FROM Ingredients INNER JOIN RecipeIngredients ON Ingredients.Id = RecipeIngredients.IngredientId  WHERE Ingredients.Name not in ({}) ;'.format(string_of_placeholders), filter_ingredients_list)
            returned_tuples = cursor.fetchall()
            ingredient_id_set = {individual_tuple[0] for individual_tuple in returned_tuples}
            ingredient_id_list = [ingredient_id for ingredient_id in ingredient_id_set]
            return ingredient_id_list
    except Exception as e:
        print("GEIS ERROR {}".format(e))
        
# print(get_excluded_ingredients_set(["Milk", "Butter"]))




def filter_by_ingredients(recipe_ids_list, filter_ingredients_list):
    
    """ 
    returns a list of ids for all recipes that
    don't contain any of the ingredients in the 
    argument set
    """
    recipe_ids_string = convert_list_to_string_for_sql_search(recipe_ids_list)
    
    excluded_ingredients_list = get_excluded_ingredients_list(filter_ingredients_list)
    excluded_ingredients_string =  convert_list_to_string_for_sql_search(excluded_ingredients_list)
    
    try:
        with connection.cursor() as cursor:
           
            cursor.execute('SELECT RecipeId FROM RecipeIngredients ' +
            'INNER JOIN Ingredients ON Ingredients.Id = RecipeIngredients.IngredientId '+
            'WHERE Ingredients.Id not in ' + excluded_ingredients_string +
            ' and RecipeId in ' + recipe_ids_string)
            returned_tuples = cursor.fetchall()
            id_list = [individual_tuple[0] for individual_tuple in returned_tuples]
            return id_list
    except Exception as e:
        print("FBC ERROR {}".format(e))
        
        


def get_recipes_average_review_score(recipe_ids_list):
    """
    returns a dictionary with the Id and average 
    review score for all recipes included in the
    argument  list
    """
    
    average_review_list = []
    
    for recipe_id in recipe_ids_list:
        average_review_list.append({
            "Id" : recipe_id,
            "Score" : int(get_average_review_score(get_recipe_reviews(recipe_id)))
        })
        
    return average_review_list
    
def add_average_review_score_to_dictionary_list(recipe_dictionary_list):
    """
    adds a 'Score' key/value pair to each dictionarinary in the 
    argument list. This represents the average review score
    """
    
    for recipe in recipe_dictionary_list:
        recipe["Score"] = int(get_average_review_score(get_recipe_reviews(recipe["Id"])))
        
    return recipe_dictionary_list
    
def sort_recipe_dictionaries_by_score(recipes_dictionary_list):
    """
    sorts the argument list of directions in descending order
    of their 'Score' value
    """
    #from:https://stackoverflow.com/questions/72899/how-do-i-sort-a-list-of-dictionaries-by-values-of-the-dictionary-in-python
    sorted_list = sorted(recipes_dictionary_list, key=lambda k: k['Score'] ,reverse=True ) 
    
    return sorted_list

def filter_by_review_score(recipe_ids_list, min_score, max_score):
    """
    returns a list of ids for all recipes with an average 
    review score that is equal to or between the arguments
    """

    
    list_of_score_dictionaries =  get_recipes_average_review_score(recipe_ids_list)
    returned_id_list = []
    for dictionary in list_of_score_dictionaries:
        if dictionary["Score"] >= int(min_score) and dictionary["Score"] <= int(max_score):
            returned_id_list.append(dictionary["Id"])
            
    return returned_id_list
    
def get_recipes_total_time(ids_list):
    """
    returns a list of dictionaries with the Id
    and total (prep+cook)  time for all recipes
    """
    total_time_list = []
    for recipe_id in ids_list:
        total_time_list.append({
            "Id": recipe_id,
            "Time": (get_value_from_recipes_table("PrepTime", recipe_id)+ get_value_from_recipes_table("CookTime", recipe_id))
        })
        
        
    return total_time_list
    
    
def filter_by_total_time(ids_list, min_time, max_time):
    """
    returns a list of recipes ids for all recipes 
    whose total time is between or equal to the arguments
    """
    
    #convert max and min times to timedelta
    # code from https://stackoverflow.com/questions/35241643/convert-datetime-time-into-datetime-timedelta-in-python-3-4?noredirect=1&lq=1
    timedelta_min_time = datetime.datetime.combine(datetime.date.min, min_time) - datetime.datetime.min
    timedelta_max_time = datetime.datetime.combine(datetime.date.min, max_time) - datetime.datetime.min
    
    
    total_time_dictionary_list = get_recipes_total_time(ids_list)
    returned_ids_list = []
    for dictionary in total_time_dictionary_list:
        if dictionary["Time"] >= timedelta_min_time and dictionary["Time"] <= timedelta_max_time:
            returned_ids_list.append(dictionary["Id"])
            
    
    return returned_ids_list
    

    

def filter_by_difficulty(recipe_ids_list, list_of_difficulties):
    """
    returns all recipes that have a difficulty score
    contained in the argument list
    """
    
    possible_difficulties = ["0","1","2"]
    # difficulties_to_exclude = list(set(possible_difficulties)-set(list_of_difficulties))
    difficulties_to_exclude = [difficulty for difficulty in possible_difficulties if difficulty not in list_of_difficulties]
   
    string_of_placeholders = ",".join(['%s']*len(difficulties_to_exclude))
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT Id FROM Recipes WHERE Difficulty not in ({}) ;'.format(string_of_placeholders),difficulties_to_exclude)
            returned_tuples = cursor.fetchall()
            id_list = [individual_tuple[0] for individual_tuple in returned_tuples]
            return id_list
            
    except Exception as e:
        print("FBD ERROR: {}".format(e))
    
    return difficulties_to_exclude
    

def combine_lists_and_remove_common_elements(list_of_lists):
    
    """
    returns a list with all unique values in the 
    argument
    """
    
    
    element_set = set()
    
    for individual_list in list_of_lists:
        for element in individual_list:
            element_set.add(element)
    
    element_list = list(element_set)
    
    return element_list

    
def get_filter_categories():
    """
    returns false if user has not entered any
    categories to filter by. Otherwise returns list 
    of category names
    """
    
    at_least_one_category = check_if_string_contains_letters(request.form["category-0"])
    if at_least_one_category:
        categories_list = get_categories_list()
        return categories_list
    return False
    
def get_filter_ingredients():
    """
    returns false if user has not entered any
    ingredients to filter by. Otherwise returns list 
    of ingredient names
    """
    
    at_least_one_ingredient = check_if_string_contains_letters(request.form["ingredient-0"])
    if at_least_one_ingredient:
        ingredients_dictionary_list = get_ingredients_dictionary_list()
        ingredients_name_list = [ingredient["Name"] for ingredient in ingredients_dictionary_list]
        # print (ingredients_name_list)
        return ingredients_name_list
    return False
    
    
def get_min_score_filter():
    """
    returns the min score selected by the user.
    Returns 0 if user did not select a min score
    """
    
    try:
        min_score_entered = request.form["min-score"]
        return min_score_entered 
    except Exception as e:
        return 0
        
def get_max_score_filter():
    """
    returns the max score selected by the user.
    Returns 5 if user did not select a max score
    """
    
    try:
        max_score_entered = request.form["max-score"]
        return max_score_entered
    except Exception as e:
        return 5
        

        
def get_min_time_filter():
    """
    returns the min time selected by the user.
    Returns 0:00 if no min time selected
    """
    try:
        min_hours = request.form["min-hours"]
    except Exception as e:
        pass
    try:
        min_mins = request.form["min-mins"]
    except Exception as e:
        pass
    
    if min_hours == "":
        min_hours = 00
    if min_mins == "":
        min_mins= 00
    
    min_time =  datetime.datetime.strptime('{0}:{1}'.format(min_hours, min_mins), '%H:%M').time()
    return  min_time
    
def get_max_time_filter():
    """
    returns the max time selected by the user.
    Returns 20:00 if no max time selected
    """
    
    try:
        max_hours = request.form["max-hours"]
    except Exception as e:
        pass
    try:
        max_mins = request.form["max-mins"]
    except Exception as e:
        pass
    
    if max_hours == "":
        max_hours = 20
    if max_mins == "":
        max_mins= 00
    
    max_time =  datetime.datetime.strptime('{0}:{1}'.format(max_hours, max_mins), '%H:%M').time()
    return  max_time
    
def get_difficulties_filter():
    """
    returns a lsit of all difficulties selected 
    by the user. Returns false if no difficulties 
    selected 
    """
    try:
        difficulties = request.form.getlist("difficulties-filter")
        # print(difficulties)
        return difficulties 
    except Exception as e:
        return False
    
def get_ids_that_match_all_filters():
    """
    returns a lsit of recipe ids that match all
    the user's filters
    """
    ids_list = get_list_of_recipe_ids()
    print(ids_list)
    
    filter_categories = get_filter_categories()
    if filter_categories:
        ids_list = filter_by_categories(ids_list, filter_categories)
        print("FC {}".format(ids_list))
        
    
    filter_ingredients = get_filter_ingredients()
    if filter_ingredients:
        ids_list = filter_by_ingredients(ids_list, filter_ingredients)
        print("FI")
        print(ids_list)
        
    min_score = get_min_score_filter()
    max_score = get_max_score_filter()
    
    if (min_score != 0) or (max_score != 5):
        ids_list = filter_by_review_score(ids_list, min_score, max_score)
        print("score")
        print(ids_list)
        
    min_time = get_min_time_filter()
    max_time = get_max_time_filter()
    

    ids_list = filter_by_total_time(ids_list, min_time, max_time)
    print("time")
    print(ids_list)
    
    difficulties_list = get_difficulties_filter()
    
    if (len(difficulties_list) > 0):
        ids_list = filter_by_difficulty(ids_list, difficulties_list)
        print("diff")
        print(ids_list)
        
    
    return ids_list
    
    
def get_search_results(recipe_ids_list):
    """
    returns all data required to render a user's
    search results (except score) after filters have been applied
    """
    ids_list_string = convert_list_to_string_for_sql_search(recipe_ids_list)
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT Id, Name, Blurb, ImageName FROM Recipes WHERE Id in  {};'.format(ids_list_string))
            returned_tuples = cursor.fetchall()
            values_list = [{ "Id": individual_tuple[0], "Name": individual_tuple[1], "Blurb": individual_tuple[2], "ImageName": individual_tuple[3]} for individual_tuple in returned_tuples]
            return values_list
    except Exception as e:
        print("GSR ERROR: {}".format(e))
    
    return True
    
def get_sorted_recipes_list(ids_list):
    """
    returns all the data required to render
    the user's search results, sorted in descending
    order by score. Returns "no_results" if ids_list is empty
    """
    if len(ids_list) == 0:
        return "no_results"
    recipes_list = get_search_results(ids_list)
    recipes_list = add_average_review_score_to_dictionary_list(recipes_list)
    recipes_list = sort_recipe_dictionaries_by_score(recipes_list)
    return recipes_list

@app.route("/", methods= ["POST", "GET"])
def search_recipes():
    categories= get_all_categories_from_table()
    ingredients = get_all_ingredients_from_table()
    
    if request.method == "POST":
        ids_list = get_ids_that_match_all_filters()
        recipes_list = get_sorted_recipes_list(ids_list)
        return render_template("index.html", categories=categories, ingredients= ingredients, recipes_list = recipes_list)
       
        
        
        
    return render_template("index.html", categories=categories, ingredients= ingredients )

"""

INTERACTING WITH MYSQL
"""


def get_last_recipe_id():
    """
    returns the value of the last Id created in
    MySQL
    """
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT LAST_INSERT_ID()")
            last_id_tuple = cursor.fetchone()
            last_id = last_id_tuple[0]
            return last_id
    except Exception as e:
       print("ERROR GET LAST ID: {}".format(e))
       
   
    
def add_to_categories_if_not_duplicate(category_list):
    """
    adds each category to Categories SQL table if 
    category name does not already exist in table
    code from: https://stackoverflow.com/questions/3164505/mysql-insert-record-if-not-exists-in-table
    """
    # print(category_list)
    try:
        with connection.cursor() as cursor:
            for category in category_list:
                lower_case = category.lower()
                capitalized = category.capitalize()
                cursor.execute('INSERT INTO Categories(Name) SELECT * FROM (SELECT "{0}" ) AS tmp WHERE NOT EXISTS (SELECT Name FROM Categories WHERE Name = "{0}");'.format(capitalized))
            connection.commit()
        
    except Exception as e:
        print("ERROR ADD TO CATAGORIES: {}".format(e))
        # connection.close()    
        
def add_to_ingredients_if_not_duplicate(ingredients_dictionary_list):
    """
    adds each ingredient name to Ingredients SQL table if 
    ingredient name does not already exist in table
    code from: https://stackoverflow.com/questions/3164505/mysql-insert-record-if-not-exists-in-table
    """
    
    ingredients_name_list = [ingredient_dictionary["Name"] for ingredient_dictionary in ingredients_dictionary_list ]
    try:
        with connection.cursor() as cursor:
            for ingredient_name in ingredients_name_list:
                cursor.execute('INSERT INTO Ingredients(Name) SELECT * FROM (SELECT "{0}" ) AS tmp WHERE NOT EXISTS (SELECT Name FROM Ingredients WHERE Name = "{0}");'.format(ingredient_name))
            connection.commit()
    except Exception as e:
        print("ERROR ADD TO INGREDIENTS: {}".format(e))
        # connection.close()
            
def add_to_recipe_ingredients(ingredients_dictionary_list, recipe_id):
    
    """
    adds the ingredients in the ingredients_dictionary to
    RecipeIngredients table. Each has a RecipeId value of 
    the second argument 
    """

    try:
        with connection.cursor() as cursor:
            for ingredient_dictionary in ingredients_dictionary_list:
                cursor.execute('INSERT INTO RecipeIngredients(RecipeId, IngredientId, Quantity) VALUES ("{0}", (SELECT Id FROM Ingredients WHERE Name="{1}"), "{2}")'.format(
                    recipe_id,
                    ingredient_dictionary["Name"],
                    ingredient_dictionary["Quantity"]
                    ))
                    
            connection.commit()
    except Exception as e:
        print("RECIPEINGRedients ERROR: {}".format(e))
        # connection.close()
    
    
def add_to_recipe_categories(categories_list, recipe_id):
    
    """
    adds each category in categories_list to RecipeCategories
    table. Each has a RecipeId value of the second argument 
    """
    
    try:
        with connection.cursor() as cursor:
            for category in categories_list:
                cursor.execute('INSERT INTO RecipeCategories(RecipeId, CategoryId) VALUES ("{0}",  (SELECT Id FROM Categories WHERE Name="{1}"))'.format(recipe_id, category))

            connection.commit()
    except Exception as e:
        print("add to recipe categories error: {}".format(e))

    

    
# def test_function():
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("SET FOREIGN_KEY_CHECKS=0")
#             insert_into = "(Name, UserId, Difficulty, Serves, Blurb, PrepTime, CookTime, Instructions)"
#             values = '("Chicken Fillet Role", "123", "1", "4", "From spar. Good chicken fillet", "11:12:00", "04:10:00", "{}")'.format("['First do this', 'Then do that', 'Then this']")
#             cursor.execute("INSERT INTO Recipes{0} VALUES {1};".format(insert_into, values))
#             connection.commit()
#     finally:
#         connection.close()

        
def insert_dictionary_into_recipes_table(values_dictionary):
    """
    function to insert the retrieved dictionary of 
    form values into the MySQL database
    """
    
    if values_dictionary["ImageName"]:
        insert_into = "(Name, UserId, ImageName, Difficulty, Serves, Blurb, PrepTime, CookTime, Instructions)"
        values = create_recipe_values_with_image(values_dictionary)
    else:
        insert_into = "(Name, UserId, Difficulty, Serves, Blurb, PrepTime, CookTime, Instructions)"
        values = create_recipe_values_without_image(values_dictionary)

    try:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO Recipes{0} VALUES {1};".format(insert_into, values))
            connection.commit()
    except Exception as e:
        print("ERROR  INSERT into recipes: {0}".format(e))
        # connection.close()
            
    
@app.route("/addrecipe",  methods=["POST", "GET"] )
@login_required
def add_recipe():
    if request.method == "POST":
        
        values_dictionary = get_form_values()
        insert_dictionary_into_recipes_table(values_dictionary)
        recipe_id = get_last_recipe_id()
        add_to_categories_if_not_duplicate(values_dictionary["Categories"])
        add_to_ingredients_if_not_duplicate(values_dictionary["Ingredients"])
        add_to_recipe_ingredients(values_dictionary["Ingredients"], recipe_id)
        add_to_recipe_categories(values_dictionary["Categories"],recipe_id )
        
        return redirect("/recipe/{}".format(recipe_id))
    
    categories= get_all_categories_from_table()
    ingredients = get_all_ingredients_from_table()
    return render_template("addrecipe.html", categories=categories, ingredients=ingredients)


def check_user_is_logged_in():
    """
    return True if the user is logged in.
    Returns False otherwsie
    """
    if current_user.is_authenticated:
        return True
    else:
        return False
def add_user_review(recipe_id):
    """
    gets the review posted by the user and adds
    it to the Reviews table along with the UserId
    """
    score = request.form["user-review"]
    user_id = current_user.id
    try:
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO Reviews(UserId, RecipeId, Score) VALUES ("{0}", "{1}", "{2}");'.format(user_id, recipe_id, score))
            connection.commit()
    except Exception as e:
        print("AUR ERROR: {}".format(e))

    return score
    
def add_to_user_favourites_table(recipe_id):
    """
    adds user_id and recipe_id to the UserFavourites. Deletes 
    any previous row with these values
    """
    user_id = current_user.id
    try:
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM UserFavourites WHERE UserId = "{0}" and RecipeId = "{1}";'.format(user_id, recipe_id))
            cursor.execute('INSERT INTO UserFavourites(UserId, RecipeId) VALUES ("{0}", "{1}");'.format(user_id, recipe_id))
            connection.commit()
    except Exception as e:
        print("ATUFT ERROR: {}".format(e))
        
        
def get_username(user_id):
    """
    returns the username that matches the 
    argument user_id
    """
    try:
         with connection.cursor() as cursor:
            cursor.execute('SELECT Username FROM Users WHERE Id = "{}";'.format(user_id))
            returned_tuple = cursor.fetchone()
            username = returned_tuple[0]
            return username
    
    except Exception as e:
        print("GU ERROR: {}".format(e))
        
def get_user_favourites(user_id):
    """
    returns a list of recipe ids for
    all of the argument user's favourite recipes
    """
    
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT Id, Name, Blurb, ImageName FROM Recipes INNER JOIN UserFavourites ON UserFavourites.RecipeId = Recipes.Id WHERE UserFavourites.UserId = "{}";'.format(user_id))
            returned_tuples = cursor.fetchall()
            values_list = [{ "Id": individual_tuple[0], "Name": individual_tuple[1], "Blurb": individual_tuple[2], "ImageName": individual_tuple[3]} for individual_tuple in returned_tuples]
            values_list = add_average_review_score_to_dictionary_list(values_list)
            return values_list
    except Exception as e:
        print("GUF ERROR: {}".format(e))
        
def get_user_recipes(user_id):
    """
    returns a list of dictionaries for all of 
    the argument user's submitted recipes. Each
    dictionary contains Id, Name, Blurb, and ImageName
    fields
    """   
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT Id, Name, Blurb, ImageName FROM Recipes WHERE UserId = "{}";'.format(user_id))
            returned_tuples = cursor.fetchall()
            values_list = [{ "Id": individual_tuple[0], "Name": individual_tuple[1], "Blurb": individual_tuple[2], "ImageName": individual_tuple[3]} for individual_tuple in returned_tuples]
            values_list =  add_average_review_score_to_dictionary_list(values_list)
            return values_list
            
    except Exception as e:
        print("GUR ERROR: {}".format(e))
    
def get_userpage_values(user_id):
    """
    return a dictionary with all the values required to
    render the userpage template
    """
    dictionary = {
        "Username" : get_username(user_id),
        "Favourites" : get_user_favourites(user_id),
        "Recipes" : get_user_recipes(user_id)
    }
    return dictionary 
    

@app.route("/userpage/<user_id>")
def userpage(user_id):
    
    userpage_values = get_userpage_values(user_id)
    return render_template("userpage.html", user= userpage_values)


@app.route("/addtofavourites/<recipe_id>")
def add_to_favourites(recipe_id):
    user_logged_in = check_user_is_logged_in()
    if not user_logged_in:
        return redirect(url_for("login"))
    else:
        add_to_user_favourites_table(recipe_id)
    return redirect(redirect_url())
    

def return_timedelta_full_hours(timedelta_time):
    """
    returns the number of full hours in 
    the timedelta argument 
    """
    
    return (timedelta_time.seconds // 3600)
    
def return_timedelta_remaining_minutes(timedelta_time):
    """
    returns the the remaining minutes from the 
    timedelta argument after subtracting the full hours
    """
    return ((timedelta_time.seconds % 3600)// 60)
    
def create_time_dictionary(recipe_dictionary):
    """
    returns a dictionaries with the hours and minutes
    for both prep and cook time
    """
    time_dictionary = {
        "PrepHours" : return_timedelta_full_hours(recipe_dictionary["PrepTime"]),
        "PrepMins" : return_timedelta_remaining_minutes(recipe_dictionary["PrepTime"]),
        "CookHours": return_timedelta_full_hours(recipe_dictionary["CookTime"]),
        "CookMins": return_timedelta_remaining_minutes(recipe_dictionary["CookTime"])
    }
    
    return time_dictionary
    


@app.route("/edit/<recipe_id>")
def edit_recipe(recipe_id):
    categories= get_all_categories_from_table()
    ingredients = get_all_ingredients_from_table()
    recipe_dictionary  = get_recipe_values(recipe_id)
    time_dictionary = create_time_dictionary(recipe_dictionary)
    
    return render_template("edit.html", recipe= recipe_dictionary, time_dictionary = time_dictionary,  categories= categories, ingredients=ingredients)
    
@app.route("/delete/<recipe_id>")
def delete_recipe(recipe_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            cursor.execute('DELETE FROM Recipes WHERE Id = "{}";'.format(recipe_id))
            cursor.execute('DELETE FROM RecipeCategories WHERE RecipeId = "{}";'.format(recipe_id))
            cursor.execute('DELETE FROM RecipeCategories WHERE RecipeId = "{}";'.format(recipe_id))
            cursor.execute('DELETE FROM RecipeIngredients WHERE RecipeId = "{}";'.format(recipe_id))
            cursor.execute('DELETE FROM Reviews WHERE RecipeId = "{}";'.format(recipe_id))
            cursor.execute('DELETE FROM UserFavourites WHERE RecipeId = "{}";'.format(recipe_id))
            connection.commit()
    
    except Exception as e:
        print("GU ERROR: {}".format(e))
    
    return redirect(redirect_url())
    
@app.route("/recipe/<recipe_id>", methods=["GET", "POST"])
def show_recipe(recipe_id):
    recipe_values = get_recipe_values(recipe_id)
    average_review_score = get_average_review_score(recipe_values["Reviews"])
    
    if request.method =="POST":

        user_logged_in = check_user_is_logged_in()
        if not user_logged_in:
            return redirect(url_for("login"))
        else:
            add_user_review(recipe_id)
        
        
    
    
    return render_template("recipe.html", recipe = recipe_values, review_score = average_review_score, recipe_id = recipe_id)

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')),
        debug=True)
