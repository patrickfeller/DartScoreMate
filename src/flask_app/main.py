# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, jsonify, Response, session
from . import gamedata
from . import camera_handling
import cv2 
from flask_session import Session
from dotenv import load_dotenv
from mysql.connector.errors import Error
from . import aid_functions_sql 
from . import recommender
import random
import platform
from groq import Groq
import os

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY', "")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Shared thread references, currently not clear why needed
adminRef = gamedata.Admin()
gameRef = gamedata.Game()

# Flask setup
app = Flask(__name__)
app.secret_key = "supersecretkey"  # Kann auch aus .env kommen
app.config["SESSION_TYPE"] = "filesystem"  # Damit wird die Session serverseitig gespeichert
app.config["SESSION_PERMANENT"] = False
Session(app)

# ------------------------- ROUTES -------------------------

@app.route("/")
@app.route("/play")
def play():
    return render_template("play.html")

@app.route("/board-status")
def boardstatus():
    cam = camera_handling.camera()
    return render_template("board-status.html",
                           avaiable_cameras=cam.get_available_cameras(),
                           resulution_options=cam.resulution_options,
                           fps_options=cam.fps_options)

@app.route("/video_feed")
def video_feed():
    camera_id = request.args.get('camera_id', default=0, type=int)
    return Response(generate_frames(camera_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames(camera_id):
    system = platform.system()
    if system == "Linux":
        camera = cv2.VideoCapture(camera_id, cv2.CAP_V4L2)
    else:
        camera = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    try:
        while True:
            success, frame = camera.read()
            if not success:
                break
            ret, buffer = cv2.imencode('.jpeg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    finally:
        camera.release()

@app.route("/new_game", methods=["POST"])
def new_game():
    format = int(request.form['game-type'])
    first_to = int(request.form['legs'])
    playerA = request.form['player1name']
    playerB = request.form['player2name']
    gameRef.start_game(first_to, format, playerA, playerB)
    session.pop("loaded_game_id", None)  # Entferne alte Spiel-ID, falls vorhanden
    return redirect(f'/game/{playerA}/{playerB}/{format}/{first_to}')

@app.route('/game/<playerA>/<playerB>/<format>/<first_to>')
def game(playerA, playerB, format, first_to):
    scores = gameRef.get_totals()
    first_to = int(first_to)
    current_player = gameRef.current_leg.player_index
    wins_players = [player.wins for player in gameRef.players]
    return render_template('game.html',
                           playerA=playerA,
                           playerB=playerB,
                           format=format,
                           scoreA=scores[0],
                           scoreB=scores[1],
                           wins_playerA = wins_players[0],
                           wins_playerB = wins_players[1],
                           first_to=first_to,
                           current_player=current_player)

# Route for a new game round / new leg
@app.route('/new_leg', methods=["POST"])
def new_leg():
    # Check if game is active
    if gameRef.playing:
        # Check if game is not over
        if not gameRef.is_game_over():
            # get current Game state
            playerA, playerB = [player.name for player in gameRef.players]
            format = gameRef.format
            first_to = gameRef.first_to
            # Start a new leg
            return redirect('/game/'+playerA+'/'+playerB+'/'+str(format)+'/'+str(first_to))
        # if game is over, redirect to start page
        else:
            return redirect('/play')
    # if no game is active, redirect to start page
    else:
        return redirect('/play')


# Route for handling throws
@app.route("/throw")
def handle_throw():
    throw_number = int(request.args.get('throwNumber', 1))
    base_score = int(request.args.get('score', 0))
    multiplier = int(request.args.get('multiplier', 1))
    score_recommendation = 0 # equal to false in JS
    # Create a dart object
    dart = gamedata.Dart(base_score, multiplier, None)  # Position is None as we don't use camera
    
    # Try to make the throw
    gameRef.dart(dart)    
    
    # Get updated game state
    scores = gameRef.get_totals()

    current_throws = gameRef.get_scores()
    active_player = gameRef.current_leg.player_index
    current_player_throws = current_throws[active_player]
    
    # give score recommendations:
    if throw_number < 3:
        double_out_recommendation = recommender.get_recommendation(scores[active_player])
        if double_out_recommendation and len(double_out_recommendation)<=3-throw_number:
            score_recommendation = recommender.get_recommendation(scores[active_player])

    # Check if player has won, the leg and / or the game
    just_won, winner_index, playing= gameRef.has_just_won()
    game_over = gameRef.is_game_over()

    # Prepare display score
    display_score = f"{multiplier}x{base_score}" if multiplier > 1 else str(base_score)
    
    return jsonify({
        "received": base_score,
        "multiplier": multiplier,
        "displayScore": display_score,
        "scoreA": scores[0],
        "scoreB": scores[1],
        "currentThrows": current_throws,
        "isRoundComplete": gameRef.current_leg.change,
        "isBust": gameRef.is_bust,
        "justWon": just_won,
        "GameOver": game_over,
        "winnerIndex": winner_index if just_won else -1,
        "scoreRecommendation": score_recommendation,
        "currentPlayer": gameRef.current_leg.player_index
    })

@app.route("/undo_throw", methods=["POST"])
def undo_throw():
    if gameRef.undo_last_dart():
        scores = gameRef.get_totals()
        return jsonify({
            "success": True,
            "currentThrows": gameRef.get_scores(),
            "scoreA": scores[0],
            "scoreB": scores[1],
        })
    return jsonify({'success': False, 'error': 'No throws to undo'}), 400

@app.route("/save_game", methods=["POST"])
def save_game():
    scoreA, scoreB = gameRef.get_totals()
    playerA, playerB = [p.name for p in gameRef.players]
    game_mode = gameRef.format

    conn = aid_functions_sql.get_db_connection()
    cursor = conn.cursor()

    try:
        loaded_game_id = session.get("loaded_game_id")

        if loaded_game_id:
            # Update vorhandenes Spiel
            cursor.execute("""
                UPDATE game
                SET game_mode = %s,
                    player_A = %s,
                    player_B = %s,
                    score_player_A = %s,
                    score_player_B = %s
                WHERE game_id = %s
            """, (game_mode, playerA, playerB, scoreA, scoreB, loaded_game_id))
            print(f"Aktualisiertes Spiel-ID: {loaded_game_id}")
        else:
            # Neues Spiel speichern
            cursor.execute("""
                INSERT INTO game (game_mode, player_A, player_B, score_player_A, score_player_B)
                VALUES (%s, %s, %s, %s, %s)
            """, (game_mode, playerA, playerB, scoreA, scoreB))
            print("Neues Spiel gespeichert")

        conn.commit()
        return jsonify({"success": True})

    except Error as e:
        print(f"Fehler beim Speichern: {str(e)}")
        return jsonify({"success": False})

    finally:
        cursor.close()
        conn.close()

@app.route("/load_game", methods=["POST"])
def load_game():
    game_id = request.form.get("game_id")
    if not game_id:
        return redirect("/play")

    conn = aid_functions_sql.get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM game WHERE game_id = %s", (game_id,))
        game_data = cursor.fetchone()
        
        if not game_data:
            print(f"Kein Spiel mit ID {game_id} gefunden.")
            return jsonify({"error": f"Kein Spiel mit ID {game_id} gefunden."}), 404 # status 404 = nicht gefunden
        session["loaded_game_id"] = game_id  # Spiel-ID merken
        gameRef.start_game(1, game_data["game_mode"], game_data["player_A"], game_data["player_B"])
        gameRef.players[0].total_score = game_data["score_player_A"]
        gameRef.players[1].total_score = game_data["score_player_B"]
        
        ### ---> add the correct data from MARIADB HERE
        name_a  = game_data["player_A"]
        name_b  = game_data["player_B"]
        game_mode = game_data["game_mode"]
        return jsonify({"namePlayerA": name_a,
                        "namePlayerB": name_b,
                        "scorePlayerA": game_data["score_player_A"],
                        "scorePlayerB": game_data["score_player_B"],
                        "gamemode": game_mode, 
                        "redirect_url": f'/game/{name_a}/{name_b}/{game_mode}/1'})
        # return redirect(f'/game/{game_data["player_A"]}/{game_data["player_B"]}/{game_data["game_mode"]}/1') 
        #statt redirect 4 elemente aus db ls json zurückgeben!!! weiterverarbeitet im js

    except Error as e:
        print(f"Fehler beim Laden des Spiels: {str(e)}")
        return redirect("/play")

    finally:
        cursor.close()
        conn.close()

@app.route("/current-game")
def return_to_game():
    if gameRef.playing:
        scores = gameRef.get_totals()
        if scores != -1:
            return redirect(f'/game/{gameRef.players[0].name}/{gameRef.players[1].name}/{gameRef.format}/{gameRef.first_to}')
    return redirect('/play')

@app.route("/reset_chat", methods=["POST"])
def reset_chat():
    session.pop("chat_history", None)
    return jsonify({"status": "ok"})

@app.route("/get_score_prediction", methods = ["GET"])
def get_score_prediction():
    def random_dart_score():
        # Choose a base score from 0, 1–20, or 25
        score = random.choice([0] + list(range(1, 21)) + [25])
        
        # Determine allowed multiplier based on score
        if score == 0:
            multiplier = 1
        elif score == 25:
            multiplier = random.choice([1, 2])
        else:
            multiplier = random.choice([1, 2, 3])
        
        # Return JSON-serializable result
        return score, multiplier
    score_prediction = random_dart_score()
    return jsonify({"score": score_prediction[0], "multiplier": score_prediction[1]})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
