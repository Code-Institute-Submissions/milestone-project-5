import pymysql
import os
from flask import request
from flask_login import current_user
from passlib.handlers.sha2_crypt import \
    sha256_crypt  # informed by: https://pythonprogramming.net/password-hashing-flask-tutorial/

from helpers import convert_list_to_string_for_sql_search, get_average_review_score, create_recipe_values_with_image, \
    create_recipe_values_without_image

test_username = os.getenv("C9_USER")
username = "b3fca7f37ee0f5"
"""
connection for testing. Using C9 MySQL database: 
pymysql.connect(host='localhost', user=test_username, password="", db="milestoneProjectFour")

ClearDB database for deployment on heroku:
pymysql.connect(host='eu-cdbr-west-02.cleardb.net', user= username, password = "6e996cb2", db="heroku_12eaf3a664b1763")
"""


def open_connection():
    """
    helper function that opens the connection.
    Switch between connection and test connection as needed
    """
    return pymysql.connect(host='eu-cdbr-west-02.cleardb.net', user=username, password="6e996cb2",
                           db="heroku_12eaf3a664b1763")
    # return pymysql.connect(host='localhost', user=test_username, password="", db="milestoneProjectFour")


def get_username_for_id(user_id):
    """
    returns the username from Users table that
    is on the same row as the argument user_id
    """

    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT Username FROM Users WHERE Id ="{}";'.format(user_id))
            table_username_tuple = cursor.fetchone()
            table_username = table_username_tuple[0]
            return table_username

    except Exception as e:
        print("ERROR: {}".format(e))

    finally:
        if connection.open:
            connection.close()


def get_id_for_username(username):
    """
    returns the Id from the Users table that
    matches the argument username
    """

    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT Id FROM Users WHERE Username ="{}";'.format(username))
            table_id_tuple = cursor.fetchone()
            table_id = table_id_tuple[0]
            return table_id

    except Exception as e:
        print("ERROR: {}".format(e))

    finally:
        if connection.open:
            connection.close()


def add_form_values_to_users():
    """
    adds username and password entered in registration
    form to Users table.
    """
    name = request.form["username"]
    password = get_encrypted_password()

    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO Users(Username, Password) VALUES ("{0}", "{1}");'.format(name, password))
            connection.commit()
    except Exception as e:
        print("Error: {}".format(e))

    finally:
        if connection.open:
            connection.close()


def check_if_username_exists(username):
    """
    returns True if the argument already exists in the
    Users table, otherwise returns False
    """

    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT Username FROM Users WHERE Username="{}";'.format(username))
            username_tuple = cursor.fetchone()
            if username_tuple is None:
                return False
            return True
    except Exception as e:
        print("ERROR: {}".format(e))

    finally:
        if connection.open:
            connection.close()


def check_password_correct(username, password):
    """
    returns True if the password matches the username's password
    in Users table. Returns false otherwise. Reads passwords
    using sha256 encryption
    """

    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT Password FROM Users WHERE Username="{}";'.format(username))
            table_password_tuple = cursor.fetchone()
            table_password = table_password_tuple[0]
            # below line of code from: https://pythonprogramming.net/password-hashing-flask-tutorial/
            password_correct = sha256_crypt.verify(password, table_password)
            return password_correct

    except Exception as e:
        print("ERROR: {}".format(e))

    finally:
        if connection.open:
            connection.close()


def get_encrypted_password():
    """
    returns the user password entered in the
    registration form. Encrypts it using sha256
    """

    password = request.form["password"]
    encrypted_password = sha256_crypt.encrypt(password)
    return encrypted_password


def get_value_from_recipes_table(column, recipe_id):
    """
    identifies a recipe in the Recipes table using the
    argument Id. Returns the value of the column entered
    as an argument
    """

    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT {0} FROM Recipes WHERE Id ="{1}";'.format(column, recipe_id))
            returned_tuple = cursor.fetchone()
            value = returned_tuple[0]
            return value

    except Exception as e:
        print("ERROR: {}".format(e))

    finally:
        if connection.open:
            connection.close()


