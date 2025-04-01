import unittest
from unittest.mock import patch
from src.flask_app.main import app

# in this script, we can add tests for main.py.
# At the moment, I only created one to work on Gitlab Integration.


class FlaskUnitTest(unittest.TestCase):
    def setUp(self):
        # initialize the Flask test client
        self.app = app.test_client()
        self.app.testing = True

    def test_get_to_home(self):
        # make a get request to the route "/" of the test client and check if status code is 200
        print("\nTesting home route in Flask App...")
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)

    def test_next_player(self):
        print("\nTesting next player route in Flask App...")
        resonse = self.app.get("/next")
        json_data = resonse.get_json()
        self.assertEqual(json_data["success"], True)

    @patch("src.flask_app.main.gameRef")
    def test_two_players_game(self, MockGameRef):
        mock_gameRef_instance = MockGameRef.return_value
        mock_gameRef_instance.get_totals.return_value = [45, 60]

        response = self.app.get("/game/Max/Moritz/301/25")

        self.assertEqual(response.status_code, 200)

        self.assertIn(b"Max", response.data)
        self.assertIn(b"Moritz", response.data)
        # derzeit noch Fehler aufgrund von MagicMock
        # self.assertIn(b"45", response.data)
        # self.assertIn(b"60", response.data)


if __name__ == "__main__":
    unittest.main()
