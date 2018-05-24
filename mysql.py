import os
import datetime
import pymysql


username = os.getenv("C9_USER")


connection = pymysql.connect(host = 'localhost', user= username, password = "", db="milestoneProjectFour")



def add_origins():
    
    origins=[
    "Indian",
    "Chinese",
    "Thai",
    "Asian",
    "Italian",
    "French",
    "Spanish",
    "European",
    "Mexican",
    "Latin American",
    "African",
    "American",
    "Australian",
    "British",
    "Irish",
    "Jewish"]
    try:
        with connection.cursor() as cursor:
            for origin in origins:
                cursor.execute('INSERT INTO Categories(Name) VALUES ("{0}");'.format(origin))
            connection.commit()
    except Exception as e:
        print(e)
        connection.close()
        
        
        
# add_origins()