def get_recipe_categories(recipe_id):
    """
    returns a list the names of all categories in RecipeCategories
    that match the recipe_id. String names taken from Categories table
    """
    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT Name FROM Categories INNER JOIN RecipeCategories on RecipeCategories.CategoryId = '
                'Categories.Id WHERE RecipeCategories.RecipeId = "{}";'.format(
                    recipe_id))
            returned_tuples = cursor.fetchall()
            values_list = [individual_tuple[0] for individual_tuple in returned_tuples]
            return values_list

    except Exception as e:
        print("ERROR: {}".format(e))

    finally:
        if connection.open:
            connection.close()


def get_recipe_user(recipe_id):
    """
    returns the username of the user who submitted the
    recipe identified in the argument
    """
    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT Username FROM Users INNER JOIN Recipes on Users.Id = Recipes.UserId WHERE Recipes.Id = "{}";'.format(
                    recipe_id))
            returned_tuple = cursor.fetchone()
            username = returned_tuple[0]
            return username

    except Exception as e:
        print("ERROR: {}".format(e))

    finally:
        if connection.open:
            connection.close()


def get_recipe_ingredients(recipe_id):
    """
    returns a list the dictionaries for all ingredients in the
    RecipeIngredients table that match the recipe_id. Each dictionary
    has Name and Quantity keys. String names taken from Ingredients table
    """

    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT Ingredients.Name, Quantity FROM RecipeIngredients INNER JOIN Ingredients on Ingredients.Id = RecipeIngredients.IngredientId INNER JOIN Recipes on RecipeIngredients.RecipeId = Recipes.Id WHERE Recipes.Id = "{}";'.format(
                    recipe_id))
            returned_tuples = cursor.fetchall()
            values_list = [{"Quantity": individual_tuple[1], "Ingredient": individual_tuple[0]} for individual_tuple in
                           returned_tuples]
            return values_list

    except Exception as e:
        print("ERROR: {}".format(e))

    finally:
        if connection.open:
            connection.close()


def get_recipe_instructions(recipe_id):
    """
    returns the argument recipe's instructions as list
    """

    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT Instructions FROM Recipes WHERE Id ="{}";'.format(recipe_id))
            returned_tuple = cursor.fetchone()
            list_as_string = returned_tuple[0]

            list_as_list = list_as_string.split(",")

            # remove unwanted characters
            list_as_list = [x.replace("[", "") for x in list_as_list]
            list_as_list = [x.replace("]", "") for x in list_as_list]
            list_as_list = [x.replace("'", "") for x in list_as_list]

            return list_as_list

    except Exception as e:
        print("ERROR: {}".format(e))

    finally:
        if connection.open:
            connection.close()


def get_recipe_reviews(recipe_id):
    """
    returns a list of all scores from the
    Reviews table for the argument recipe
    """
    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT Score FROM Reviews INNER JOIN Recipes on Recipes.Id = Reviews.RecipeId  WHERE Recipes.Id = "{}";'.format(
                    recipe_id))
            returned_tuples = cursor.fetchall()
            list_of_scores = [int(individual_tuple[0]) for individual_tuple in returned_tuples]
            return list_of_scores

    except Exception as e:
        print("ERROR: {}".format(e))

    finally:
        if connection.open:
            connection.close()


def get_all_categories_from_table():
    """
    returns a list of all category names
    in the Categories table
    """
    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT Name FROM Categories;')
            returned_tuples = cursor.fetchall()
            categories_list = [individual_tuple[0] for individual_tuple in returned_tuples]
            return categories_list

    except Exception as e:
        print("ERROR: {}".format(e))

    finally:
        if connection.open:
            connection.close()


def get_all_ingredients_from_table():
    """
    returns a list of all ingredient names
    in the Ingredients table
    """
    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT Name FROM Ingredients;')
            returned_tuples = cursor.fetchall()
            ingredients_list = [individual_tuple[0] for individual_tuple in returned_tuples]
            return ingredients_list

    except Exception as e:
        print("ERROR: {}".format(e))

    finally:
        if connection.open:
            connection.close()


def get_list_of_recipe_ids():
    """
    returns a list of all ids in the
    Recipes table
    """

    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT Id FROM Recipes;')
            returned_tuples = cursor.fetchall()
            list_of_ids = [int(individual_tuple[0]) for individual_tuple in returned_tuples]
            return list_of_ids

    except Exception as e:
        print("ERROR: {}".format(e))

    finally:
        if connection.open:
            connection.close()


