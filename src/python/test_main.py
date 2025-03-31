import unittest
from main import app

# in this script, we can add tests for main.py. At the moment, I only created one to work on Gitlab Integration.


class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        # initialize the Flask test client
        self.app = app.test_client()
        self.app.testing=True

    def test_get_to_home(self):
        # make a get request to the route "/" of the test client and check if status code is 200
        response = self.app.get("/")
        self.assertEqual(response.status_code,200)

if __name__== '__main__':
    unittest.main()
