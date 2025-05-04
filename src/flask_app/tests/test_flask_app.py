import unittest
from unittest.mock import patch
import src.flask_app.main as main
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os
import subprocess
import sys
import chromedriver_autoinstaller
from dotenv import load_dotenv
import shutil
from flask_session import Session
import glob

load_dotenv()


class FlaskUnitTest(unittest.TestCase):
    def setUp(self):
        # initialize the Flask test client
        main.app.config["TESTING"] = True
        main.app.config["SESSION_TYPE"] = "filesystem"
        main.app.config["SESSION_FILE_DIR"] = "./flask_session"
        main.app.config["SESSION_PERMANENT"] = False
        Session(main.app)  # <-- important
        main.app.config["SECRET_KEY"] = "supersecretkey"
        self.app = main.app.test_client()


    def test_get_to_home(self):
        # make a get request to the route "/" of the test client and check if status code is 200
        print("\nTesting home route in Flask App...")
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)

    def test_score_recommendations(self):
        response = self.app.post("/get_score_recommendation", json={"score": 36})
        recommendation = response.get_json()
        self.assertTrue(response.status_code==200)
        self.assertTrue(recommendation["scoreRecommendation"]==["D18"])

        no_possible_recommendation = self.app.post("/get_score_recommendation", json={"score": 700})
        self.assertTrue(no_possible_recommendation.get_json()["scoreRecommendation"] is None)

    def test_score_recommendations_bad_request(self):
        response = self.app.post("/get_score_recommendation",
                                json={}  # sends empty JSON with correct Content-Type
                                )
        self.assertEqual(response.status_code, 400)

    def test_new_game(self):
        # Define the form data expected by the route
        form_data = {
            'game-type': '501',
            'legs': '1',
            'player1name': 'Alice',
            'player2name': 'Bob'
        }

        # Send POST request to the /new_game route
        response = self.app.post('/new_game', data=form_data, follow_redirects=False)

        # Check if the response is a redirect (302)
        self.assertEqual(response.status_code, 302)

        # Check if the redirect location is correct
        self.assertIn('/game/Alice/Bob/501/1', response.headers['Location'])

    @patch.dict(os.environ, {"GROQ_API_KEY": "wrong_key"})
    def test_chat_wrong_api_key(self):
        response = self.app.post('/chat', json={"message": "Hallo"})
        self.assertEqual(response.status_code,401)

    @patch("src.flask_app.main.Groq")  
    def test_chat_valid_api_key(self, mock_groq_class):
        # Arrange: Mock Groq client response
        mock_client = mock_groq_class.return_value
        mock_completion = mock_client.chat.completions.create.return_value

        # Simulated Groq response structure
        mock_completion.choices = [
            type("obj", (object,), {
                "message": type("msg", (object,), {"content": "Hi, ich bin Mrs. Darts. Wie kann ich helfen?"})
            })()
        ]

        # Act: Make request to Flask route
        response = self.app.post('/chat', json={"message": "Hallo"})

        # Assert: Validate HTTP and content
        self.assertEqual(response.status_code, 200)
        self.assertIn("Mrs. Darts", response.data.decode("utf-8"))

    def test_chat_empty_chat_message(self):
        response = self.app.post("/chat", json = {})
        self.assertEqual(response.status_code,400)

    @patch("src.flask_app.main.Groq")  
    def test_chat_session_saved_to_disk(self, mock_groq_class):
        # Arrange
        session_dir = "./flask_session"
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir)
        os.makedirs(session_dir)

        # Mock Groq client
        mock_client = mock_groq_class.return_value
        mock_completion = mock_client.chat.completions.create.return_value
        mock_completion.choices = [
            type("obj", (object,), {
                "message": type("msg", (object,), {"content": "Hi, ich bin Mrs. Darts."})
            })()
        ]

        # Act
        response = self.app.post('/chat', json={"message": "Hallo"})

        # Assert
        self.assertEqual(response.status_code, 200)

        session_files = glob.glob(os.path.join(session_dir, "*"))
        self.assertGreater(len(session_files), 0, "No session file was created.")
        latest_file = min(session_files, key=os.path.getmtime)
        # Optionally: check content
        with open(latest_file, "rb") as f:
            contents = f.read().decode("utf-8", errors="ignore")
            self.assertIn("Hallo", contents)
            self.assertIn("Mrs. Darts", contents)

    """
    def test_chat_history(self):
        self.app.post("/chat", json={"message": "Hi, my name is Bob"})
        response = self.app.post("/chat", json={"message": "What is my name?"})
        response_text = response.data.decode("utf-8")
        self.assertIn("Bob", response_text)
        self.assertTrue()
    """
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
