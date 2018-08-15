import datetime
import unittest

from flask import Flask

from add_recipe import get_prep_time, get_cook_time, get_categories_list, get_ingredients_dictionary_list, \
    get_form_values
from app_init import login_manager
from helpers import convert_list_to_string_for_sql_search
from sql_functions import get_last_recipe_id, open_connection_if_not_already_open

app = Flask(__name__)
c = app.test_client()

login_manager.init_app(app)
login_manager.login_view = 'login'  # from https://stackoverflow.com/questions/33724161/flask-login-shows-401-instead-of-redirecting-to-login-view


class TestAddRecipe(unittest.TestCase):

    def test_get_prep_and_cook_time_returns_time_value_from_form(self):
        """
        test to check that get_prep_time and get_cook_time
        returns the prep_time/cook_time in the post request
        form as a time object. String should be formatted
        as %H:%M:%S
        """

        with c:
            # login required to add recipe
            login_data = {"login-username": "Paddywc", "password": "Password"}
            c.post("/login", data=login_data, follow_redirects=False)

            form_data = {"prep-hours": 2, "prep-mins": 30, "cook-hours": 1, "cook-mins": 15,
                         "recipe-name": "Test Times", "difficulty-select": "1", "serves": 2, "category-0": "German",
                         "quantity-0": "1 Teaspoon", "ingredient-0": "Pepper", "instruction-1": "test instruction",
                         "blurb": "test blurb"}

            c.post("/addrecipe", data=form_data)

            prep_time = get_prep_time()
            self.assertTrue(isinstance(prep_time, datetime.time))
            self.assertEqual(str(prep_time), "02:30:00")

            cook_time = get_cook_time()
            self.assertTrue(isinstance(cook_time, datetime.time))
            self.assertEqual(str(cook_time), "01:15:00")

            # Deletes test values
            recipe_id = get_last_recipe_id()
            c.get("/delete/{}".format(recipe_id))

    def test_get_categories_list_returns_list_of_all_form_categories(self):
        """
        rest to check that get_categories list returns a list of all
        categories in the post request form
        """

        with c:
            # login required to add recipe
            login_data = {"login-username": "Paddywc", "password": "Password"}
            c.post("/login", data=login_data, follow_redirects=False)

            form_data = {"prep-hours": 2, "prep-mins": 30, "cook-hours": 1, "cook-mins": 15,
                         "recipe-name": "Test Categories List", "difficulty-select": "1", "serves": 2,
                         "category-0": "German", "category-1": "Family and Kids", "category-2": "Sweet",
                         "quantity-0": "1 Teaspoon", "ingredient-0": "Pepper", "instruction-1": "test instruction",
                         "blurb": "test blurb"}

            c.post("/addrecipe", data=form_data)

            categories_list = get_categories_list()
            self.assertTrue(isinstance(categories_list, list))
            self.assertEqual(len(categories_list), 3)
            self.assertTrue("Sweet" in categories_list)
            self.assertTrue("Family and Kids" in categories_list)
            self.assertTrue("German" in categories_list)

            # Deletes recipe data
            recipe_id = get_last_recipe_id()
            c.get("/delete/{}".format(recipe_id))

    def test_get_ingredients_returns_list_of_ingredient_dictionaries(self):
        """
        test to check that get_ingredients_dictionary_list returns a list
        of directories, with each dictionary having "Quantity"
        and "Name" keys. Their values should be the data posted in the form.
        Ingredient names should be capitalized
        """

        with c:
            # login required to add recipe
            login_data = {"login-username": "Paddywc", "password": "Password"}
            c.post("/login", data=login_data, follow_redirects=False)

            form_data = {"prep-hours": 2, "prep-mins": 30, "cook-hours": 1, "cook-mins": 15,
                         "recipe-name": "Test Ingredients", "difficulty-select": "1", "serves": 2,
                         "category-0": "German", "quantity-0": "1 spoon", "ingredient-0": "Maple Syrup",
                         "ingredient-1": "Mustard", "quantity-1": "1/2 cup", "instruction-1": "test instruction",
                         "blurb": "test blurb"}

            c.post("/addrecipe", data=form_data)

            ingredients_dictionary_list = get_ingredients_dictionary_list()
            self.assertTrue(isinstance(ingredients_dictionary_list, list))
            self.assertTrue(isinstance(ingredients_dictionary_list[0], dict))
            self.assertEqual(ingredients_dictionary_list[0]["Quantity"], "1 spoon")
            self.assertEqual(ingredients_dictionary_list[0]["Name"], "Maple syrup")
            self.assertEqual(ingredients_dictionary_list[1]["Quantity"], "1/2 cup")
            self.assertEqual(ingredients_dictionary_list[1]["Name"], "Mustard")

            # Deletes test values
            recipe_id = get_last_recipe_id()
            c.get("/delete/{}".format(recipe_id))

    def test_get_form_values_returns_dictionary_with_all_form_values(self):
        """
        test to check that get_form_values returns a dictionary with values for all
        data posted in the add_recipe form
        """

        with c:
            # login required to add recipe
            login_data = {"login-username": "Paddywc", "password": "Password"}
            c.post("/login", data=login_data, follow_redirects=False)

            form_data = {"prep-hours": 2, "prep-mins": 30, "cook-hours": 1, "cook-mins": 15, "recipe-name": "Test",
                         "difficulty-select": "1", "serves": 2, "category-0": "German", "quantity-0": "1 spoon",
                         "ingredient-0": "Maple Syrup", "ingredient-1": "Mustard", "quantity-1": "1/2 cup",
                         "instruction-1": "test instruction", "blurb": "test blurb"}

            c.post("/addrecipe", data=form_data)

            values_dictionary = get_form_values()
            self.assertTrue(isinstance(values_dictionary, dict))
            self.assertEqual(values_dictionary["Name"], "Test")
            self.assertEqual(values_dictionary["Difficulty"], "1")
            self.assertEqual(values_dictionary["Serves"], "2")
            self.assertEqual(values_dictionary["Blurb"], "test blurb")
            self.assertEqual(str(values_dictionary["CookTime"]), "01:15:00")
            self.assertEqual(str(values_dictionary["PrepTime"]), "02:30:00")
            self.assertTrue(isinstance(values_dictionary["Categories"], list))
            self.assertTrue(isinstance(values_dictionary["Ingredients"], list))

            # Deletes test data from tables
            connection = open_connection_if_not_already_open()
            with connection.cursor() as cursor:
                cursor.execute('SELECT Id from Recipes where Recipes.Name="TEST";')
                returned_tuples = cursor.fetchall()
                test_ids = [tup[0] for tup in returned_tuples]
                test_ids_string = convert_list_to_string_for_sql_search(test_ids)
                cursor.execute(
                    "DELETE FROM RecipeIngredients WHERE RecipeIngredients.RecipeId IN {} ; ".format(test_ids_string))
                cursor.execute(
                    "DELETE FROM RecipeCategories WHERE RecipeCategories.RecipeId IN {} ; ".format(test_ids_string))
                cursor.execute("DELETE FROM Recipes WHERE Recipes.Id IN {} ; ".format(test_ids_string))

                connection.commit()
