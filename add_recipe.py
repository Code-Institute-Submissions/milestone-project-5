import datetime
import os
from random import choice

from flask import request
from werkzeug.utils import secure_filename  # for uploading images

from app_init import app
from helpers import check_if_string_contains_letters


def get_prep_time():
    """
    returns prep time from the form in time format.
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
    returns prep time from the form in time format
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

        except Exception:
            end_of_ingredients = True

        counter += 1

    return ingredients_dictionary_list


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
