import os
import requests
import pymysql
from  flask import Flask, render_template, request, redirect, url_for
import datetime
from werkzeug.utils import secure_filename #for uploading images 


app = Flask(__name__)
"""
 INSERT INTO Recipes (Name, UserId, Difficulty, Serves, Blurb, PrepTime, CookTime, Instructions)
 VALUES ("Chicken Fillet Role", "123", "1", "4", "From spar. Good chicken fillet", "11:12:00", "04:10:00", "['First do this', 'Then do that', 'Then this']");
 """
app.secret_key = 'some_secret'


username = os.getenv("C9_USER")


connection = pymysql.connect(host = 'localhost', user= username, password = "", db="milestoneProjectFour")


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
    # https://stackoverflow.com/questions/14295673/convert-string-into-datetime-time-object
    prep_hours = request.form["prep-hours"]
    prep_mins = request.form["prep-mins"]
    prep_time =   datetime.datetime.strptime('{0}:{1}'.format(prep_hours, prep_mins), '%H:%M').time()
    
    return prep_time
    
def get_cook_time():
    # https://stackoverflow.com/questions/14295673/convert-string-into-datetime-time-object
    cook_hours = request.form["cook-hours"]
    cook_mins = request.form["cook-mins"]
    cook_time =   datetime.datetime.strptime('{0}:{1}'.format(cook_hours, cook_mins), '%H:%M').time()
    
    return cook_time
    
def get_instructions_list():
    
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
        
        
        
        
    

def get_form_values():

    values_dictionary = {
        "Name" : request.form["recipe-name"],
        "Image": get_recipe_image(),
        "Difficulty": request.form["difficulty-select"],
        "Serves" : request.form["serves"],
        "Blurb" : request.form["blurb"],
        "PrepTime": get_prep_time(),
        "CookTime": get_cook_time(),
        "Instructions": get_instructions_list()
    }
    return values_dictionary

def test_function():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            insert_into = "(Name, UserId, Difficulty, Serves, Blurb, PrepTime, CookTime, Instructions)"
            values = '("Chicken Fillet Role", "123", "1", "4", "From spar. Good chicken fillet", "11:12:00", "04:10:00", "{}")'.format("['First do this', 'Then do that', 'Then this']")
            cursor.execute("INSERT INTO Recipes{0} VALUES {1};".format(insert_into, values))
            connection.commit()
    finally:
        connection.close()
        
        
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
        print(e)
        connection.close()
            
    
@app.route("/",  methods=["POST", "GET"] )
def add_recipe():
    if request.method == "POST":
        values_dictionary = get_form_values()
        insert_dictionary_into_recipes_table(values_dictionary)
        
        return render_template("addrecipe.html", testvalue="POST")
    
  
    return render_template("addrecipe.html", testvalue="NOT POST")
    
    

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')),
        debug=True)
