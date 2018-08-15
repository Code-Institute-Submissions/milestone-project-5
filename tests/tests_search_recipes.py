import datetime
import unittest
from random import sample

from flask import Flask

from add_recipe import get_categories_list
from app_init import login_manager
from searching_recipes import get_recipes_average_review_score, sort_recipe_dictionaries_by_score, \
    filter_by_review_score, get_recipes_total_time, filter_by_total_time, get_filter_ingredients, get_min_score_filter, \
    get_max_score_filter, get_min_time_filter, get_max_time_filter, get_difficulties_filter
from sql_functions import get_list_of_recipe_ids

app = Flask(__name__)
c = app.test_client()

login_manager.init_app(app)
login_manager.login_view = 'login'  # from https://stackoverflow.com/questions/33724161/flask-login-shows-401-instead-of-redirecting-to-login-view


class TestSearchRecipes(unittest.TestCase):

    def test_get_recipes_average_review_score_returns_list_of_dictionaries_length_of_argument(self):
        """
        test to check that get_recipes_average_review_score returns a list of dictionaries.
        The list of dictionaries should be the length of the argument list
        """

        recipe_ids_list = sample(get_list_of_recipe_ids(), 3)
        average_review_score_list = get_recipes_average_review_score(recipe_ids_list)
        self.assertTrue(isinstance(average_review_score_list, list))
        self.assertEqual(len(average_review_score_list), 3)
        self.assertTrue(isinstance(average_review_score_list[0], dict))
        self.assertTrue(isinstance(average_review_score_list[0]["Score"], int))

    def test_can_sort_recipes_dictionary_by_score(self):
        """
        test to check that sort_recipe_dictionaries_by_score returns
        its argument list, sorted by each dictionaries 'Score' value,
        in descending order
        """

        recipe_ids_list = get_list_of_recipe_ids()
        dictionaries_list = get_recipes_average_review_score(recipe_ids_list)

        list_sorted = True
        highest_score = 6
        for recipe_dictionary in dictionaries_list:
            if not (recipe_dictionary["Score"] <= highest_score):
                list_sorted = False
            highest_score = recipe_dictionary["Score"]
        self.assertFalse(list_sorted)

        sorted_dictionaries_list = sort_recipe_dictionaries_by_score(dictionaries_list)
        highest_score = 6
        for recipe_dictionary in sorted_dictionaries_list:
            self.assertTrue(recipe_dictionary["Score"] <= highest_score)
            highest_score = recipe_dictionary["Score"]

    def test_can_filter_by_review_score(self):
        """
        test to check that filter_by_review_score removes all
        recipes who's average review score does not fall between
        those specified in the parameters. All other recipes should
        remain
        """

        recipe_ids_list = sample(get_list_of_recipe_ids(), 8)
        average_score_dictionaries_list = get_recipes_average_review_score(recipe_ids_list)
        filtered_ids_list = filter_by_review_score(recipe_ids_list, 4, 5)

        self.assertTrue(len(recipe_ids_list) > len(filtered_ids_list))

        for recipe in average_score_dictionaries_list:
            if recipe["Id"] in filtered_ids_list:
                self.assertTrue((recipe["Score"] >= 4) or (recipe["Score"] <= 5))
            else:
                self.assertTrue(recipe["Score"] <= 4)

    def test_can_get_total_time_of_recipes(self):
        """
        test to check that get_recipes_total_time returns
        a list of dictionaries. Each dictionary should have
        'Id' and 'Time' values. The time value should be a
        timedelta variable
        """

        recipes_ids_list = sample(get_list_of_recipe_ids(), 3)
        total_time_list = get_recipes_total_time(recipes_ids_list)
        self.assertTrue(isinstance(total_time_list, list))
        self.assertTrue(isinstance(total_time_list[0], dict))

        for i in range(len(recipes_ids_list)):
            self.assertEqual(recipes_ids_list[i], total_time_list[i]["Id"])
            self.assertTrue(isinstance(total_time_list[i]["Time"], datetime.timedelta))

    def test_can_filter_by_total_time(self):
        """
        test to check that filter_by_total_score returns
        a list that is shorter than its argument list
        """

        min_time = datetime.datetime.strptime('{0}:{1}'.format(1, 20), '%H:%M').time()
        max_time = datetime.datetime.strptime('{0}:{1}'.format(4, 0), '%H:%M').time()

        recipe_ids_list = get_list_of_recipe_ids()
        filtered_ids_list = filter_by_total_time(recipe_ids_list, min_time, max_time)

        self.assertTrue(len(recipe_ids_list) > len(filtered_ids_list))

    def test_can_get_filter_form_values(self):
        """
        test to check that the functions in search_recipes.py can
        accurately retrieve the filter values used in the home page
        recipes search
        """

        with c:
            filter_data = {"category-0": "Sweet", "category-1": "German", "ingredient-0": "Mustard",
                           "ingredient-1": "Maple Syrup", "min-score": 3, "max-score": 4, "min-hours": 3,
                           "min-mins": 20, "max-hours": 4, "max-mins": 30, "difficulties-filter": [0, 2]}

            c.post("/", data=filter_data)

            categories_list = get_categories_list()
            self.assertTrue(isinstance(categories_list, list))
            self.assertTrue("Sweet" in categories_list)
            self.assertTrue("German" in categories_list)

            ingredients_list = get_filter_ingredients()
            self.assertTrue(isinstance(ingredients_list, list))
            self.assertTrue("Mustard" in ingredients_list)
            self.assertTrue("Maple syrup" in ingredients_list)

            min_score = get_min_score_filter()
            max_score = get_max_score_filter()
            self.assertEqual(min_score, '3')
            self.assertEqual(max_score, '4')

            min_time = get_min_time_filter()
            max_time = get_max_time_filter()
            self.assertTrue(isinstance(min_time, datetime.time))
            self.assertTrue(isinstance(max_time, datetime.time))
            self.assertEqual(str(min_time), "03:20:00")
            self.assertEqual(str(max_time), "04:30:00")

            difficulties_filter = get_difficulties_filter()
            self.assertTrue(isinstance(difficulties_filter, list))
            self.assertTrue("0" in difficulties_filter)
            self.assertTrue("2" in difficulties_filter)
