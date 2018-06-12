import datetime
import os
from random import choice  # to avoid duplicates in file names
from flask import render_template, request, redirect, flash, url_for
from flask_login import UserMixin, login_user, \
    login_required, current_user, logout_user  # informed by: https://www.youtube.com/watch?v=2dEM-s3mRLE
# for uploading images
from werkzeug.utils import secure_filename  # informed by: http://flask.pocoo.org/docs/1.0/patterns/fileuploads/

from app_init import app, login_manager
from helpers import add_average_review_score_to_dictionary_list, get_average_review_score, redirect_url, \
    check_if_string_contains_letters, get_converted_difficulty, create_recipe_values_without_image, \
    create_recipe_values_with_image
from sql_fuctions import open_connection, get_username_for_id, get_id_for_username, add_form_values_to_users, \
    check_if_username_exists, check_password_correct, get_value_from_recipes_table, get_recipe_categories, \
    get_recipe_user, get_recipe_ingredients, get_recipe_instructions, get_recipe_reviews, get_all_categories_from_table, \
    get_all_ingredients_from_table, get_list_of_recipe_ids, filter_by_categories, filter_by_ingredients, \
    filter_by_difficulty, get_search_results, get_last_recipe_id, add_to_categories_if_not_duplicate, \
    add_to_ingredients_if_not_duplicate, add_to_recipe_ingredients, add_to_recipe_categories, add_user_review, \
    add_to_user_favourites_table, get_username, get_user_favourites, get_user_recipes

app.secret_key = 'some_secret'

login_manager.init_app(app)
login_manager.login_view = 'login'  # from https://stackoverflow.com/questions/33724161/flask-login-shows-401-instead-of-redirecting-to-login-view



# from: http://flask.pocoo.org/docs/1.0/patterns/fileuploads/
UPLOAD_FOLDER = 'static/images'
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

"""
ACCOUNT FUNCTIONS
"""


class User(UserMixin):
    """
    class for creating and logging into
    users accounts. Code partly 
    from: https://teamtreehouse.com/community/how-usermixin-and-class-inheritance-work
    """
    id = int
    username = str
    password = str

    is_enabled = False

    def __init__(self, id, username):
        self.id = id
        self.username = username,

    def is_active(self):
        return self.is_enabled


@login_manager.user_loader
def load_user(current_user):
    """
    for loading an instance of the 
    User class. Code party from:
    https://flask-login.readthedocs.io/en/latest/#how-it-works
    """
    username = get_username_for_id(current_user)
    return User(current_user, username)


@app.route("/register", methods=["POST", "GET"])
def register_user():
    """
    registering page. Only accepts registration if:
    Username is less than 15 chars
    Username doesn't already exist 
    
    adds values to Users table if registeration successful
    """
    if request.method == "POST":
        username = request.form["username"]
        already_exists = check_if_username_exists(username)

        if len(username) > 15:
            error_message = "ERROR. Username can't be more than 15 characters"
            return render_template("register.html", error=error_message)

        if not already_exists:
            add_form_values_to_users()
            flash("You have successfully registered your account")
            flash("Please login now")
            return redirect(url_for("login"))


        else:
            error_message = "ERROR: Username already exists. Please try a different username"
            return render_template("register.html", error=error_message)

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """"
    login page. Logs in user if:
    username is in Users table
    password matches that user's password
    
    if the user's previous page is not the login page,
    returns user to previous page. Otherwise redirects to 
    home page
    
    Refreshes page with error message if login unsuccessful 
    """
    if request.method == "POST":
        username = request.form["login-username"]
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
        flash("Successfully logged in")
        # checks if /login is in the redirect_url()
        if request.path not in redirect_url():
            return redirect(redirect_url())
        else:
            return redirect(url_for("search_recipes"))

    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """
    functionality to logout user.
    Code from: https://www.youtube.com/watch?v=2dEM-s3mRLE
    """
    logout_user()
    flash("Successfully logged out")
    return redirect(url_for("search_recipes"))


