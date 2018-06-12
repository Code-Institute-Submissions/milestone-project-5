import datetime

from flask import request

from add_recipe import get_categories_list, get_ingredients_dictionary_list
from helpers import get_average_review_score, check_if_string_contains_letters
from sql_fuctions import get_recipe_reviews, get_value_from_recipes_table, get_list_of_recipe_ids, filter_by_categories, \
    filter_by_ingredients, filter_by_difficulty, get_search_results, add_average_review_score_to_dictionary_list


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
