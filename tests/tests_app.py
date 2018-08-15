import unittest
from random import choice

from flask import Flask

from app import check_user_is_logged_in, get_recipe_values_for_data_visualization, get_all_data_for_visualization, \
    check_is_current_users_userpage
from app_init import login_manager
from helpers import get_average_review_score
from sql_functions import check_if_username_exists, open_connection_if_not_already_open, get_list_of_recipe_ids, \
    get_recipe_values, get_last_recipe_id, get_user_recipes

app = Flask(__name__)
c = app.test_client()

login_manager.init_app(app)
login_manager.login_view = 'login'  # from https://stackoverflow.com/questions/33724161/flask-login-shows-401-instead-of-redirecting-to-login-view


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
            login_data = {"login-username": "Cremen", "password": "Password"}
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

            login_data = {"login-username": "Paddywc", "password": "Password"}
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
            login_data = {"login-username": "Paddywc", "password": "Password"}
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
            login_data = {"login-username": "Paddywc", "password": "Password"}
            c.post("/login", data=login_data, follow_redirects=False)

            recipe_data = {"prep-hours": 2, "prep-mins": 30, "cook-hours": 1, "cook-mins": 15,
                           "recipe-name": "Test Delete", "difficulty-select": "1", "serves": 4, "category-0": "German",
                           "quantity-0": "1 Cup", "ingredient-0": "Maple Syrup", "instruction-1": "test instruction",
                           "blurb": "test blurb"}
            c.post("/addrecipe", data=recipe_data)
            user_recipe_id = get_last_recipe_id()

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
            login_data = {"login-username": "Paddywc", "password": "Password"}
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
            login_data = {"login-username": "Paddywc", "password": "Password"}
            c.post("/login", data=login_data, follow_redirects=False)

            original_values = {"prep-hours": 2, "prep-mins": 30, "cook-hours": 1, "cook-mins": 15,
                               "recipe-name": "Test Edit", "difficulty-select": "1", "serves": 2,
                               "category-0": "German", "quantity-0": "1 Cup", "ingredient-0": "Maple Syrup",
                               "instruction-1": "test instruction", "blurb": "test blurb"}
            c.post("/addrecipe", data=original_values)

            recipe_id = get_last_recipe_id()
            original_returned_values = get_recipe_values(recipe_id)

            self.assertEqual(original_returned_values["Name"], original_values["recipe-name"])
            self.assertEqual(original_returned_values["Serves"], original_values["serves"])
            self.assertEqual(original_returned_values["Blurb"], original_values["blurb"])

            new_values = {"prep-hours": 1, "prep-mins": 20, "cook-hours": 5, "cook-mins": 00,
                          "recipe-name": "Edited test edit", "difficulty-select": "2", "serves": 5,
                          "category-0": "Christmas", "quantity-0": "1/2 cup", "ingredient-0": "Mustard",
                          "instruction-1": "New test instruction", "blurb": "Edited blurb"}

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