"""
HELPER FUNCTIONS
"""


def get_recipe_image_filename():
    """
    if the user submitted an image, uploads that
    image and returns its filename. If the user did
    not upload an image, returns False
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
    returns prep time from the form in datetime format.
    If user did not submit a value for minutes, sets their value as 00
    code partly from:  https://stackoverflow.com/questions/14295673/convert-string-into-datetime-time-object
    """
    prep_hours = request.form["prep-hours"]
    try:
        prep_mins = request.form["prep-mins"]
    except Exception as e:
        pass

    if prep_mins == "":
        prep_mins = 00

    prep_time = datetime.datetime.strptime('{0}:{1}'.format(prep_hours, prep_mins), '%H:%M').time()

    return prep_time


def get_cook_time():
    """
    returns prep time from the form in datetime format
    code partly from:  https://stackoverflow.com/questions/14295673/convert-string-into-datetime-time-object
    """
    cook_hours = request.form["cook-hours"]
    try:
        cook_mins = request.form["cook-mins"]
    except Exception as e:
        pass

    if cook_mins == "":
        cook_mins = 00

    cook_time = datetime.datetime.strptime('{0}:{1}'.format(cook_hours, cook_mins), '%H:%M').time()

    return cook_time


def get_categories_list():
    """
    returns a list of all categories entered 
    into the add recipe form
    """
    end_of_categories = False
    categories_list = []
    counter = 0

    while not end_of_categories:
        try:
            category = request.form["category-{}".format(counter)]
            if check_if_string_contains_letters(category):
                categories_list.append(category)
            else:
                end_of_categories = True
        except Exception as e:
            end_of_categories = True

        counter += 1
    return categories_list


def get_instructions_list():
    """
    returns a list of all instructions 
    entered into the add recipe form
    """

    end_of_instructions = False
    instructions_list = []
    counter = 1

    while not end_of_instructions:
        try:
            instruction = request.form["instruction-{}".format(counter)]
            if check_if_string_contains_letters(instruction):
                instructions_list.append(instruction)
            else:
                end_of_instructions = True
        except Exception as e:
            end_of_instructions = True

        counter += 1

    return instructions_list


def get_ingredients_dictionary_list():
    """
    returns a list of dictionaries. Each dictionary
    represents an ingredient entered into the add recipe
    form, with 'Quantity' and 'Name" as keys. Capitalizes 
    name value. All other chars set to lowercase
    """

    end_of_ingredients = False
    ingredients_dictionary_list = []
    counter = 0

    while not end_of_ingredients:
        try:
            ingredient_name = request.form["ingredient-{}".format(counter)]
            if check_if_string_contains_letters(ingredient_name):
                lowercase_ingredient_name = ingredient_name.lower()
                capitalized_ingredient_name = lowercase_ingredient_name.capitalize()
                ingredient_dictionary = {
                    "Quantity": request.form["quantity-{}".format(counter)],
                    "Name": capitalized_ingredient_name
                }
                ingredients_dictionary_list.append(ingredient_dictionary)
            else:
                end_of_ingredients = True

        except Exception as e:
            end_of_ingredients = True

        counter += 1

    return ingredients_dictionary_list


""" 
OTHER FUNCTIONS
"""


def add_recipe_image_and_return_filename():
    """
    adds the image uploaded on the add recipe form
    to the project image folder. Adds random ints
    to end of filename to avoid overwiping files 
    of the same name. Returns the filename
    """

    file = request.files["recipe-img"]

    # two lines of code below are from: http://flask.pocoo.org/docs/1.0/patterns/fileuploads/
    # added random int to file name to avoid duplicate filenames
    filename = "{0}{1}".format(choice(range(1000)), secure_filename(file.filename))
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return filename


