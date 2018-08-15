import unittest
from random import sample, choice

from flask import Flask

from add_recipe import get_form_values
from app_init import login_manager
from helpers import convert_list_to_string_for_sql_search
from sql_functions import get_username_for_id, get_id_for_username, check_if_username_exists, add_form_values_to_users, \
    open_connection_if_not_already_open, check_password_correct, get_value_from_recipes_table, get_recipe_user, \
    get_recipe_instructions, get_recipe_categories, get_recipe_ingredients, get_all_ingredients_from_table, \
    get_all_categories_from_table, get_excluded_categories_list, get_excluded_ingredients_list, get_last_recipe_id, \
    add_to_categories_if_not_duplicate, add_to_ingredients_if_not_duplicate, close_connection_if_open, \
    get_list_of_recipe_ids, add_to_recipe_categories, add_to_recipe_ingredients, get_recipe_reviews, \
    get_user_favourites, add_average_review_score_to_dictionary_list, insert_dictionary_into_recipes_table, \
    get_recipe_values

app = Flask(__name__)
c = app.test_client()

login_manager.init_app(app)
login_manager.login_view = 'login'  # from https://stackoverflow.com/questions/33724161/flask-login-shows-401-instead-of-redirecting-to-login-view


class TestSQLFunctions(unittest.TestCase):

    def test_can_match_id_with_username(self):
        """
        test to check that get_username_for_id returns
        the correct username for the argument id, and that
        get_id_for_username returns the correct id for
        the argument username
        """

        sample_of_ids_and_usernames = [{"username": "Paddywc", "id": 12}, {"username": "Sam", "id": 18},
                                       {"username": "Bart", "id": 21}, {"username": "Ben", "id": 25}]
        random_dictionary = choice(sample_of_ids_and_usernames)

        returned_username = get_username_for_id(random_dictionary["id"])
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

        should_be_a_tin_of_baked_beans = get_value_from_recipes_table("Blurb", 127)
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
        sample_categories = [{"Name": "Indian", "Id": 16}, {"Name": "Vegetarian", "Id": 9}]
        filtered_category_ids = get_excluded_categories_list([category["Name"] for category in sample_categories])
        self.assertEqual(len(filtered_category_ids),
                         (len(all_categories_in_recipe_categories) - len(sample_categories)))
        for category in sample_categories:
            self.assertTrue(category["Id"] in all_categories_in_recipe_categories)
            self.assertTrue(category["Id"] not in filtered_category_ids)

        all_ingredients_in_recipe_ingredients = get_excluded_ingredients_list(["No valid filter"])
        sample_ingredients = [{"Name": "Butter", "Id": 6}, {"Name": "Rashers", "Id": 13}]
        filtered_ingredient_ids = get_excluded_ingredients_list(
            [ingredient["Name"] for ingredient in sample_ingredients])
        self.assertEqual(len(filtered_ingredient_ids),
                         (len(all_ingredients_in_recipe_ingredients) - len(sample_ingredients)))
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
            # login required to add recipe
            login_data = {"login-username": "Paddywc", "password": "Password"}
            c.post("/login", data=login_data, follow_redirects=False)

            form_data = {"prep-hours": 2, "prep-mins": 30, "cook-hours": 1, "cook-mins": 15,
                         "recipe-name": "Test Last Id", "difficulty-select": "1", "serves": 2, "category-0": "German",
                         "quantity-0": "1 spoon", "ingredient-0": "Maple Syrup", "ingredient-1": "Mustard",
                         "quantity-1": "1/2 cup", "instruction-1": "test instruction", "blurb": "test blurb"}

            c.post("/addrecipe", data=form_data)

            id_retrieved_using_function = get_last_recipe_id()

            connection = open_connection_if_not_already_open()
            with connection.cursor() as cursor:
                cursor.execute('SELECT Id from Recipes where Recipes.Name="Test Last Id";')
                returned_tuple = cursor.fetchone()
                id_from_database = returned_tuple[0]

                # Deletes test values from database
                cursor.execute(
                    "DELETE FROM RecipeIngredients WHERE RecipeIngredients.RecipeId = {} ; ".format(id_from_database))
                cursor.execute(
                    "DELETE FROM RecipeCategories WHERE RecipeCategories.RecipeId = {} ; ".format(id_from_database))
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
        self.assertTrue((new_categories[0] not in categories_prior_to_function_call) and (
                new_categories[1] not in categories_prior_to_function_call))
        with_new_categories = random_existing_categories + new_categories
        add_to_categories_if_not_duplicate(with_new_categories)
        categories_after_second_function_called = get_all_categories_from_table()
        self.assertEqual(len(categories_after_second_function_called), len(categories_prior_to_function_call) + 2)

        ingredients_prior_to_function_call = get_all_ingredients_from_table()
        random_existing_ingredients = sample(ingredients_prior_to_function_call, 3)
        existing_ingredients_dictionary_list = [{"Name": ingredient} for ingredient in random_existing_ingredients]
        add_to_ingredients_if_not_duplicate(existing_ingredients_dictionary_list)
        ingredients_after_function_called = get_all_ingredients_from_table()
        self.assertEqual(len(ingredients_after_function_called), len(ingredients_prior_to_function_call))

        new_ingredients = [{"Name": "Not Existing"}, {"Name": "Another test"}]
        self.assertTrue((new_ingredients[0]["Name"] not in ingredients_prior_to_function_call) and (
                new_ingredients[1] not in ingredients_prior_to_function_call))
        with_new_ingredients = existing_ingredients_dictionary_list + new_ingredients
        add_to_ingredients_if_not_duplicate(with_new_ingredients)
        ingredients_after_second_function_called = get_all_ingredients_from_table()
        self.assertEqual(len(ingredients_after_second_function_called), len(ingredients_prior_to_function_call) + 2)

        # Delete test values from tables
        test_values_string = convert_list_to_string_for_sql_search(new_categories)
        connection = open_connection_if_not_already_open()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM Ingredients WHERE Name IN {} ; ".format(test_values_string))
            cursor.execute("DELETE FROM Categories WHERE Name IN {} ; ".format(test_values_string))
            connection.commit()

        close_connection_if_open()

    def test_can_add_to_recipe_categories(self):
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
        self.assertEqual(len(original_recipe_categories) + 3, len(new_recipe_categories))
        for category in test_categories_list:
            self.assertTrue(category in new_recipe_categories)

        # deletes test values from database
        connection = open_connection_if_not_already_open()
        test_categories_string = convert_list_to_string_for_sql_search(test_categories_list)
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

        test_ingredients_dictionary_list = [{"Name": "Test1", "Quantity": "1 Test"},
                                            {"Name": "Test2", "Quantity": "2 Test"},
                                            {"Name": "Test3", "Quantity": "3 Test"},
                                            {"Name": "Test4", "Quantity": "4 Test"}]
        original_recipe_ingredients = get_recipe_ingredients(random_recipe_id)
        for ingredient in test_ingredients_dictionary_list:
            self.assertFalse(
                ingredient["Name"] in [ingredient["Ingredient"] for ingredient in original_recipe_ingredients])
            self.assertFalse(
                ingredient["Quantity"] in [ingredient["Quantity"] for ingredient in original_recipe_ingredients])

        add_to_ingredients_if_not_duplicate(test_ingredients_dictionary_list)
        add_to_recipe_ingredients(test_ingredients_dictionary_list, random_recipe_id)

        new_recipe_ingredients = get_recipe_ingredients(random_recipe_id)
        self.assertEqual(len(original_recipe_ingredients) + 4, len(new_recipe_ingredients))
        for ingredient in test_ingredients_dictionary_list:
            self.assertTrue(ingredient["Name"] in [ingredient["Ingredient"] for ingredient in new_recipe_ingredients])
            self.assertTrue(ingredient["Quantity"] in [ingredient["Quantity"] for ingredient in new_recipe_ingredients])

        # deletes test values from database
        connection = open_connection_if_not_already_open()
        ingredient_name_list = [ingredient["Name"] for ingredient in test_ingredients_dictionary_list]
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
            ids_of_recipes_user_has_already_reviewed = [recipe_id for recipe_id in all_recipe_ids if
                                                        recipe_id not in ids_of_recipes_user_has_already_reviewed]
            random_recipe_id = choice(ids_of_recipes_user_has_already_reviewed)
            review_score = {"user-review": "6"}

            c.get("/logout")
            c.post("/recipe/{}".format(random_recipe_id), data=review_score, follow_redirects=False)
            recipe_reviews = get_recipe_reviews(random_recipe_id)
            self.assertFalse(6 in recipe_reviews)

            login_data = {"login-username": "Paddywc", "password": "Password"}
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
            login_data = {"login-username": "Patrick", "password": "Password"}
            c.post("/login", data=login_data, follow_redirects=False)
            existing_user_favorites = get_user_favourites(14)
            existing_favorites_id_list = [recipe["Id"] for recipe in existing_user_favorites]
            random_existing_favorite_id = choice(existing_favorites_id_list)

            c.get("/addtofavourites/{}".format(random_existing_favorite_id))
            new_user_favorites = get_user_favourites(14)
            self.assertEqual(len(new_user_favorites), len(existing_user_favorites))

            all_recipe_ids = get_list_of_recipe_ids()
            ids_of_recipes_that_user_has_not_favorited = [recipe_id for recipe_id in all_recipe_ids if
                                                          recipe_id not in existing_favorites_id_list]
            random_new_recipe_id = choice(ids_of_recipes_that_user_has_not_favorited)

            c.get("/addtofavourites/{}".format(random_new_recipe_id))
            new_user_favorites = get_user_favourites(14)
            self.assertEqual(len(new_user_favorites), len(existing_user_favorites) + 1)

            # deletes test values from database
            connection = open_connection_if_not_already_open()
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM UserFavourites WHERE RecipeId = {} AND UserId = 14 ".format(random_new_recipe_id))
                connection.commit()

    def test_can_get_average_review_score_from_dictionary_with_recipe_id(self):
        """
        test to check that add_average_review_score_to_dictionary_list adds a 'Score'
        value to each dictionary in the argument list. This value should be the average of all
        Score values from rows in the Reviews table whose RecipeId value matches
        the Id value of the argument dictionary
        """

        with c:
            login_data = {"login-username": "Paddywc", "password": "Password"}
            c.post("/login", data=login_data, follow_redirects=False)
            new_recipe_data = {"prep-hours": 5, "prep-mins": 30, "cook-hours": 1, "cook-mins": 15,
                               "recipe-name": "Test Avg Review Score", "difficulty-select": "1", "serves": 2,
                               "category-0": "German", "quantity-0": "1 Teaspoon", "ingredient-0": "Pepper",
                               "instruction-1": "test instruction", "blurb": "test blurb"}
            c.post("/addrecipe", data=new_recipe_data)
            id_of_new_recipe = get_last_recipe_id()
            populate_reviews_avg_of_4 = [{"UserId": 15, "Score": 5}, {"UserId": 28, "Score": 3},
                                         {"UserId": 17, "Score": 4}]

            connection = open_connection_if_not_already_open()
            with connection.cursor() as cursor:
                for user in populate_reviews_avg_of_4:
                    cursor.execute('INSERT INTO Reviews(UserId, Score, RecipeId) VALUES ("{0}", "{1}", "{2}");'.format(
                        user["UserId"], user["Score"], id_of_new_recipe))
                connection.commit()

            dictionary_with_recipe_id = {"Id": id_of_new_recipe}
            dictionary_with_id_and_avg_score = add_average_review_score_to_dictionary_list([dictionary_with_recipe_id])[
                0]

            self.assertEqual(dictionary_with_id_and_avg_score["Id"], id_of_new_recipe)
            self.assertEqual(dictionary_with_id_and_avg_score["Score"], 4)

            # Deletes test data from tables
            connection = open_connection_if_not_already_open()
            with connection.cursor() as cursor:
                cursor.execute('SELECT Id from Recipes where Recipes.Name="Test Avg Review Score";')
                returned_tuple = cursor.fetchone()
                id_from_database = returned_tuple[0]
                cursor.execute(
                    'DELETE FROM RecipeIngredients WHERE RecipeIngredients.RecipeId = "{}" ; '.format(id_from_database))
                cursor.execute(
                    'DELETE FROM RecipeCategories WHERE RecipeCategories.RecipeId = "{}" ; '.format(id_from_database))
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
            login_data = {"login-username": "Patrick", "password": "Password"}
            c.post("/login", data=login_data, follow_redirects=False)

            new_recipe_data = {"prep-hours": 1, "prep-mins": 30, "cook-hours": 4, "cook-mins": 30,
                               "recipe-name": "Test Inserting", "difficulty-select": "2", "serves": 2,
                               "category-0": "Breakfast", "quantity-0": "1/2 Cup", "ingredient-0": "Pepper",
                               "instruction-1": "Test instruction 1", "blurb": "this is a test"}
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
            self.assertEqual(retrieved_recipe_values["Instructions"][0], "Test instruction 1")

            # Tests values were only added to Recipes table
            # and not RecipeCategories and RecipesIngredients tables
            self.assertEqual(len(retrieved_recipe_values["Categories"]), 0)
            self.assertEqual(len(retrieved_recipe_values["Ingredients"]), 0)

            # Deletes test data from tables
            connection = open_connection_if_not_already_open()
            with connection.cursor() as cursor:
                cursor.execute('DELETE FROM Recipes WHERE Name = "{}"; '.format("Test Inserting"))
                connection.commit()
