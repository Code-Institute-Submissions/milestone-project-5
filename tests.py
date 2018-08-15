import unittest
import requests
from flask import Flask, request, current_app
import datetime
from werkzeug.test import Client, EnvironBuilder
from werkzeug.testapp import test_app
from werkzeug.wrappers import BaseResponse
from app import app, User, get_userpage_values
from random import sample, choice
from flask_login import UserMixin, login_user, \
    login_required, current_user, logout_user  # informed by: https://www.youtube.com/watch?v=2dEM-s3mRLE
from app_init import app, login_manager

from add_recipe import get_prep_time, get_cook_time, get_categories_list, get_instructions_list, get_ingredients_dictionary_list, get_form_values, add_recipe_image_and_return_filename, get_recipe_image_filename

from sql_fuctions import open_connection_if_not_already_open, close_connection_if_open, get_username_for_id, get_id_for_username, add_form_values_to_users, \
    check_if_username_exists, check_password_correct, get_value_from_recipes_table, get_recipe_categories, \
    get_recipe_ingredients, get_recipe_reviews, get_all_categories_from_table, \
    get_all_ingredients_from_table, get_list_of_recipe_ids, get_last_recipe_id, add_to_categories_if_not_duplicate, \
    add_to_ingredients_if_not_duplicate, add_to_recipe_ingredients, add_to_recipe_categories, add_user_review, \
    add_to_user_favourites_table, get_username, get_user_favourites, get_user_recipes, \
    get_converted_difficulty, insert_dictionary_into_recipes_table, get_recipe_values, get_recipe_user, get_recipe_instructions, get_recipe_categories,  get_excluded_categories_list, get_excluded_ingredients_list, add_average_review_score_to_dictionary_list

from helpers import get_average_review_score, redirect_url, check_if_string_contains_letters, return_timedelta_full_hours, return_timedelta_remaining_minutes, convert_list_to_string_for_sql_search

from searching_recipes import get_recipes_average_review_score,  sort_recipe_dictionaries_by_score, filter_by_review_score, get_recipes_total_time, filter_by_total_time, get_filter_categories, get_filter_ingredients, get_min_score_filter, get_max_score_filter, get_min_time_filter, get_max_time_filter, get_difficulties_filter, get_ids_that_match_all_filters, get_sorted_recipes_list

from app import load_user, register_user, check_user_is_logged_in, login, logout, get_recipe_values_for_data_visualization, get_all_data_for_visualization, visualize_data, search_recipes, add_recipe, get_userpage_values, check_is_current_users_userpage, userpage, edit_recipe, delete_recipe, show_recipe, add_to_favourites
c = app.test_client()


app = Flask(__name__)

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
            #login required to add recipe   
            login_data = { "login-username": "Paddywc", "password": "Password"}
            c.post("/login", data=login_data, follow_redirects=False)
            
            form_data = {"prep-hours": 2, "prep-mins": 30, "cook-hours": 1, "cook-mins": 15, "recipe-name":  "Test Times", "difficulty-select": "1", "serves": 2, "category-0": "German", "quantity-0": "1 Teaspoon", "ingredient-0": "Pepper", "instruction-1": "test instruction", "blurb": "test blurb" }
            
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
            #login required to add recipe   
            login_data = { "login-username": "Paddywc", "password": "Password"}
            c.post("/login", data=login_data, follow_redirects=False)
            
            form_data = {"prep-hours": 2, "prep-mins": 30, "cook-hours": 1, "cook-mins": 15, "recipe-name": "Test Categories List", "difficulty-select": "1", "serves": 2, "category-0": "German", "category-1": "Family and Kids", "category-2": "Sweet", "quantity-0": "1 Teaspoon", "ingredient-0": "Pepper", "instruction-1": "test instruction", "blurb": "test blurb" }
            
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
            #login required to add recipe   
            login_data = { "login-username": "Paddywc", "password": "Password"}
            c.post("/login", data=login_data, follow_redirects=False)
            
            form_data = {"prep-hours": 2, "prep-mins": 30, "cook-hours": 1, "cook-mins": 15, "recipe-name": "Test Ingredients", "difficulty-select": "1", "serves": 2, "category-0": "German", "quantity-0": "1 spoon", "ingredient-0": "Maple Syrup", "ingredient-1": "Mustard", "quantity-1": "1/2 cup", "instruction-1": "test instruction", "blurb": "test blurb" }
            
            c.post("/addrecipe", data=form_data)
            
            ingredients_dictionary_list = get_ingredients_dictionary_list()
            self.assertTrue(isinstance(ingredients_dictionary_list, list))
            self.assertTrue(isinstance(ingredients_dictionary_list[0], dict))
            self.assertEqual(ingredients_dictionary_list[0]["Quantity"],"1 spoon" )
            self.assertEqual(ingredients_dictionary_list[0]["Name"], "Maple syrup")
            self.assertEqual(ingredients_dictionary_list[1]["Quantity"], "1/2 cup" )
            self.assertEqual(ingredients_dictionary_list[1]["Name"], "Mustard" )
            
            # Deletes test values
            recipe_id = get_last_recipe_id()
            c.get("/delete/{}".format(recipe_id))
            
    def test_get_form_values_returns_dictionary_with_all_form_values(self):
        """
        test to check that get_form_values returns a dictionary with values for all 
        data posted in the add_recipe form
        """
        
        with c:
            #login required to add recipe   
            login_data = { "login-username": "Paddywc", "password": "Password"}
            c.post("/login", data=login_data, follow_redirects=False)
            
            form_data = {"prep-hours": 2, "prep-mins": 30, "cook-hours": 1, "cook-mins": 15, "recipe-name": "Test", "difficulty-select": "1", "serves": 2, "category-0": "German", "quantity-0": "1 spoon", "ingredient-0": "Maple Syrup", "ingredient-1": "Mustard", "quantity-1": "1/2 cup", "instruction-1": "test instruction", "blurb": "test blurb" }
            
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
                cursor.execute("DELETE FROM RecipeIngredients WHERE RecipeIngredients.RecipeId IN {} ; ".format(test_ids_string)) 
                cursor.execute("DELETE FROM RecipeCategories WHERE RecipeCategories.RecipeId IN {} ; ".format(test_ids_string)) 
                cursor.execute("DELETE FROM Recipes WHERE Recipes.Id IN {} ; ".format(test_ids_string)) 
                
                connection.commit()
            

                
                