def get_form_values():
    """
    Returns a dictionary with all values entered into
    the add recipe form. Keys match their SQL names
    """

    values_dictionary = {
        "Name": request.form["recipe-name"],
        "ImageName": get_recipe_image_filename(),
        "Difficulty": request.form["difficulty-select"],
        "Serves": request.form["serves"],
        "Blurb": request.form["blurb"],
        "PrepTime": get_prep_time(),
        "CookTime": get_cook_time(),
        "Instructions": get_instructions_list(),
        "Categories": get_categories_list(),
        "Ingredients": get_ingredients_dictionary_list()

    }
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
        "ImageName": get_value_from_recipes_table("ImageName", recipe_id),
        "Blurb": get_value_from_recipes_table("Blurb", recipe_id),
        "Username": get_recipe_user(recipe_id),
        "Difficulty": get_converted_difficulty(recipe_id),
        "PrepTime": get_value_from_recipes_table("PrepTime", recipe_id),
        "CookTime": get_value_from_recipes_table("CookTime", recipe_id),
        "Serves": get_value_from_recipes_table("Serves", recipe_id),
        "Ingredients": get_recipe_ingredients(recipe_id),
        "Instructions": get_recipe_instructions(recipe_id),
        "Reviews": get_recipe_reviews(recipe_id)

    }
    return values_dictionary


"""
VISUALIZING DATA
"""


def get_recipe_values_for_data_visualization(recipe_id):
    """
    A shorted version of get_recipe_values() that excludes
    the data not required for visualization. Adds rating
    """
    values_dictionary = {
        "Name": get_value_from_recipes_table("Name", recipe_id),
        "Categories": get_recipe_categories(recipe_id),
        "Difficulty": get_converted_difficulty(recipe_id),
        "Serves": get_value_from_recipes_table("Serves", recipe_id),
        "Ingredients": get_recipe_ingredients(recipe_id),
        "Rating": get_average_review_score(get_recipe_reviews(recipe_id))

    }
    return values_dictionary


def get_all_data_for_visualization():
    """
    returns a list of dictionaries. Each dictionary 
    represents a recipe and contains the information required 
    to visualize data
    """
    data_dictionary_list = []
    ids_list = get_list_of_recipe_ids()

    for recipe_id in ids_list:
        recipe_dictionary = get_recipe_values_for_data_visualization(recipe_id)
        data_dictionary_list.append(recipe_dictionary)

    return data_dictionary_list


@app.route("/visualizedata")
def visualize_data():
    """
    renders the visualize data page
    """
    data = get_all_data_for_visualization()
    return render_template("visualizedata.html", imported_data=data)


"""
SEARCHING RECIPES
"""


def get_recipes_average_review_score(recipe_ids_list):
    """
    returns a dictionary with the Id and average 
    review score for all recipes included in the
    argument list
    """

    average_review_list = []

    for recipe_id in recipe_ids_list:
        average_review_list.append({
            "Id": recipe_id,
            "Score": int(get_average_review_score(get_recipe_reviews(recipe_id)))
        })

    return average_review_list


def sort_recipe_dictionaries_by_score(recipes_dictionary_list):
    """
    sorts the argument list of dictionaries in descending order
    of their 'Score' value
    """
    # below line of code from:
    # https://stackoverflow.com/questions/72899/how-do-i-sort-a-list-of-dictionaries-by-values-of-the-dictionary-in-python
    sorted_list = sorted(recipes_dictionary_list, key=lambda k: k['Score'], reverse=True)

    return sorted_list


def filter_by_review_score(recipe_ids_list, min_score, max_score):
    """
    returns a list of ids for all recipes with an average 
    review score that is equal to or between the arguments
    """

    list_of_score_dictionaries = get_recipes_average_review_score(recipe_ids_list)
    returned_id_list = []
    for dictionary in list_of_score_dictionaries:
        if int(min_score) <= dictionary["Score"] <= int(max_score):
            returned_id_list.append(dictionary["Id"])

    return returned_id_list


def get_recipes_total_time(ids_list):
    """
    returns a list of dictionaries with the Id
    and total(prep+cook) time for all recipes in 
    the argument list
    """
    total_time_list = []
    for recipe_id in ids_list:
        total_time_list.append({
            "Id": recipe_id,
            "Time": (get_value_from_recipes_table("PrepTime", recipe_id) + get_value_from_recipes_table("CookTime",
                                                                                                        recipe_id))
        })

    return total_time_list


