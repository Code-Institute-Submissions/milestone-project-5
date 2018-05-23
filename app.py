import os
import requests
import pymysql
from  flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

app.secret_key = 'some_secret'


username = os.getenv("C9_USER")


connection = pymysql.connect(host = 'localhost', user= username, password = "", db="milestoneProjectFour")

try:
    print("Hello word")

finally:
    connection.close()
    
    # https://stackoverflow.com/questions/17599035/django-how-can-i-call-a-view-function-from-template/19761466
# def add_category(request):
#     if(request.GET.get('mybtn')):
#       recipe_name= "if worked"
#     else:
#         recipe_name = "if didn't work"
#     return render_template("addrecipe.html", testvalue=recipe_name)
    
    
@app.route("/",  methods=["POST", "GET"] )
def add_recipe():
    if request.method == "POST":
        return render_template("addrecipe.html", testvalue="POST")
    
  
    return render_template("addrecipe.html", testvalue="NOT POST")
    
    

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')),
        debug=True)
