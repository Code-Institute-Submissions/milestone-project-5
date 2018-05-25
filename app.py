import os
import requests
import pymysql
from  flask import Flask, render_template, request, redirect, url_for
import datetime


# for managing logins
from flask_login import LoginManager, current_user, login_user
from passlib.hash import sha256_crypt # https://pythonprogramming.net/password-hashing-flask-tutorial/


#for uploading images 
from werkzeug.utils import secure_filename 



# login_manager = LoginManager()

app = Flask(__name__)

# login_manager.init_app(app)


app.secret_key = 'some_secret'

username = os.getenv("C9_USER")

connection = pymysql.connect(host = 'localhost', user= username, password = "", db="milestoneProjectFour")


"""
ACCOUNT FUNCTIONS
"""

def get_encrypted_password():
    """
    returns the user password entered in the
    registration form encrypted using SHA256 
    """

    password = request.form["password"]
    encrypted_password =  sha256_crypt.encrypt(password)
    # print(encrypted_password)
    return encrypted_password
    
    
    
def add_to_users():
    """
    adds username and password entered in form
    to Users table
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
        add_to_users()
    return render_template("register.html")
    



# @login_manager.user_loader
# def load_user(user_id):
#     return User.get(user_id)
    
    



"""
HELPER FUNCTIONS
"""


def get_recipe_image():
    """
    returns the image that the user uploads 
    returns false if user didn't upload image
    """
    try:
        recipe_image = request.files["recipe-img"]
        image_added = True
    except Exception as e:
        image_added = False
        
    if image_added:
        return recipe_image 
    else:
        return False
        
    
def get_prep_time():
    """
    returns prep time from the form in datetime format
    code partly from:  https://stackoverflow.com/questions/14295673/convert-string-into-datetime-time-object
    """
    prep_hours = request.form["prep-hours"]
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
    
        
        
def create_recipe_values_without_image(values_dictionary):
    
    dummy_userid = "123"
    
    #must use double quotes inside values string 
    values = '("{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}")'.format( 
    values_dictionary["Name"], 
    dummy_userid, 
    values_dictionary["Difficulty"], 
    values_dictionary["Serves"], 
    values_dictionary["Blurb"], 
    values_dictionary["PrepTime"], 
    values_dictionary["CookTime"], 
    values_dictionary["Instructions"])
    
    return values
    
def create_recipe_values_with_image(values_dictionary):
    
    dummy_userid = "123"
    
    #must use double quotes inside values string 
    values = '("{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}", "{8}")'.format( 
    values_dictionary["Name"], 
    dummy_userid, 
    values_dictionary["Image"],
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
        
        
def get_form_values():
    """
    Returns a dictionary with all values entered into
    the add recipe form. Keys match their SQL names
    """

    values_dictionary = {
        "Name" : request.form["recipe-name"],
        "Image": get_recipe_image(),
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
    
    if values_dictionary["Image"]:
        insert_into = "(Name, UserId, Image, Difficulty, Serves, Blurb, PrepTime, CookTime, Instructions)"
        values = create_recipe_values_with_image(values_dictionary)
    else:
        insert_into = "(Name, UserId, Difficulty, Serves, Blurb, PrepTime, CookTime, Instructions)"
        values = create_recipe_values_without_image(values_dictionary)

    try:
        with connection.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            cursor.execute("INSERT INTO Recipes{0} VALUES {1};".format(insert_into, values))
            connection.commit()
    except Exception as e:
        print("ERROR  INSERT into recipes: {0}".format(e))
        # connection.close()
            
    
@app.route("/",  methods=["POST", "GET"] )
def add_recipe():
    if request.method == "POST":
        values_dictionary = get_form_values()
        # print(values_dictionary)
        insert_dictionary_into_recipes_table(values_dictionary)
        recipe_id = get_last_recipe_id()
        add_to_categories_if_not_duplicate(values_dictionary["Categories"])
        add_to_ingredients_if_not_duplicate(values_dictionary["Ingredients"])
        add_to_recipe_ingredients(values_dictionary["Ingredients"], recipe_id)
        add_to_recipe_categories(values_dictionary["Categories"],recipe_id )
        
        return render_template("addrecipe.html", testvalue="POST")
    
  
    return render_template("addrecipe.html", testvalue="NOT POST")
    


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')),
        debug=True)
