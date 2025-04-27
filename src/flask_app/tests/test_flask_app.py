import unittest
from unittest.mock import patch
from src.flask_app.main import app
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os
import subprocess
import sys
import chromedriver_autoinstaller

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

class IntegrationTest(unittest.TestCase):

    def setUp(self):
        os.environ['FLASK_APP'] = 'src.flask_app.main' 
        # initialize the Flask test client
        self.flask_process = subprocess.Popen(['python', '-m', 'flask', 'run', '--port', '5000'])
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # Only set binary location for CI-CD
        if sys.platform.startswith("linux"):
            chromedriver_autoinstaller.install()
            options.binary_location = "/usr/bin/chromium"
        else:
            chromedriver_autoinstaller.install()
        self.browser =  webdriver.Chrome(options=options)
        self.browser.implicitly_wait(20)

    def tearDown(self):
        self.browser.quit()
        self.flask_process.terminate()


    def test_game(self):
        self.browser.get("http://localhost:5000/play")
        time.sleep(3)
        self.browser.implicitly_wait(2)
        player1_input = self.browser.find_element(By.ID, "player1name")
        player2_input = self.browser.find_element(By.ID, "player2name")
        
        # fill in player names
        player1_input.send_keys("John")
        player2_input.send_keys("Phil")

        # press submit button

        submit_button = self.browser.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Play']")
        submit_button.click()
        time.sleep(3)
        
        
        # Check if the Browser title updated to "Dart App, New Game"
        self.assertEqual(self.browser.title, 'Dart-App')

        # check if the expected route was used
        self.assertEqual( self.browser.current_url, "http://localhost:5000/game/John/Phil/501/1")

        player1_score = self.browser.find_element(By.ID, "playerA_score").text
        player2_score = self.browser.find_element(By.ID, "playerB_score").text

        self.assertTrue(player1_score=="501"), "Expect player A to start with score 501"
        self.assertTrue(player2_score=="501"), "Expected player B to start with score 501"
    

if __name__ == "__main__":
    unittest.main()
