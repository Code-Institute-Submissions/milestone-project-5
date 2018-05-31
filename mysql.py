import os
import datetime
import pymysql
from random import choice

username = os.getenv("C9_USER")


connection = pymysql.connect(host = 'localhost', user= username, password = "", db="milestoneProjectFour")


def populate_ratings():
    
    possible_recipe_ids= range(113, 115)
    possible_scores= range(1,6)
    user_id = 13
    
    i = 0
    try:
        with connection.cursor() as cursor:
            while (i < 100):
                recipe_id = choice(possible_recipe_ids)
                score = 5
                cursor.execute('INSERT INTO Reviews(UserId, RecipeId, Score) VALUES( "{0}","{1}","{2}");'.format(user_id, recipe_id, score))
                connection.commit()
                i+=1
            
    except Exception as e:
        print(e)
    return True
    
    
# populate_ratings()
    

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