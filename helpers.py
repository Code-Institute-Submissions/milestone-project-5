from flask import request, url_for
from flask_login import current_user

from sql_fuctions import get_recipe_reviews, get_value_from_recipes_table


def convert_list_to_string_for_sql_search(argument_list):
    """
    converts argument list into a string correctly formatted
    to be inserted into an SQL query
    """
    list_as_string = "{}".format(argument_list)
    formatted_string = list_as_string.replace("[", "(").replace("]", ")").replace("{", "(").replace("}", ")")

    return formatted_string


def add_average_review_score_to_dictionary_list(recipe_dictionary_list):
    """
    adds a 'Score' key/value pair to each dictionarinary in the
    argument list. This represents the average review score
    """

    for recipe in recipe_dictionary_list:
        recipe["Score"] = int(get_average_review_score(get_recipe_reviews(recipe["Id"])))

    return recipe_dictionary_list


def get_average_review_score(list_of_scores):
    """
    returns the average of all values in the argument,
    rounded to the nearest int
    """
    length_of_list = len(list_of_scores)
    if length_of_list == 0:
        return 0
    sum_count = 0
    for score in list_of_scores:
        sum_count += score

    average_of_scores = int((sum_count / length_of_list) + 0.5)

    return average_of_scores


def redirect_url(default='/'):
    """
    to enable request.referrer. Code
    from: http://flask.pocoo.org/docs/1.0/reqcontext/
    """
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)


def check_if_string_contains_letters(string):
    """
    returns True if the string contains a letter,
    otherwise returns False
    """

    lower_string = string.lower()
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
               'v', 'w', 'x', 'y', 'z']
    for letter in lower_string:
        if letter in letters:
            return True

    return False


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


def create_recipe_values_without_image(values_dictionary):
    """
    creates values to use in SQL query for adding a
    new recipe for a recipes table, if the user did NOT
    submit an image
    """
    values = '("{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}")'.format(
        values_dictionary["Name"],
        current_user.id,
        values_dictionary["Difficulty"],
        values_dictionary["Serves"],
        values_dictionary["Blurb"],
        values_dictionary["PrepTime"],
        values_dictionary["CookTime"],
        values_dictionary["Instructions"])

    return values


def create_recipe_values_with_image(values_dictionary):
    """
    creates values to use in SQL query for adding a
    new recipe for a recipes table, if the user did submit
    an image
    """

    values = '("{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}", "{8}")'.format(
        values_dictionary["Name"],
        current_user.id,
        values_dictionary["ImageName"],
        values_dictionary["Difficulty"],
        values_dictionary["Serves"],
        values_dictionary["Blurb"],
        values_dictionary["PrepTime"],
        values_dictionary["CookTime"],
        values_dictionary["Instructions"])

    return values