def filter_by_total_time(ids_list, min_time, max_time):
    """
    returns a list of recipes ids for all recipes in the 
    argument ids list whose total time is between or equal to the
    other two arguments
    """

    # convert max and min times to timedelta
    # code from https://stackoverflow.com/questions/35241643/convert-datetime-time-into-datetime-timedelta-in-python-3-4?noredirect=1&lq=1
    timedelta_min_time = datetime.datetime.combine(datetime.date.min, min_time) - datetime.datetime.min
    timedelta_max_time = datetime.datetime.combine(datetime.date.min, max_time) - datetime.datetime.min

    total_time_dictionary_list = get_recipes_total_time(ids_list)
    returned_ids_list = []
    for dictionary in total_time_dictionary_list:
        if timedelta_min_time <= dictionary["Time"] <= timedelta_max_time:
            returned_ids_list.append(dictionary["Id"])

    return returned_ids_list


def get_filter_categories():
    """
    returns false if user has not entered any
    categories to filter by. Otherwise returns a 
    list of their selected category names
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
        min_mins = 00

    min_time = datetime.datetime.strptime('{0}:{1}'.format(min_hours, min_mins), '%H:%M').time()
    return min_time


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
        max_mins = 00

    max_time = datetime.datetime.strptime('{0}:{1}'.format(max_hours, max_mins), '%H:%M').time()
    return max_time


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

    filter_categories = get_filter_categories()
    if filter_categories:
        ids_list = filter_by_categories(ids_list, filter_categories)
        print("FC {}".format(ids_list))

    filter_ingredients = get_filter_ingredients()
    if filter_ingredients:
        ids_list = filter_by_ingredients(ids_list, filter_ingredients)

    min_score = get_min_score_filter()
    max_score = get_max_score_filter()

    if (min_score != 0) or (max_score != 5):
        ids_list = filter_by_review_score(ids_list, min_score, max_score)

    min_time = get_min_time_filter()
    max_time = get_max_time_filter()

    ids_list = filter_by_total_time(ids_list, min_time, max_time)

    difficulties_list = get_difficulties_filter()

    if len(difficulties_list) > 0:
        ids_list = filter_by_difficulty(ids_list, difficulties_list)

    return ids_list


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


@app.route("/", methods=["POST", "GET"])
def search_recipes():
    """
    renders home/search page. Shows all recipes 
    matching the user's filters. Otherwise shows 
    all recipes in database. Recipes sorted by avg score 
    """
    categories = get_all_categories_from_table()
    ingredients = get_all_ingredients_from_table()
    filtered_search = False

    if request.method == "POST":
        ids_list = get_ids_that_match_all_filters()
        filtered_search = True

    else:
        ids_list = get_list_of_recipe_ids()

    recipes_list = get_sorted_recipes_list(ids_list)
    return render_template("index.html", filtered_search=filtered_search,
                           categories=categories, ingredients=ingredients, recipes_list=recipes_list)


"""

