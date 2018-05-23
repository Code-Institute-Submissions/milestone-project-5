import os
import requests
import pymysql
from  flask import Flask, render_template, request, redirect, url_for
import datetime


app = Flask(__name__)
"""
 INSERT INTO Recipes (Name, UserId, Difficulty, Serves, Blurb, PrepTime, CookTime, Instructions)
 VALUES ("Chicken Fillet Role", "123", "1", "4", "From spar. Good chicken fillet", "11:12:00", "04:10:00", "['First do this', 'Then do that', 'Then this']");
 """
app.secret_key = 'some_secret'


username = os.getenv("C9_USER")


connection = pymysql.connect(host = 'localhost', user= username, password = "", db="milestoneProjectFour")


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
    

# test_function()
    
@app.route("/",  methods=["POST", "GET"] )
def add_recipe():
    if request.method == "POST":
        values_dictionary = get_form_values()
        print (values_dictionary["Name"])
        print (values_dictionary["Serves"])
        print (values_dictionary["Blurb"])
        print (values_dictionary["PrepTime"])
        print (values_dictionary["CookTime"])
        print (values_dictionary["Difficulty"])
        print (values_dictionary["Instructions"])
        return render_template("addrecipe.html", testvalue="POST")
    
  
    return render_template("addrecipe.html", testvalue="NOT POST")
    
    

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')),
        debug=True)