def get_excluded_categories_list(filter_categories_list):
    """
    returns a list of category ids for all categories
    not included in the argument list. Argument list is
    list of category names
    """

    string_of_placeholders = ",".join(['%s'] * len(filter_categories_list))

    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT Id FROM Categories INNER JOIN RecipeCategories ON Categories.Id = RecipeCategories.CategoryId  WHERE Categories.Name not in ({}) ;'.format(
                    string_of_placeholders), filter_categories_list)
            returned_tuples = cursor.fetchall()
            category_id_set = {individual_tuple[0] for individual_tuple in returned_tuples}

            return category_id_set
    except Exception as e:
        print("ERROR {}".format(e))

    finally:
        if connection.open:
            connection.close()


def filter_by_categories(recipe_ids_list, filter_categories_list):
    """
    removes ids from the argument list that are
    not don't have at least one of the categories
    argument categories list. Returns remaining ids
    """

    recipe_ids_string = convert_list_to_string_for_sql_search(recipe_ids_list)
    excluded_categories_id_list = get_excluded_categories_list(filter_categories_list)

    excluded_categories_string = convert_list_to_string_for_sql_search(excluded_categories_id_list)

    try:
        connection = open_connection()
        with connection.cursor() as cursor:

            cursor.execute('SELECT RecipeId FROM RecipeCategories INNER JOIN Categories ' +
                           'ON Categories.Id = RecipeCategories.CategoryId ' +
                           'WHERE Categories.Id not in ' + excluded_categories_string +
                           ' and RecipeId in ' + recipe_ids_string)

            returned_tuples = cursor.fetchall()
            id_list = [individual_tuple[0] for individual_tuple in returned_tuples]
            return id_list
    except Exception as e:
        print("ERROR {}".format(e))

    finally:
        if connection.open:
            connection.close()


def get_excluded_ingredients_list(filter_ingredients_list):
    """
    returns a list of ingredient ids for all ingredients
    not included in the argument list. Argument list
    is list of ingredient names
    """

    string_of_placeholders = ",".join(['%s'] * len(filter_ingredients_list))

    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT Id FROM Ingredients INNER JOIN RecipeIngredients ON Ingredients.Id = RecipeIngredients.IngredientId  WHERE Ingredients.Name not in ({}) ;'.format(
                    string_of_placeholders), filter_ingredients_list)
            returned_tuples = cursor.fetchall()
            ingredient_id_set = {individual_tuple[0] for individual_tuple in returned_tuples}
            ingredient_id_list = [ingredient_id for ingredient_id in ingredient_id_set]
            return ingredient_id_list
    except Exception as e:
        print("ERROR {}".format(e))

    finally:
        if connection.open:
            connection.close()


def filter_by_ingredients(recipe_ids_list, filter_ingredients_list):
    """
    returns a list of ids for all recipes that
    don't contain any of the ingredients in the
    argument ingredients list
    """
    recipe_ids_string = convert_list_to_string_for_sql_search(recipe_ids_list)

    excluded_ingredients_list = get_excluded_ingredients_list(filter_ingredients_list)
    excluded_ingredients_string = convert_list_to_string_for_sql_search(excluded_ingredients_list)

    try:
        connection = open_connection()
        with connection.cursor() as cursor:

            cursor.execute('SELECT RecipeId FROM RecipeIngredients ' +
                           'INNER JOIN Ingredients ON Ingredients.Id = RecipeIngredients.IngredientId ' +
                           'WHERE Ingredients.Id not in ' + excluded_ingredients_string +
                           ' and RecipeId in ' + recipe_ids_string)
            returned_tuples = cursor.fetchall()
            id_list = [individual_tuple[0] for individual_tuple in returned_tuples]
            return id_list
    except Exception as e:
        print("ERROR {}".format(e))

    finally:
        if connection.open:
            connection.close()


def filter_by_difficulty(recipe_ids_list, list_of_difficulties):
    """
    returns a list of ids for all recipes that have a
    difficulty value contained in the argument difficulties list
    """

    possible_difficulties = ["0", "1", "2"]
    difficulties_to_exclude = [difficulty for difficulty in possible_difficulties if
                               difficulty not in list_of_difficulties]

    string_of_placeholders = ",".join(['%s'] * len(difficulties_to_exclude))
    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT Id FROM Recipes WHERE Difficulty not in ({}) ;'.format(string_of_placeholders),
                           difficulties_to_exclude)
            returned_tuples = cursor.fetchall()
            id_list = [individual_tuple[0] for individual_tuple in returned_tuples]
            return id_list

    except Exception as e:
        print("ERROR: {}".format(e))

    finally:
        if connection.open:
            connection.close()

    return difficulties_to_exclude


