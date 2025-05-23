import unittest
from unittest.mock import patch, MagicMock
import src.flask_app.main as main
from src.flask_app import gamedata
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os
import subprocess
import sys
import chromedriver_autoinstaller
from dotenv import load_dotenv
import shutil
from flask_session import Session
import glob
import json

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

    def initialize_game(self):
        game = gamedata.Game()
        game.start_game(first_to=1, format=501, name_a="Alice", name_b="Bob")
        main.gameRef = game

    def test_get_to_home(self):
        # make a get request to the route "/" of the test client and check if status code is 200
        print("\nTesting home route via '/' in Flask App...")
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        print("\n Testing home route again with /play")
        response = self.app.get("/play")
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
        for file in session_files:
            try:
                with open(file, "rb") as f:
                    contents = f.read().decode("utf-8", errors="ignore")
                    if "Hallo" in contents and "Mrs. Darts" in contents:
                        found = True
                        break
            except Exception:
                continue  # Skip unreadable files

        self.assertTrue(found, "No session file contained both 'Hallo' and 'Mrs. Darts'")

    def test_next_player(self):
        print("\nTesting next player route in Flask App...")
        resonse = self.app.get("/next")
        json_data = resonse.get_json()
        self.assertEqual(json_data["success"], True)

    @patch("src.flask_app.main.gameRef")
    def test_two_players_game(self, MockGameRef):
        # Create mock instance
        mock_gameRef_instance = MockGameRef.return_value
        
        # Mock all required methods
        mock_gameRef_instance.get_totals.return_value = [45, 60]
        mock_gameRef_instance.get_wins.return_value = [0, 0]
        mock_gameRef_instance.playing = True
        
        # Initialize game with proper values
        mock_gameRef_instance.start_game.return_value = None
        mock_gameRef_instance.format = 301
        mock_gameRef_instance.first_to = 2
        
        # Make the request
        response = self.app.get("/game/Max/Moritz/301/2")

        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Max", response.data)
        self.assertIn(b"Moritz", response.data)
        
        # Verify the game was properly initialized
        mock_gameRef_instance.start_game.assert_called_once_with(
            first_to=2,
            format=301,
            name_a="Max",
            name_b="Moritz"
        )
    
    @patch("src.flask_app.main.camera_handling.camera")
    def test_board_status_route(self, mock_camera_class):
        # Mock camera instance
        mock_camera = MagicMock()
        mock_camera.get_available_cameras.return_value = ["Camera 0", "Camera 1"]
        mock_camera.resulution_options = ["640x480", "1280x720"]
        mock_camera.fps_options = [30, 60]

        # Assign mock instance to class constructor return
        mock_camera_class.return_value = mock_camera

        # Make the request
        response = self.app.get("/board-status")
        
        # Validate response
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("Camera 0", html)
        self.assertIn("1280x720", html)

    def test_real_dart_throw_scenario(self):
        # Simulate a valid dart throw: single 20
        response = self.app.get("/throw?throwNumber=1&score=20&multiplier=1")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)

        # Basic assertions about the response
        self.assertEqual(data["received"], 20)
        self.assertEqual(data["multiplier"], 1)
        self.assertEqual(data["displayScore"], "20")
        self.assertIn("scoreA", data)
        self.assertIn("scoreB", data)
        self.assertIn("currentThrows", data)
        self.assertIsInstance(data["currentThrows"], list)
        self.assertIn("isBust", data)
        self.assertIn("justWon", data)
        self.assertIn("scoreRecommendation", data)

        print("Game state after throw:", data)

        # verify player A's score decreased from 501 (default start)
        self.assertLess(data["scoreA"], 501)
    
    def test_undo_throw_success(self):
        # Arrange: start the game
        self.initialize_game()

        # Act 1: make a throw via the route
        resp_throw = self.app.get("/throw", query_string={
            "throwNumber": 1,
            "score": 20,
            "multiplier": 2
        })
        self.assertEqual(resp_throw.status_code, 200)
        data_throw = resp_throw.get_json()

        # Check that the score actually decreased for player A
        score_after_throw = data_throw["scoreA"]
        self.assertLess(score_after_throw, 501,
                        f"Expected scoreA < 501 after throw, got {score_after_throw}")

        # Act 2: undo the throw
        resp_undo = self.app.post("/undo_throw")
        self.assertEqual(resp_undo.status_code, 200)
        data_undo = resp_undo.get_json()

        # Assert: undo was successful
        self.assertTrue(data_undo["success"])

        # After undo, player A's score returns to 501
        self.assertEqual(data_undo["scoreA"], 501)
        self.assertEqual(data_undo["scoreB"], 501)

        # No darts thrown in current turn
        self.assertEqual(data_undo["currentThrows"], ['-', '-', '-'])

    def test_undo_throw_failure(self):
        # Arrange: game with no throws
        self.initialize_game()

        # Act: undo immediately
        resp = self.app.post("/undo_throw")
        data = resp.get_json()

        # Assert: failure
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(data["success"])
        self.assertIn("error", data)


class IntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['FLASK_APP'] = 'src.flask_app.main'
        # Start Flask server once
        cls.flask_process = subprocess.Popen(
            ['python', '-m', 'flask', 'run', '--port', '5000'],
            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
        )
        # Give Flask time to come up
        WebDriverWaitTimeout = 5
        WebDriverWait(cls, WebDriverWaitTimeout).until(lambda _: True)

        # Install ChromeDriver and launch browser
        chromedriver_autoinstaller.install()
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        if sys.platform.startswith("linux"):
            options.binary_location = "/usr/bin/chromium"

        cls.browser = webdriver.Chrome(options=options)
        cls.wait = WebDriverWait(cls.browser, 10)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        cls.flask_process.terminate()
        cls.flask_process.wait()

    def start_game(self):
        # Navigate and start a new game
        self.browser.get("http://localhost:5000/play")
        # wait for form inputs
        self.wait.until(EC.visibility_of_element_located((By.ID, "player1name")))
        self.browser.find_element(By.ID, "player1name").send_keys("John")
        self.browser.find_element(By.ID, "player2name").send_keys("Phil")
        self.browser.find_element(
            By.CSS_SELECTOR, "input[type='submit'][value='Play']"
        ).click()
        # wait for redirect URL
        self.wait.until(EC.url_contains("/game/John/Phil/501/1"))

    def test_start_and_play(self):
        self.start_game()
        # verify title and scores
        self.wait.until(EC.title_is("Dart-App"))
        self.assertEqual(self.browser.current_url, "http://localhost:5000/game/John/Phil/501/1")

        p1 = self.wait.until(EC.visibility_of_element_located((By.ID, "playerA_score"))).text
        p2 = self.browser.find_element(By.ID, "playerB_score").text
        self.assertEqual(p1, "501")
        self.assertEqual(p2, "501")

    def test_throw_and_undo(self):
        self.start_game()

        # initial score
        initial = int(self.wait.until(
            EC.visibility_of_element_located((By.ID, "playerA_score"))
        ).text)

        # throw double 18
        self.wait.until(EC.element_to_be_clickable((By.ID, "double"))).click()
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='18']"))).click()

        # wait for score update
        self.wait.until(EC.text_to_be_present_in_element(
            (By.ID, "playerA_score"), str(initial - 36)
        ))

        # undo
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Undo')]"))).click()

        # wait for revert
        self.wait.until(EC.text_to_be_present_in_element(
            (By.ID, "playerA_score"), str(initial)
        ))
        final = int(self.browser.find_element(By.ID, "playerA_score").text)
        self.assertEqual(final, initial)

    def test_start_new_game(self):
        self.start_game()
        # click New Game link
        new_game = self.wait.until(EC.element_to_be_clickable((
            By.LINK_TEXT, "New Game"
        )))
        new_game.click()
        # wait for play page
        self.wait.until(EC.url_contains("/play"))
        self.assertTrue(self.browser.current_url.endswith("/play"))

    def test_board_status_and_return_to_game(self):
        self.start_game()

        # click Board Status
        board = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Board Status")))
        board.click()
        # wait for board-status URL
        self.wait.until(EC.url_contains("/board-status"))

        # check cams
        for cam_id in ("camera_a_feed", "camera_b_feed", "camera_c_feed"):
            elem = self.wait.until(EC.visibility_of_element_located((By.ID, cam_id)))
            self.assertTrue(elem.is_displayed(), f"{cam_id} not visible")

        # click Return to Game
        rtn = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Return to Game")))
        rtn.click()
        self.wait.until(EC.url_contains("/game/John/Phil/501/1"))
        self.assertEqual(self.browser.find_element(By.ID, "playerA_score").text, "501")

    def test_chat_chatbot(self):
        # 1) Wait for the chat button to be present in the DOM
        chat_btn = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.chat-button"))
        )
        # 2) Assert it’s displayed
        self.assertTrue(chat_btn.is_displayed(), "Chat button should be visible")

        # 3) Wait until it’s clickable, then click
        WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.chat-button"))
        ).click()

        # Wait until the input field is present
        input_field = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//input[@type='text' and @placeholder='Stellen Sie Ihre Frage...']")
            )
        )
        # Assert it's visible
        self.assertTrue(input_field.is_displayed(), "Input field should be visible")

        # Wait until the reset button is present
        reset_button = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[@class='reset-button' and text()='Chatverlauf zurücksetzen']"))
        )

        # Assert it's visible
        self.assertTrue(reset_button.is_displayed(), "Reset button should be visible")
        reset_button.click()

if __name__ == "__main__":
    unittest.main()