class TestHelpers(unittest.TestCase):
    
    def test_get_average_review_score_returns_average_of_argument_list(self):
        """
        test to check that get_average_review_score returns that average
        int of its argument list, rounded to the nearest int
        """
        should_be_3 = [1,2,3,4,5]
        self.assertEqual(get_average_review_score(should_be_3), 3)
        
        should_be_rounded_to_3 = [1, 3, 4]
        self.assertEqual(get_average_review_score(should_be_rounded_to_3), 3)
        
        should_be_rounded_to_1 = [1,1,2]
        self.assertEqual(get_average_review_score(should_be_rounded_to_1), 1)
        
    def test_can_check_if_string_contains_letters(self):
        """
        test to see if check_string_contains_letters returns true
        if the argument string contains letters, false otherwise
        """
        
        self.assertTrue(check_if_string_contains_letters("abc"))
        self.assertTrue(check_if_string_contains_letters("1134f3"))
        self.assertTrue(check_if_string_contains_letters("ABC"))
        self.assertFalse(check_if_string_contains_letters("223"))
        self.assertFalse(check_if_string_contains_letters("#$"))
        self.assertFalse(check_if_string_contains_letters(" "))

    def test_can_get_full_hours_and_remaining_minutes_from_timedelta_time_object(self):
        """
        test to check that return_timedelta_full_hours returns the 
        number of full hours only in the argument. return_timedelta_remaining_minutes
        should return the remaining minutes after all full hours have been subtracted 
        """
        
        three_hours_20_mins = datetime.time(3, 20)
        three_20_timedelta_object = datetime.datetime.combine(datetime.date.min, three_hours_20_mins) - datetime.datetime.min
        self.assertEqual(return_timedelta_full_hours(three_20_timedelta_object), 3)
        self.assertEqual(return_timedelta_remaining_minutes(three_20_timedelta_object), 20)
        
        five_hours_50_mins = datetime.time(5, 50)
        five_50_timedelta_object = datetime.datetime.combine(datetime.date.min, five_hours_50_mins) - datetime.datetime.min
        self.assertEqual(return_timedelta_full_hours(five_50_timedelta_object), 5)
        self.assertEqual(return_timedelta_remaining_minutes(five_50_timedelta_object), 50)
        
    