INTERACTING WITH MYSQL
"""


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


@app.route("/addrecipe", methods=["POST", "GET"])
@login_required
def add_recipe():
    """
    renders the add recipe page. If the user 
    submits a recipe, adds the values to the appropriate 
    SQL tables
    """
    if request.method == "POST":
        values_dictionary = get_form_values()
        insert_dictionary_into_recipes_table(values_dictionary)
        recipe_id = get_last_recipe_id()
        add_to_categories_if_not_duplicate(values_dictionary["Categories"])
        add_to_ingredients_if_not_duplicate(values_dictionary["Ingredients"])
        add_to_recipe_ingredients(values_dictionary["Ingredients"], recipe_id)
        add_to_recipe_categories(values_dictionary["Categories"], recipe_id)
        return redirect("/recipe/{}".format(recipe_id))

    categories = get_all_categories_from_table()
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
        flash("You must be logged in to complete this task")
        return False


def get_userpage_values(user_id):
    """
    return a dictionary with all the values required to
    render the userpage template
    """
    dictionary = {
        "Username": get_username(user_id),
        "Favourites": get_user_favourites(user_id),
        "Recipes": get_user_recipes(user_id)
    }
    return dictionary


def check_is_current_users_userpage(userpage_user_id):
    """
    returns True if the user is on their own 
    userpage. Otherwise returns False
    """

    if not check_user_is_logged_in():
        return False

    if userpage_user_id == current_user.id:
        return True
    else:
        return False


@app.route("/userpage/<user_id>")
def userpage(user_id):
    """
    renders the userpage for the argument user id
    """
    userpage_values = get_userpage_values(user_id)
    own_page = check_is_current_users_userpage(user_id)
    return render_template("userpage.html", user=userpage_values, own_page=own_page)


@app.route("/addtofavourites/<recipe_id>")
def add_to_favourites(recipe_id):
    """
    adds the argument recipe and the current
    user's id to the UserFavourites table
    """
    user_logged_in = check_user_is_logged_in()
    if not user_logged_in:
        return redirect(url_for("login"))
    else:
        add_to_user_favourites_table(recipe_id)
        flash("Recipe added to favourites")
    return redirect(redirect_url())


def return_timedelta_full_hours(timedelta_time):
    """
    returns the number of full hours in 
    the timedelta argument 
    """

    return timedelta_time.seconds // 3600


def return_timedelta_remaining_minutes(timedelta_time):
    """
    returns the the remaining minutes from the 
    timedelta argument after subtracting the full hours
    """
    return (timedelta_time.seconds % 3600) // 60


def create_time_dictionary(recipe_dictionary):
    """
    returns a dictionaries with the hours and minutes
    for both prep and cook time
    """
    time_dictionary = {
        "PrepHours": return_timedelta_full_hours(recipe_dictionary["PrepTime"]),
        "PrepMins": return_timedelta_remaining_minutes(recipe_dictionary["PrepTime"]),
        "CookHours": return_timedelta_full_hours(recipe_dictionary["CookTime"]),
        "CookMins": return_timedelta_remaining_minutes(recipe_dictionary["CookTime"])
    }

    return time_dictionary


@app.route("/edit/<recipe_id>")
def edit_recipe(recipe_id):
    """
    renders the edit recipe page
    """
    categories = get_all_categories_from_table()
    ingredients = get_all_ingredients_from_table()
    recipe_dictionary = get_recipe_values(recipe_id)
    time_dictionary = create_time_dictionary(recipe_dictionary)
    if recipe_dictionary["ImageName"]:
        flash("Please reupload recipe image")

    return render_template("edit.html", recipe=recipe_dictionary, time_dictionary=time_dictionary,
                           categories=categories, ingredients=ingredients)


@app.route("/delete/<recipe_id>")
def delete_recipe(recipe_id):
    """
    deletes a recipe from the Recipes table, along with all
    connected data from other tables
    """
    try:
        connection = open_connection()
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
        print("ERROR: {}".format(e))

    finally:
        if connection.open:
            connection.close()

    return redirect(redirect_url())


@app.route("/recipe/<recipe_id>", methods=["GET", "POST"])
def show_recipe(recipe_id):
    """
    renders the recipe page
    """
    recipe_values = get_recipe_values(recipe_id)
    recipe_user_id = get_id_for_username(recipe_values["Username"])
    time_values = create_time_dictionary(recipe_values)
    average_review_score = get_average_review_score(recipe_values["Reviews"])

    # represents the user submitting a review score
    # adds to Reviews table
    if request.method == "POST":
        user_logged_in = check_user_is_logged_in()
        if not user_logged_in:
            return redirect(url_for("login"))
        else:
            add_user_review(recipe_id)

    return render_template("recipe.html", recipe=recipe_values, times=time_values, review_score=average_review_score,
                           recipe_id=recipe_id, user_id=recipe_user_id)


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