def get_search_results(recipe_ids_list):
    """
    returns all data required to render a user's
    search results (except score) after filters have been applied
    """
    ids_list_string = convert_list_to_string_for_sql_search(recipe_ids_list)
    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT Id, Name, Blurb, ImageName FROM Recipes WHERE Id in  {};'.format(ids_list_string))
            returned_tuples = cursor.fetchall()
            values_list = [{"Id": individual_tuple[0], "Name": individual_tuple[1], "Blurb": individual_tuple[2],
                            "ImageName": individual_tuple[3]} for individual_tuple in returned_tuples]
            return values_list
    except Exception as e:
        print("ERROR: {}".format(e))

    finally:
        if connection.open:
            connection.close()
    return True


def get_last_recipe_id():
    """
    returns the most recent Id added to
    the Recipes table
    """
    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT Id FROM Recipes ORDER BY Id DESC LIMIT 1")
            last_id_tuple = cursor.fetchone()
            last_id = last_id_tuple[0]
            return last_id
    except Exception as e:
        print("ERROR: {}".format(e))

    finally:
        if connection.open:
            connection.close()


def add_to_categories_if_not_duplicate(category_list):
    """
    adds each category to Categories SQL table if
    category name does not already exist in table
    code from: https://stackoverflow.com/questions/3164505/mysql-insert-record-if-not-exists-in-table
    """
    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            for category in category_list:
                lower_case = category.lower()
                capitalized = lower_case.capitalize()
                cursor.execute(
                    'INSERT INTO Categories(Name) SELECT * FROM (SELECT "{0}" ) AS tmp WHERE NOT EXISTS (SELECT Name FROM Categories WHERE Name = "{0}");'.format(
                        capitalized))
            connection.commit()

    except Exception as e:
        print("ERROR: {}".format(e))
    finally:
        if connection.open:
            connection.close()


def add_to_ingredients_if_not_duplicate(ingredients_dictionary_list):
    """
    adds each ingredient name to Ingredients SQL table if
    ingredient name does not already exist in table
    code from: https://stackoverflow.com/questions/3164505/mysql-insert-record-if-not-exists-in-table
    """

    ingredients_name_list = [ingredient_dictionary["Name"] for ingredient_dictionary in ingredients_dictionary_list]
    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            for ingredient_name in ingredients_name_list:
                cursor.execute(
                    'INSERT INTO Ingredients(Name) SELECT * FROM (SELECT "{0}" ) AS tmp WHERE NOT EXISTS (SELECT Name FROM Ingredients WHERE Name = "{0}");'.format(
                        ingredient_name))
            connection.commit()
    except Exception as e:
        print("ERROR: {}".format(e))
    finally:
        if connection.open:
            connection.close()


def add_to_recipe_ingredients(ingredients_dictionary_list, recipe_id):
    """
    adds the ingredients in the ingredients_dictionary to
    RecipeIngredients table. Each has a RecipeId value of
    the second argument
    """
    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            for ingredient_dictionary in ingredients_dictionary_list:
                print(ingredient_dictionary["Name"])
                cursor.execute(
                    'INSERT INTO RecipeIngredients(RecipeId, IngredientId, Quantity) VALUES ("{0}", (SELECT Id FROM Ingredients WHERE Name="{1}"), "{2}")'.format(
                        recipe_id,
                        ingredient_dictionary["Name"],
                        ingredient_dictionary["Quantity"]
                    ))

            connection.commit()
    except Exception as e:
        print("ERROR: {}".format(e))
    finally:
        if connection.open:
            connection.close()


def add_to_recipe_categories(categories_list, recipe_id):
    """
    adds each category in categories_list to RecipeCategories
    table. Each has a RecipeId value of the second argument
    """
    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            for category in categories_list:
                cursor.execute(
                    'INSERT INTO RecipeCategories(RecipeId, CategoryId) VALUES ("{0}",  (SELECT Id FROM Categories WHERE Name="{1}"))'.format(
                        recipe_id, category))

            connection.commit()
    except Exception as e:
        print("ERROR: {}".format(e))

    finally:
        if connection.open:
            connection.close()