class TestSearchRecipes(unittest.TestCase):
    
    def test_get_recipes_average_review_score_returns_list_of_dictionaries_length_of_argument(self):
        """
        test to check that get_recipes_average_review_score returns a list of dictionaries.
        The list of dictionaries should be the legnth of the argument list
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
            if not (recipe_dictionary["Score"]  <= highest_score):
                list_sorted = False
            highest_score = recipe_dictionary["Score"]
        self.assertFalse(list_sorted)
        
        sorted_dictionaries_list = sort_recipe_dictionaries_by_score(dictionaries_list)
        highest_score = 6
        for recipe_dictionary in sorted_dictionaries_list:
            self.assertTrue(recipe_dictionary["Score"]<= highest_score)
            highest_score = recipe_dictionary["Score"]
            
            
    def test_can_filter_by_review_score(self):
        """
        test to check that filter_by_review_score removes all
        recipes whos average review score does not fall between
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
            self.assertEqual(recipes_ids_list[i],total_time_list[i]["Id"])
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
            filter_data = {"category-0": "Sweet", "category-1": "German", "ingredient-0": "Mustard", "ingredient-1": "Maple Syrup", "min-score": 3, "max-score" : 4, "min-hours": 3, "min-mins": 20, "max-hours": 4,  "max-mins": 30,  "difficulties-filter": [0,2]}
            
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
            
            
class TestSQLFunctions(unittest.TestCase):
    
    
    def test_can_match_id_with_username(self):
        """
        test to check that get_username_for_id returns
        the correct username for the argument id, and that
        get_id_for_username returns the correct id for 
        the argument username
        """
        
        sample_of_ids_and_usernames = [{"username" : "Paddywc", "id": 12},{"username" : "Sam", "id": 18},{"username" : "Bart", "id": 21 }, {"username": "Ben", "id": 25}]
        random_dictionary = choice(sample_of_ids_and_usernames)
        
        returned_username =  get_username_for_id(random_dictionary["id"])
        self.assertEqual(random_dictionary["username"], returned_username)
        
        returned_id = get_id_for_username(random_dictionary["username"])
        self.assertEqual(random_dictionary["id"], returned_id)
        
        
    def test_can_create_user_from_frontend(self):
        """
        test to check that add_form_values_to_users creates
        a new row in the Users table from the form values
        """
        
        with c:
            self.assertTrue(check_if_username_exists("Paddywc"))
            test_username = "testuser1919"
            self.assertFalse(check_if_username_exists("testuser1919"))
    
            form_data = {"username": test_username, "password": "MyPassword"}
            
            # incorrect url. '/register' not used because 
            # it would automatically add the user to the database
            c.post("/visualize_data", data=form_data)
            add_form_values_to_users()
            self.assertTrue(check_if_username_exists(test_username))
            
            # delete test user from database
            connection = open_connection_if_not_already_open()
            with connection.cursor() as cursor:
                cursor.execute('DELETE FROM Users WHERE Users.Username = "{}" ; '.format(test_username))
                connection.commit()
        
        
        
    def test_can_check_if_username_exists(self):
        """
        test to check that check_if_username_exists returns
        True if the username is in the Users table, False otherwise
        """
        
        should_be_true = check_if_username_exists("Lisa")
        self.assertTrue(should_be_true)
        should_be_false = check_if_username_exists("Iamnotreal")
        self.assertFalse(should_be_false)      
        
    def test_can_validate_password(self):
        """
        test to check that check_password_correct returns
        True if the password is correct, False otherwise
        """
        
        should_be_false = check_password_correct("Patrick", "WrongPassword")
        self.assertFalse(should_be_false)
        
        should_be_true = check_password_correct("Patrick", "Password")
        self.assertTrue(should_be_true)
        
    def test_can_get_values_from_recipe_table(self):
        """
        Test to check that get_value_from_recipes_table returns
        the returns the value specified in the first argument 
        for the recipe specified in the second argument
        """
        
        should_be_salad = get_value_from_recipes_table("Name", 122)
        self.assertEqual(should_be_salad, "Salad")
        
        should_be_visa_photo = get_value_from_recipes_table("ImageName", 119)
        self.assertEqual(should_be_visa_photo, "788Visa_photo.jpg")
        
        should_be_a_tin_of_baked_beans= get_value_from_recipes_table("Blurb", 127)
        self.assertEqual(should_be_a_tin_of_baked_beans, "A tin of baked beans")
        
        should_be_1_hour_20_mins = get_value_from_recipes_table("PrepTime", 106)
        self.assertEqual(str(should_be_1_hour_20_mins), "1:20:00")
        
        should_be_3_mins = get_value_from_recipes_table("CookTime", 127)
        self.assertEqual(str(should_be_3_mins), "0:03:00")
        
        should_be_1 = get_value_from_recipes_table("Serves", 127)
        self.assertEqual(should_be_1, 1)
        
    def test_can_get_recipe_user(self):
        """
        test to check that get_recipe_user returns 
        the username for the user that submitted the recipe 
        """
        
        should_be_paddywc = get_recipe_user(105)
        self.assertEqual(should_be_paddywc, "Paddywc")
        
        should_be_patrick = get_recipe_user(121)
        self.assertEqual(should_be_patrick, "Patrick")
        

            
            
    def test_can_get_recipe_instructions_and_categories(self):
        """
        test to check that get_recipe_categories returns a list
        of the names of its argument recipe's categories, and that 
        get_recipe_instructions returns a list of its argument
        recipe's instructions
        """
        should_have_2_instructions = get_recipe_instructions(106)
        self.assertTrue(isinstance(should_have_2_instructions, list))
        self.assertEqual(len(should_have_2_instructions), 2)
        self.assertEqual(str(should_have_2_instructions), "['Test Instructions', ' Second instruction']")
        
        should_have_3_categories = get_recipe_categories(104)
        self.assertTrue(isinstance(should_have_3_categories, list))
        self.assertEqual(len(should_have_3_categories), 3)
        self.assertEqual(str(should_have_3_categories), "['Indian', 'Spicy', 'Asian']")
        
    def test_can_get_recipe_ingredients(self):
        """
        test to check that get_recipe_ingredients returns a list
        of dictionaries. Each dictionary should have 'Quantity' and
        'Ingredient' value that represent the quantity and name for that 
        RecipeIngredients row
        """
        
        should_have_3_ingredients = get_recipe_ingredients(103)
        self.assertTrue(isinstance(should_have_3_ingredients, list))
        self.assertEqual(len(should_have_3_ingredients), 3)
        self.assertTrue(isinstance(should_have_3_ingredients[0], dict))
        self.assertEqual(should_have_3_ingredients[2]["Quantity"], "1/2 Tin")
        self.assertEqual(should_have_3_ingredients[2]["Ingredient"], "Marmalade ")
        
    def test_can_get_all_categories_and_ingredients_from_tables(self):
        """
        test to check that get_all_categories_from_table returns a list
        of all names in the Categories table, and that get_all_ingredients_from_table
        returns a list of all names in the Ingredients table
        """
        sample_of_ingredients = ["Coke", "Eggs", "Water"]
        all_ingredients = get_all_ingredients_from_table()
        self.assertTrue(isinstance(all_ingredients, list))
        for ingredient in sample_of_ingredients:
            self.assertTrue(ingredient in all_ingredients)
            
        sample_of_categories = ["Irish", "Side", "Cuisines"]
        all_categories = get_all_categories_from_table()
        self.assertTrue(isinstance(all_categories, list))
        for category in sample_of_categories:
            self.assertTrue(category in all_categories)
            
    def test_can_get_excluded_categories_and_ingredients(self):
        """
        test to check that get_excluded_categories_list returns
        all category Ids EXCEPT those named in the argument list, 
        and get_excluded_ingredients_list does the same for ingredients
        """
        
        all_categories_in_recipe_categories = get_excluded_categories_list(["No valid filter"])
        sample_categories = [{"Name": "Indian", "Id": 16}, {"Name": "Vegetarian", "Id":9}]
        filtered_category_ids =  get_excluded_categories_list([category["Name"] for category in sample_categories])
        self.assertEqual(len(filtered_category_ids), (len(all_categories_in_recipe_categories)-len(sample_categories)))
        for category in sample_categories:
            self.assertTrue(category["Id"] in all_categories_in_recipe_categories)
            self.assertTrue(category["Id"] not in filtered_category_ids)
            
        all_ingredients_in_recipe_ingredients = get_excluded_ingredients_list(["No valid filter"])
        sample_ingredients = [{"Name": "Butter", "Id": 6}, {"Name": "Rashers", "Id": 13}]
        filtered_ingredient_ids =  get_excluded_ingredients_list([ingredient["Name"] for ingredient in sample_ingredients])
        self.assertEqual(len(filtered_ingredient_ids), (len(all_ingredients_in_recipe_ingredients)-len(sample_ingredients)))
        for ingredient in sample_ingredients:
            self.assertTrue(ingredient["Id"] in all_ingredients_in_recipe_ingredients)
            self.assertTrue(ingredient["Id"] not in filtered_ingredient_ids)
            
    def test_can_get_last_recipe_id(self):
        """
        test to check that get_last_recipe_id returns
        the Id of the recipe that was most recently added 
        to the Recipes table
        """
        with c:
            #login required to add recipe   
            login_data = { "login-username": "Paddywc", "password": "Password"}
            c.post("/login", data=login_data, follow_redirects=False)
            
            form_data = {"prep-hours": 2, "prep-mins": 30, "cook-hours": 1, "cook-mins": 15, "recipe-name": "Test Last Id", "difficulty-select": "1", "serves": 2, "category-0": "German", "quantity-0": "1 spoon", "ingredient-0": "Maple Syrup", "ingredient-1": "Mustard", "quantity-1": "1/2 cup", "instruction-1": "test instruction", "blurb": "test blurb" }
            
            c.post("/addrecipe", data=form_data)
            
            id_retrieved_using_function = get_last_recipe_id()
            
            connection=open_connection_if_not_already_open()
            with connection.cursor() as cursor:
                cursor.execute('SELECT Id from Recipes where Recipes.Name="Test Last Id";')
                returned_tuple = cursor.fetchone()
                id_from_database = returned_tuple[0]
                
                # Deletes test values from database
                cursor.execute("DELETE FROM RecipeIngredients WHERE RecipeIngredients.RecipeId = {} ; ".format(id_from_database)) 
                cursor.execute("DELETE FROM RecipeCategories WHERE RecipeCategories.RecipeId = {} ; ".format(id_from_database)) 
                cursor.execute("DELETE FROM Recipes WHERE Recipes.Id = {} ; ".format(id_from_database)) 
                connection.commit()
            
            self.assertEqual(id_retrieved_using_function, id_from_database)
            
                
    def test_can_add_to_tables_if_not_duplicate(self):
        """
        test to check that add_to_categories_if_not duplicate
        adds the argument category names to the Categories table
        if it does not already exist, and add_to_ingredients_if_not_duplicate
        does the same for ingredients
        """
        
        categories_prior_to_function_call = get_all_categories_from_table()
        random_existing_categories = sample(categories_prior_to_function_call, 3)
        add_to_categories_if_not_duplicate(random_existing_categories)
        categories_after_function_called = get_all_categories_from_table()
        self.assertEqual(len(categories_after_function_called), len(categories_prior_to_function_call))
        
        
        new_categories = ["Not Existing", "Another test"]
        self.assertTrue((new_categories[0] not in categories_prior_to_function_call) and (new_categories[1] not in categories_prior_to_function_call))
        with_new_categories = random_existing_categories + new_categories
        add_to_categories_if_not_duplicate(with_new_categories)
        categories_after_second_function_called = get_all_categories_from_table()
        self.assertEqual(len(categories_after_second_function_called), len(categories_prior_to_function_call)+2)
        
        
        ingredients_prior_to_function_call = get_all_ingredients_from_table()
        random_existing_ingredients = sample(ingredients_prior_to_function_call, 3)
        existing_ingredients_dictionary_list = [{"Name": ingredient} for ingredient in random_existing_ingredients]
        add_to_ingredients_if_not_duplicate(existing_ingredients_dictionary_list)
        ingredients_after_function_called = get_all_ingredients_from_table()
        self.assertEqual(len(ingredients_after_function_called), len(ingredients_prior_to_function_call))
        
        
        new_ingredients = [{"Name": "Not Existing"}, {"Name": "Another test"}]
        self.assertTrue((new_ingredients[0]["Name"] not in ingredients_prior_to_function_call) and (new_ingredients[1] not in ingredients_prior_to_function_call))
        with_new_ingredients = existing_ingredients_dictionary_list + new_ingredients
        add_to_ingredients_if_not_duplicate(with_new_ingredients)
        ingredients_after_second_function_called = get_all_ingredients_from_table()
        self.assertEqual(len(ingredients_after_second_function_called), len(ingredients_prior_to_function_call)+2)
        
        # Delete test values from tables
        test_values_string = convert_list_to_string_for_sql_search(new_categories)
        connection = open_connection_if_not_already_open()
        with connection.cursor() as cursor:
                cursor.execute("DELETE FROM Ingredients WHERE Name IN {} ; ".format(test_values_string)) 
                cursor.execute("DELETE FROM Categories WHERE Name IN {} ; ".format(test_values_string)) 
                connection.commit()
        
        close_connection_if_open()
    
    
    def test_can_add_to_recpie_categories(self):
        """
        test to check that add_to_recipe_categories adds its argument
        list of category ids to the RecipeIngredients table
        """
        
        random_recipe_id = choice(get_list_of_recipe_ids())
        
        test_categories_list = ["Test1", "Test2", "Test3"]
        original_recipe_categories = get_recipe_categories(random_recipe_id)
        for category in test_categories_list:
            self.assertFalse(category in original_recipe_categories)
            
        add_to_categories_if_not_duplicate(test_categories_list)
        add_to_recipe_categories(test_categories_list, random_recipe_id)
        
        new_recipe_categories = get_recipe_categories(random_recipe_id)
        self.assertEqual(len(original_recipe_categories)+3, len(new_recipe_categories))
        for category in test_categories_list:
            self.assertTrue(category in new_recipe_categories)
            
        # deletes test values from database
        connection = open_connection_if_not_already_open()
        test_categories_string =  convert_list_to_string_for_sql_search(test_categories_list)
        with connection.cursor() as cursor:
            cursor.execute("SELECT Id FROM Categories WHERE Name IN {} ;".format(test_categories_string))
            returned_tuples = cursor.fetchall()
            returned_ids = [returned_tuple[0] for returned_tuple in returned_tuples]
            returned_ids_string = convert_list_to_string_for_sql_search(returned_ids)
            cursor.execute("DELETE FROM Categories WHERE Id IN {} ;".format(returned_ids_string))
            cursor.execute("DELETE FROM RecipeCategories WHERE CategoryId IN {} ;".format(returned_ids_string))
            connection.commit()
        
    
        
    def test_can_add_to_recpie_ingredients(self):
        """
        test to check that add_to_recipe_ingredients adds its argument
        dictionary list to the RecipeIngredients table. Each dictionary
        features value for the ingredient name and quantity. The ingredient
        name is converted to the matching ingredient id from the Ingredients 
        table
        """
        
        random_recipe_id = choice(get_list_of_recipe_ids())
        
        test_ingredients_dictionary_list = [{"Name": "Test1", "Quantity" : "1 Test"}, {"Name":"Test2", "Quantity" : "2 Test"}, { "Name": "Test3" ,"Quantity":"3 Test"}, { "Name": "Test4" ,"Quantity":"4 Test"}]
        original_recipe_ingredients= get_recipe_ingredients(random_recipe_id)
        for ingredient in test_ingredients_dictionary_list:
            self.assertFalse(ingredient["Name"] in [ingredient["Ingredient"] for ingredient in original_recipe_ingredients] )
            self.assertFalse(ingredient["Quantity"] in [ingredient["Quantity"] for ingredient in original_recipe_ingredients] )
            
        add_to_ingredients_if_not_duplicate(test_ingredients_dictionary_list)
        add_to_recipe_ingredients(test_ingredients_dictionary_list, random_recipe_id)
        
        new_recipe_ingredients = get_recipe_ingredients(random_recipe_id)
        self.assertEqual(len(original_recipe_ingredients)+4, len(new_recipe_ingredients))
        for ingredient in test_ingredients_dictionary_list:
            self.assertTrue(ingredient["Name"] in [ingredient["Ingredient"] for ingredient in new_recipe_ingredients] )
            self.assertTrue(ingredient["Quantity"] in [ingredient["Quantity"] for ingredient in new_recipe_ingredients] )
            
        # deletes test values from database
        connection = open_connection_if_not_already_open()
        ingredient_name_list =  [ingredient["Name"] for ingredient in test_ingredients_dictionary_list]
        ingredient_name_string = convert_list_to_string_for_sql_search(ingredient_name_list)
        with connection.cursor() as cursor:
            cursor.execute("SELECT Id FROM Ingredients WHERE Name IN {} ;".format(ingredient_name_string))
            returned_tuples = cursor.fetchall()
            returned_ids = [returned_tuple[0] for returned_tuple in returned_tuples]
            returned_ids_string = convert_list_to_string_for_sql_search(returned_ids)
            cursor.execute("DELETE FROM Ingredients WHERE Id IN {} ;".format(returned_ids_string))
            cursor.execute("DELETE FROM RecipeIngredients WHERE IngredientId IN {} ;".format(returned_ids_string))
            connection.commit()
        
    
    
    def test_can_add_user_review(self):
        """
        test to check that add_user_review adds the value
        posted on the recipe.html form to the Reviews table.
        The UserId should be the Id of the active user if the 
        user is not logged in. No data should be added if 
        the user is not logged in. Will delete any existing 
        reviews of that recipe from that user
        """
        with c:
            
            connection = open_connection_if_not_already_open()
            with connection.cursor() as cursor:
                cursor.execute("SELECT RecipeId FROM Reviews WHERE UserId = 12")
                returned_tuples = cursor.fetchall()
                ids_of_recipes_user_has_already_reviewed = [tup[0] for tup in returned_tuples]
                
            all_recipe_ids = get_list_of_recipe_ids()
            ids_of_recipes_user_has_already_reviewed = [recipe_id for recipe_id in all_recipe_ids if recipe_id not in ids_of_recipes_user_has_already_reviewed]
            random_recipe_id =  choice(ids_of_recipes_user_has_already_reviewed)
            review_score = {"user-review": "6"}
            
            c.get("/logout")
            c.post("/recipe/{}".format(random_recipe_id), data=review_score, follow_redirects=False)
            recipe_reviews = get_recipe_reviews(random_recipe_id)
            self.assertFalse(6 in recipe_reviews)
            
            login_data = { "login-username": "Paddywc", "password": "Password"}
            c.post("/login", data=login_data, follow_redirects=False)
            c.post("/recipe/{}".format(random_recipe_id), data=review_score)
            recipe_reviews = get_recipe_reviews(random_recipe_id)
            self.assertTrue(6 in recipe_reviews)
            
            # deletes test values from database
            connection = open_connection_if_not_already_open()
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM Reviews WHERE Score = 6")
                connection.commit()
                
    def test_can_add_user_favorites(self):
        """
        test to check that add_to_user_favourites_table
        adds the recipe in the url to the UserFavourites
        table. The UserId should be the Id of the active
        user. If there is already a row in UserFavourites
        with that RecipeId and UserId, that row should
        be deleted
        """
        with c:
            login_data = { "login-username": "Patrick", "password": "Password"}
            c.post("/login", data=login_data, follow_redirects=False)
            existing_user_favorites = get_user_favourites(14)
            existing_favorites_id_list = [recipe["Id"] for recipe in existing_user_favorites]
            random_existing_favorite_id = choice(existing_favorites_id_list)
            
            c.get("/addtofavourites/{}".format(random_existing_favorite_id))
            new_user_favorites = get_user_favourites(14)
            self.assertEqual(len(new_user_favorites), len(existing_user_favorites))
            
            all_recipe_ids = get_list_of_recipe_ids()
            ids_of_recipes_that_user_has_not_favorited= [recipe_id for recipe_id in all_recipe_ids if recipe_id not in existing_favorites_id_list]
            random_new_recipe_id = choice(ids_of_recipes_that_user_has_not_favorited)
            
            c.get("/addtofavourites/{}".format(random_new_recipe_id))
            new_user_favorites = get_user_favourites(14)
            self.assertEqual(len(new_user_favorites), len(existing_user_favorites)+1)
            
            
            # deletes test values from database
            connection = open_connection_if_not_already_open()
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM UserFavourites WHERE RecipeId = {} AND UserId = 14 ".format(random_new_recipe_id))
                connection.commit()
                
                
    def test_can_get_average_review_score_from_dictionary_with_recipe_id(self):
        """
        test to check that add_average_review_score_to_dictionary_list adds a 'Score'
        value to each dictionary in the argument list. This value should be the average of all
        Score values from rows in the Reviews table whose RecipeId value matches
        the Id value of the argument dictionary
        """
        
        with c:
            login_data = { "login-username": "Paddywc", "password": "Password"}
            c.post("/login", data=login_data, follow_redirects=False)
            new_recipe_data = {"prep-hours": 5, "prep-mins": 30, "cook-hours": 1, "cook-mins": 15, "recipe-name": "Test Avg Review Score", "difficulty-select": "1", "serves": 2, "category-0": "German", "quantity-0": "1 Teaspoon", "ingredient-0": "Pepper", "instruction-1": "test instruction", "blurb": "test blurb"}
            c.post("/addrecipe", data=new_recipe_data)
            id_of_new_recipe = get_last_recipe_id()
            populate_reviews_avg_of_4 = [{"UserId": 15, "Score": 5 }, {"UserId": 28, "Score": 3 }, {"UserId": 17, "Score": 4 }]
            
            connection = open_connection_if_not_already_open()
            with connection.cursor() as cursor:
                for user in populate_reviews_avg_of_4:
                    cursor.execute('INSERT INTO Reviews(UserId, Score, RecipeId) VALUES ("{0}", "{1}", "{2}");'.format(user["UserId"], user["Score"], id_of_new_recipe))
                connection.commit()
            
            dictionary_with_recipe_id = {"Id": id_of_new_recipe}
            dictionary_with_id_and_avg_score = add_average_review_score_to_dictionary_list([dictionary_with_recipe_id])[0]
            
            self.assertEqual(dictionary_with_id_and_avg_score["Id"], id_of_new_recipe)
            self.assertEqual(dictionary_with_id_and_avg_score["Score"], 4)
            
            # Deletes test data from tables
            connection = open_connection_if_not_already_open()
            with connection.cursor() as cursor:
                cursor.execute('SELECT Id from Recipes where Recipes.Name="Test Avg Review Score";')
                returned_tuple = cursor.fetchone()
                id_from_database = returned_tuple[0]
                cursor.execute('DELETE FROM RecipeIngredients WHERE RecipeIngredients.RecipeId = "{}" ; '.format(id_from_database)) 
                cursor.execute('DELETE FROM RecipeCategories WHERE RecipeCategories.RecipeId = "{}" ; '.format(id_from_database)) 
                cursor.execute('DELETE FROM Reviews WHERE Reviews.RecipeId = "{}" ; '.format(id_from_database)) 
                cursor.execute('DELETE FROM Recipes WHERE Recipes.Id = "{}"; '.format(id_from_database)) 
                connection.commit()
            
                
    def test_can_insert_into_and_retrieve_from_recipes_table(self):
        """
        test to check that insert_dictionary_into_recipes_table adds
        the values from its argument dictionary into the Recipes table,
        and that get_recipe_values retrieves these values
        """
        
        with c:
            
            login_data = { "login-username": "Patrick", "password": "Password"}
            c.post("/login", data=login_data, follow_redirects=False)
            
            new_recipe_data = {"prep-hours": 1, "prep-mins": 30, "cook-hours": 4, "cook-mins": 30, "recipe-name": "Test Inserting", "difficulty-select": "2", "serves": 2, "category-0": "Breakfast", "quantity-0": "1/2 Cup", "ingredient-0": "Pepper", "instruction-1": "Test instruction 1", "blurb": "this is a test"}
            # invalid link for adding recipe
            # used to retrieve post data without adding recipe values to dictionary
            c.post("/visualizedata", data=new_recipe_data)
            recipe_dictionary = get_form_values()
            recipe_dictionary["UserId"] = 14
            insert_dictionary_into_recipes_table(recipe_dictionary)
            
            recipe_id = get_last_recipe_id()
            retrieved_recipe_values = get_recipe_values(recipe_id)
            self.assertTrue(isinstance(retrieved_recipe_values, dict))
            self.assertEqual(retrieved_recipe_values["Name"], "Test Inserting")
            self.assertEqual(retrieved_recipe_values["Difficulty"], "Challenging")
            self.assertEqual(retrieved_recipe_values["Serves"], 2)
            self.assertEqual(retrieved_recipe_values["Blurb"], "this is a test")
            self.assertEqual(str(retrieved_recipe_values["CookTime"]), "4:30:00")
            self.assertEqual(str(retrieved_recipe_values["PrepTime"]), "1:30:00")
            self.assertTrue(isinstance(retrieved_recipe_values["Categories"], list))
            self.assertTrue(isinstance(retrieved_recipe_values["Ingredients"], list))
            self.assertTrue(isinstance(retrieved_recipe_values["Instructions"], list))
            self.assertEqual(retrieved_recipe_values["Instructions"][0],"Test instruction 1")
            
            # Tests values were only added to Recipess table
            # and not RecipeCategories and RecipesIngredients tables
            self.assertEqual(len(retrieved_recipe_values["Categories"]), 0)
            self.assertEqual(len(retrieved_recipe_values["Ingredients"]), 0)
            
            # Deletes test data from tables
            connection = open_connection_if_not_already_open()
            with connection.cursor() as cursor:
                cursor.execute('DELETE FROM Recipes WHERE Name = "{}"; '.format("Test Inserting")) 
                connection.commit()
            
            
            
