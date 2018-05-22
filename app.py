import os
import pymysql
from  flask import Flask, render_template, redirect, url_for

app = Flask(__name__)



username = os.getenv("C9_USER")


connection = pymysql.connect(host = 'localhost', user= username, password = "", db="milestoneProjectFour")

try:
    print("Hello word")

finally:
    connection.close()
    
    
    


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')),
        debug=True)
