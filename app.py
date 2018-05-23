import os
import requests
import pymysql
from  flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
"""
 INSERT INTO Recipes (Name, UserId, Difficulty, Serves, Blurb, PrepTime, CookTime, Instructions)
 VALUES ("Chicken Fillet Role", "123", "1", "4", "From spar. Good chicken fillet", "11:12:00", "04:10:00", "['First do this', 'Then do that', 'Then this']");
 """
app.secret_key = 'some_secret'


username = os.getenv("C9_USER")


connection = pymysql.connect(host = 'localhost', user= username, password = "", db="milestoneProjectFour")

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
    

test_function()
    
@app.route("/",  methods=["POST", "GET"] )
def add_recipe():
    if request.method == "POST":
        return render_template("addrecipe.html", testvalue="POST")
    
  
    return render_template("addrecipe.html", testvalue="NOT POST")
    
    

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')),
        debug=True)