class TestApp(unittest.TestCase):
    
        
    def test_can_register_user(self):
        """
        Test to check that website visitors can 
        create a new row in the Users table from 
        the frontend form
        """
        
        with c:
            test_username = "Reg User Test"
            username_exists = check_if_username_exists(test_username)
            self.assertFalse(username_exists)
            
            form_data = {"username": test_username, "password": "Password"}
            c.post("/register", data=form_data)
            username_exists = check_if_username_exists(test_username)
            self.assertTrue(username_exists)
            
            # delete test user from database
            connection = open_connection_if_not_already_open()
            with connection.cursor() as cursor:
                cursor.execute('DELETE FROM Users WHERE Users.Username = "{}" ; '.format(test_username))
                connection.commit()
        
        
    def test_can_check_if_user_is_logged_in(self):
        """
        test to check that check_user_is_logged_in 
        returns True if there if the active user is 
        logged in, False otherwise
        """
        
        with c:
            login_data = { "login-username": "Cremen", "password": "Password"}
            c.post("/login", data=login_data, follow_redirects=False)
            self.assertTrue(check_user_is_logged_in())
            
            c.get("/logout")
            self.assertFalse(check_user_is_logged_in())
            
    def test_get_login_page(self):
        """
        test to check that the login page returns 
        a response code of 200 and uses the login.html
        template
        """
        
        with c:
            response = c.get("/login")
            self.assertEqual(response.status_code, 200)
            self.assertTrue(b'<h1 class="login-header">Login</h1>' in response.data)
            
    def test_get_register_page(self):
        """
        test to check that the register page returns 
        a response code of 200 and uses the register.html
        template
        """
        
        with c:
            response = c.get("/register")
            self.assertEqual(response.status_code, 200)
            self.assertTrue(b'<h1 class="register-header">Register</h1>' in response.data)
            
    def test_can_get_values_for_data_visualization(self):
        """
        test to check that get_recipe_values_for_data_visualization
        returns a dictionary with accurate values for that recipe
        specified in the argument. Note that get_recipe_values 
        and get_average_review_score are tested in their appropriate
        test files, and it is assumed here that they function correctly
        """
        
        random_recipe_id = choice(get_list_of_recipe_ids())
        values_using_get_recipe = get_recipe_values(random_recipe_id)
        values_using_get_data_vis = get_recipe_values_for_data_visualization(random_recipe_id)
        
        self.assertEqual(values_using_get_recipe["Name"], values_using_get_data_vis["Name"])
        self.assertEqual(values_using_get_recipe["Categories"], values_using_get_data_vis["Categories"])
        self.assertEqual(values_using_get_recipe["Difficulty"], values_using_get_data_vis["Difficulty"])
        self.assertEqual(values_using_get_recipe["Serves"], values_using_get_data_vis["Serves"])
        self.assertEqual(values_using_get_recipe["Ingredients"], values_using_get_data_vis["Ingredients"])
        recipe_reviews = values_using_get_recipe["Reviews"]
        average_rating = get_average_review_score(recipe_reviews)
        self.assertEqual(average_rating, values_using_get_data_vis["Rating"])
        
    def test_get_all_data_for_visualization_returns_list_of_dictionary_length_of_recipes_table(self):
        """
        Test to check that get_all_data_for_visualization returns a list
        dictionaries. The list length should equal the number of rows
        in the Recipes table
        """
        
        data = get_all_data_for_visualization()
        self.assertTrue(isinstance(data, list))
        self.assertTrue(isinstance(data[0], dict))
        
        connection = open_connection_if_not_already_open()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Recipes;")
            returned_tuples_list = cursor.fetchall()
            
        self.assertEqual(len(data), len(returned_tuples_list))
        
    def test_get_visualize_data_page(self):
        """
        test to check that the visualize_data page returns 
        a response code of 200 and uses the visualizedata.html
        template
        """
        
        with c:
            response = c.get("/visualizedata")
            self.assertEqual(response.status_code, 200)
            self.assertTrue(b'<h1 id="visualize-data-header">Recipes Data:</h1>' in response.data)
    
    def test_get_search_recipes_page(self):
        """
        test to check that the search_recipes page returns 
        a response code of 200 and uses the index.html
        template
        """
        
        with c:
            response = c.get("/")
            self.assertEqual(response.status_code, 200)
            self.assertTrue(b'<h2 class="search-header">' in response.data)
            
    def test_add_recipe_page(self):
        """
        test to check that the search_recipes page returns 
        a response code of 200 and uses the index.html
        template. If the user is not logged in, they should 
        be redirected to the login page
        """
        
        with c:
            c.get("/logout")
            response = c.get("/addrecipe", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(b'<h1 class="login-header">Login</h1>' in response.data)
            
            login_data = { "login-username": "Paddywc", "password": "Password"}
            c.post("/login", data=login_data, follow_redirects=False)
            response = c.get("/addrecipe", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(b'<h1 class="add-recipe-header">Add Recipe</h1>' in response.data)
            
    def test_get_userpage(self):
        """
        test to check that a userpage get request
        returns  a response code of 200 and uses the
        userpage.html template
        """
        
        with c:
            
            response = c.get("/userpage/12")
            self.assertEqual(response.status_code, 200)
            self.assertTrue(b'<h1 id="userpage-header">' in response.data)
            
    def test_can_check_if_is_current_users_userpage(self):
        """
        test to check that check_is_current_users_userpage 
        returns True if the argument id matches the id of 
        the current user, False otherwise
        """
        
        with c:
            login_data = { "login-username": "Paddywc", "password": "Password"}
            c.post("/login", data=login_data, follow_redirects=False)
            self.assertTrue(check_is_current_users_userpage(12))
            self.assertFalse(check_is_current_users_userpage(13))
            
    def test_user_can_delete_their_recipe(self):
        """
        test to check that a user can delete their own recipe
        using the frontend url. A user should not be able
        to delete a recipe submitted by a different user
        """
        with c:
            login_data = { "login-username": "Paddywc", "password": "Password"}
            c.post("/login", data=login_data, follow_redirects=False)
                
            recipe_data = {"prep-hours": 2, "prep-mins": 30, "cook-hours": 1, "cook-mins": 15, "recipe-name": "Test Delete", "difficulty-select": "1", "serves": 4, "category-0": "German", "quantity-0": "1 Cup", "ingredient-0": "Maple Syrup", "instruction-1": "test instruction", "blurb": "test blurb" }
            c.post("/addrecipe", data=recipe_data)
            user_recipe_id  = get_last_recipe_id()
            
            user_recipe_dictionaries = get_user_recipes(12)
            user_recipe_ids = [recipe["Id"] for recipe in user_recipe_dictionaries]
            self.assertTrue(user_recipe_id in user_recipe_ids)
            
            c.get("/delete/{}".format(user_recipe_id))
            
            user_recipe_dictionaries = get_user_recipes(12)
            user_recipe_ids = [recipe["Id"] for recipe in user_recipe_dictionaries]
            self.assertFalse(user_recipe_id in user_recipe_ids)
            
            other_user_recipe_dictionaries = get_user_recipes(13)
            other_user_recipe_ids = [recipe["Id"] for recipe in other_user_recipe_dictionaries]
            random_other_user_recipe_id = choice(other_user_recipe_ids)
            c.get("/delete/{}".format(random_other_user_recipe_id))
            
            returned_other_user_dictionaries = get_user_recipes(13)
            returned_other_user_ids = [recipe["Id"] for recipe in returned_other_user_dictionaries]
            self.assertTrue(random_other_user_recipe_id in returned_other_user_ids)
            
    def test_get_edit_recipe_page(self):
        """
        test to check that the edit recipe page
        returns  a response code of 200 and uses the
        edit.html template. If the recipe was not submitted
        by the current user, should be redirected to home page
        """
        
        with c:
            login_data = { "login-username": "Paddywc", "password": "Password"}
            c.post("/login", data=login_data, follow_redirects=False)
            other_users_recipes = get_user_recipes(13)
            other_user_recipe_ids = [recipe["Id"] for recipe in other_users_recipes]
            random_other_user_recipe = choice(other_user_recipe_ids)
            response = c.get("/edit/{}".format(random_other_user_recipe), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(b'<h2 class="search-header">' in response.data)
            
            current_users_recipes = get_user_recipes(12)
            current_user_recipe_ids = [recipe["Id"] for recipe in current_users_recipes]
            random_user_recipe = choice(current_user_recipe_ids)
            response = c.get("/edit/{}".format(random_user_recipe), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(b'<h1 class="add-recipe-header">' in response.data)
            
    def test_can_edit_recipe(self):
        """
        test to check that a user can edit their own recipe
        using the frontend edit recipe page
        """
        with c:
            login_data = { "login-username": "Paddywc", "password": "Password"}
            c.post("/login", data=login_data, follow_redirects=False)
            
            original_values = {"prep-hours": 2, "prep-mins": 30, "cook-hours": 1, "cook-mins": 15, "recipe-name": "Test Edit", "difficulty-select": "1", "serves": 2, "category-0": "German", "quantity-0": "1 Cup", "ingredient-0": "Maple Syrup", "instruction-1": "test instruction", "blurb": "test blurb" }
            c.post("/addrecipe", data=original_values)
            
            recipe_id = get_last_recipe_id()
            original_returned_values = get_recipe_values(recipe_id)
            
            self.assertEqual(original_returned_values["Name"], original_values["recipe-name"])
            self.assertEqual(original_returned_values["Serves"], original_values["serves"])
            self.assertEqual(original_returned_values["Blurb"], original_values["blurb"])
            
            new_values = {"prep-hours": 1, "prep-mins": 20, "cook-hours": 5, "cook-mins": 00, "recipe-name": "Edited test edit", "difficulty-select": "2", "serves": 5, "category-0": "Christmas", "quantity-0": "1/2 cup", "ingredient-0": "Mustard", "instruction-1": "New test instruction", "blurb": "Edited blurb"}
            
            c.post("/edit/{}".format(recipe_id), data=new_values)
            
            new_returned_values = get_recipe_values(recipe_id)
            
            self.assertEqual(new_returned_values["Name"], new_values["recipe-name"])
            self.assertEqual(new_returned_values["Serves"], new_values["serves"])
            self.assertEqual(new_returned_values["Blurb"], new_values["blurb"])
            
            self.assertNotEqual(original_returned_values["PrepTime"], new_returned_values["PrepTime"])
            self.assertNotEqual(original_returned_values["CookTime"], new_returned_values["CookTime"])
            self.assertNotEqual(original_returned_values["Instructions"], new_returned_values["Instructions"])
            self.assertNotEqual(original_returned_values["Categories"], new_returned_values["Categories"])
            self.assertNotEqual(original_returned_values["Difficulty"], new_returned_values["Difficulty"])
            self.assertNotEqual(original_returned_values["Ingredients"], new_returned_values["Ingredients"])
            
            
            # Deletes recipes data
            c.get("/delete/{}".format(recipe_id))
            
    def test_get_recipe_page(self):
        """
        test to check that the show_recipe page 
        returns a response code of 200 and uses
        the recipe.html template
        """
        
        with c:
            random_recipe_id = choice(get_list_of_recipe_ids())
            response = c.get("/recipe/{}".format(random_recipe_id))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(b'<h1 id="recipe-page-header">' in response.data)
            
            