def add_user_review(recipe_id):
    """
    gets the review posted by the user and adds
    it to the Reviews table along with the UserId.
    If user has already submitted a rating for that recipe,
    deletes that rating.
    """
    score = request.form["user-review"]
    user_id = current_user.id
    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM Reviews WHERE UserId = "{0}" and RecipeId = "{1}";'.format(user_id, recipe_id))
            cursor.execute(
                'INSERT INTO Reviews(UserId, RecipeId, Score) VALUES ("{0}", "{1}", "{2}");'.format(user_id, recipe_id,
                                                                                                    score))
            connection.commit()
    except Exception as e:
        print("ERROR: {}".format(e))

    finally:
        if connection.open:
            connection.close()

    return score


def add_to_user_favourites_table(recipe_id):
    """
    adds user_id and recipe_id to the UserFavourites. Deletes
    any previous row with these values
    """
    user_id = current_user.id
    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                'DELETE FROM UserFavourites WHERE UserId = "{0}" and RecipeId = "{1}";'.format(user_id, recipe_id))
            cursor.execute(
                'INSERT INTO UserFavourites(UserId, RecipeId) VALUES ("{0}", "{1}");'.format(user_id, recipe_id))
            connection.commit()
    except Exception as e:
        print("ERROR: {}".format(e))

    finally:
        if connection.open:
            connection.close()


def get_username(user_id):
    """
    returns the username that matches the
    argument user_id
    """
    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT Username FROM Users WHERE Id = "{}";'.format(user_id))
            returned_tuple = cursor.fetchone()
            username = returned_tuple[0]
            return username

    except Exception as e:
        print("ERROR: {}".format(e))

    finally:
        if connection.open:
            connection.close()


def get_user_favourites(user_id):
    """
    returns a list of recipe ids for
    all of the argument user's favourite recipes
    """
    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT Id, Name, Blurb, ImageName FROM Recipes INNER JOIN UserFavourites ON UserFavourites.RecipeId = Recipes.Id WHERE UserFavourites.UserId = "{}";'.format(
                    user_id))
            returned_tuples = cursor.fetchall()
            values_list = [{"Id": individual_tuple[0], "Name": individual_tuple[1], "Blurb": individual_tuple[2],
                            "ImageName": individual_tuple[3]} for individual_tuple in returned_tuples]
            values_list = add_average_review_score_to_dictionary_list(values_list)
            return values_list
    except Exception as e:
        print("ERROR: {}".format(e))

    finally:
        if connection.open:
            connection.close()


def get_user_recipes(user_id):
    """
    returns a list of dictionaries for all of
    the argument user's submitted recipes. Each
    dictionary contains Id, Name, Blurb, and ImageName
    fields
    """
    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT Id, Name, Blurb, ImageName FROM Recipes WHERE UserId = "{}";'.format(user_id))
            returned_tuples = cursor.fetchall()
            values_list = [{"Id": individual_tuple[0], "Name": individual_tuple[1], "Blurb": individual_tuple[2],
                            "ImageName": individual_tuple[3]} for individual_tuple in returned_tuples]
            values_list = add_average_review_score_to_dictionary_list(values_list)
            return values_list

    except Exception as e:
        print("ERROR: {}".format(e))

    finally:
        if connection.open:
            connection.close()


def add_average_review_score_to_dictionary_list(recipe_dictionary_list):
    """
    adds a 'Score' key/value pair to each dictionarinary in the
    argument list. This represents the average review score
    """

    for recipe in recipe_dictionary_list:
        recipe["Score"] = int(get_average_review_score(get_recipe_reviews(recipe["Id"])))

    return recipe_dictionary_list


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


def insert_dictionary_into_recipes_table(values_dictionary):
    """
    function to insert the retrieved dictionary of
    add recipe form values into the MySQL database
    """

    if values_dictionary["ImageName"]:
        insert_into = "(Name, UserId, ImageName, Difficulty, Serves, Blurb, PrepTime, CookTime, Instructions)"
        values = create_recipe_values_with_image(values_dictionary)
    else:
        insert_into = "(Name, UserId, Difficulty, Serves, Blurb, PrepTime, CookTime, Instructions)"
        values = create_recipe_values_without_image(values_dictionary)

    try:
        connection = open_connection()
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO Recipes{0} VALUES {1};".format(insert_into, values))
            connection.commit()
    except Exception as e:
        print("ERROR: {0}".format(e))
        # connection.close()
    finally:
        if connection.open:
            connection.close()
