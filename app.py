import os
from flask import render_template, request, redirect, flash, url_for
from flask_login import UserMixin, login_user, \
    login_required, current_user, logout_user  # informed by: https://www.youtube.com/watch?v=2dEM-s3mRLE

from add_recipe import get_form_values
from app_init import app, login_manager
from helpers import get_average_review_score, redirect_url, \
    create_time_dictionary
from searching_recipes import get_ids_that_match_all_filters, get_sorted_recipes_list
from sql_fuctions import open_connection_if_not_already_open, close_connection_if_open, get_username_for_id, get_id_for_username, add_form_values_to_users, \
    check_if_username_exists, check_password_correct, get_value_from_recipes_table, get_recipe_categories, \
    get_recipe_ingredients, get_recipe_reviews, get_all_categories_from_table, \
    get_all_ingredients_from_table, get_list_of_recipe_ids, get_last_recipe_id, add_to_categories_if_not_duplicate, \
    add_to_ingredients_if_not_duplicate, add_to_recipe_ingredients, add_to_recipe_categories, add_user_review, \
    add_to_user_favourites_table, get_username, get_user_favourites, get_user_recipes, \
    get_converted_difficulty, insert_dictionary_into_recipes_table, get_recipe_values, get_recipe_user, update_recipe

app.secret_key = 'some_secret'

login_manager.init_app(app)
login_manager.login_view = 'login'  # from https://stackoverflow.com/questions/33724161/flask-login-shows-401-instead-of-redirecting-to-login-view



# from: http://flask.pocoo.org/docs/1.0/patterns/fileuploads/
UPLOAD_FOLDER = 'static/images'
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

connection = open_connection_if_not_already_open()

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
    User class. Code partly from:
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
            close_connection_if_open()
            error_message = "ERROR. Username can't be more than 15 characters"
            return render_template("register.html", error=error_message)

        if not already_exists:
            add_form_values_to_users()
            flash("You have successfully registered your account")
            flash("Please login now")
            close_connection_if_open()
            return redirect(url_for("login"))


        else:
            close_connection_if_open()
            error_message = "ERROR: Username already exists. Please try a different username"
            return render_template("register.html", error=error_message)

    return render_template("register.html")


def check_user_is_logged_in():
    """
    return True if the user is logged in.
    Returns False otherwise
    """
    if current_user.is_authenticated:
        return True
    else:
        flash("You must be logged in to complete this task")
        return False



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
            close_connection_if_open()
            return render_template("login.html", error=error)

        correct_password = check_password_correct(username, password)
        if not correct_password:
            error = "ERROR: Password incorrect"
            close_connection_if_open()
            return render_template("login.html", error=error)

        user_id = get_id_for_username(username)
        user = User(user_id, username)
        login_user(user)
        flash("Successfully logged in")
        close_connection_if_open()
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
    close_connection_if_open()
    flash("Successfully logged out")
    return redirect(url_for("search_recipes"))



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
    close_connection_if_open()
    return render_template("visualizedata.html", imported_data=data)


"""
INDEX/SEARCH PAGE
"""


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
    close_connection_if_open()
    return render_template("index.html", filtered_search=filtered_search,
                           categories=categories, ingredients=ingredients, recipes_list=recipes_list)


"""
ADD RECIPE PAGE
"""


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
        close_connection_if_open()
        return redirect("/recipe/{}".format(recipe_id))

    categories = get_all_categories_from_table()
    ingredients = get_all_ingredients_from_table()
    close_connection_if_open()
    return render_template("addrecipe.html", categories=categories, ingredients=ingredients)


"""
USERPAGE
"""

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
    close_connection_if_open()
    return render_template("userpage.html", user=userpage_values, own_page=own_page)


"""
EDIT AND DELETE RECIPES 
"""
@app.route("/edit/<recipe_id>", methods=["POST", "GET"])
@login_required
def edit_recipe(recipe_id):
    """
    renders the edit recipe page if the 
    current user is the user who submitted the
    recipe. Otherwise redirects to home page
    """
    
    recipe_user = get_recipe_user(recipe_id)
    if recipe_user == current_user.username[0]:
        if request.method == "POST":
            update_recipe(recipe_id)
            return redirect("/recipe/{}".format(recipe_id))
    
        
        categories = get_all_categories_from_table()
        ingredients = get_all_ingredients_from_table()
        recipe_dictionary = get_recipe_values(recipe_id)
        time_dictionary = create_time_dictionary(recipe_dictionary)
        if recipe_dictionary["ImageName"]:
            flash("Please reupload recipe image")
    
        close_connection_if_open()
        return render_template("edit.html", recipe=recipe_dictionary, time_dictionary=time_dictionary,
                               categories=categories, ingredients=ingredients)
    else:
        return redirect(url_for("search_recipes"))
        
@app.route("/delete/<recipe_id>")
@login_required
def delete_recipe(recipe_id):
    """
    deletes a recipe from the Recipes table, along with all
    connected data from other tables. Only possible if the 
    current user is the user who submitted the recipe. Otherwise
    returns home 
    """
    recipe_user = get_recipe_user(recipe_id)
    if recipe_user == current_user.username[0]:
        try:
            connection = open_connection_if_not_already_open()
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
            close_connection_if_open()
    
        return redirect(redirect_url())
    else:
        return redirect(url_for("search_recipes"))


"""
RECIPE PAGE
"""
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
            close_connection_if_open()
            return redirect(url_for("login"))
        else:
            add_user_review(recipe_id)
            
    close_connection_if_open()
    return render_template("recipe.html", recipe=recipe_values, times=time_values, review_score=average_review_score,
                           recipe_id=recipe_id, user_id=recipe_user_id)


@app.route("/addtofavourites/<recipe_id>")
def add_to_favourites(recipe_id):
    """
    adds the argument recipe and the current
    user's id to the UserFavourites table
    """
    user_logged_in = check_user_is_logged_in()
    if not user_logged_in:
        close_connection_if_open()
        return redirect(url_for("login"))
    else:
        add_to_user_favourites_table(recipe_id)
        flash("Recipe added to favourites")
    close_connection_if_open()
    return redirect(redirect_url())



if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
