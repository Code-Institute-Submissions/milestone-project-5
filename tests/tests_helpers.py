import datetime
import unittest

from flask import Flask

from app_init import login_manager
from helpers import get_average_review_score, check_if_string_contains_letters, return_timedelta_full_hours, \
    return_timedelta_remaining_minutes

app = Flask(__name__)
c = app.test_client()

login_manager.init_app(app)
login_manager.login_view = 'login'  # from https://stackoverflow.com/questions/33724161/flask-login-shows-401-instead-of-redirecting-to-login-view


class TestHelpers(unittest.TestCase):

    def test_get_average_review_score_returns_average_of_argument_list(self):
        """
        test to check that get_average_review_score returns that average
        int of its argument list, rounded to the nearest int
        """

        should_be_3 = [1, 2, 3, 4, 5]
        self.assertEqual(get_average_review_score(should_be_3), 3)

        should_be_rounded_to_3 = [1, 3, 4]
        self.assertEqual(get_average_review_score(should_be_rounded_to_3), 3)

        should_be_rounded_to_1 = [1, 1, 2]
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
        three_20_timedelta_object = datetime.datetime.combine(datetime.date.min,
                                                              three_hours_20_mins) - datetime.datetime.min
        self.assertEqual(return_timedelta_full_hours(three_20_timedelta_object), 3)
        self.assertEqual(return_timedelta_remaining_minutes(three_20_timedelta_object), 20)

        five_hours_50_mins = datetime.time(5, 50)
        five_50_timedelta_object = datetime.datetime.combine(datetime.date.min,
                                                             five_hours_50_mins) - datetime.datetime.min
        self.assertEqual(return_timedelta_full_hours(five_50_timedelta_object), 5)
        self.assertEqual(return_timedelta_remaining_minutes(five_50_timedelta_object), 50)
