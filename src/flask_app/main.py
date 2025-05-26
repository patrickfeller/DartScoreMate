# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, jsonify, Response, session
import gamedata
import camera_handling
import cv2 
from flask_session import Session
from dotenv import load_dotenv
from mysql.connector.errors import Error
import aid_functions_sql 
import recommender
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
    format = int(format)
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
    try:
        # extract game values safely and store them in mariadb
        scoreA, scoreB = gameRef.get_totals()
        player_names = [p.name for p in getattr(gameRef,"players", [])]
        playerA, playerB = (player_names + [None, None])[:2]
        game_mode = getattr(gameRef,"format", 501)
        legs_played = len(getattr(gameRef, "legs_played", []))
        active_player = getattr(getattr(getattr(gameRef, "current_leg", None), "current_player", None), "name", None)
        throw_1, throw_2,throw_3 = gameRef.get_scores()
        
        # Validate required (NOT NULL) fields

        required_fields = [game_mode, scoreA, scoreB, throw_1, throw_2, throw_3]
        if any(val is None for val in required_fields):
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        
        conn = aid_functions_sql.get_db_connection()
        cursor = conn.cursor()

        loaded_game_id = session.get("loaded_game_id")

        if loaded_game_id:
            # Update existing game
            cursor.execute("""
                UPDATE game
                SET game_mode = %s,
                    player_A = %s,
                    player_B = %s,
                    score_player_A = %s,
                    score_player_B = %s,
                    active_player = %s,
                    throw_1 = %s,
                    throw_2 = %s,
                    throw_3 = %s,
                    legs_played = %s
                WHERE game_id = %s
            """, (
                game_mode, playerA, playerB,
                scoreA, scoreB, active_player,
                throw_1, throw_2, throw_3,
                legs_played, loaded_game_id
            ))
            print(f"Aktualisiertes Spiel-ID: {loaded_game_id}")
        else:
            # Insert new game
            cursor.execute("""
                INSERT INTO game (
                    game_mode, player_A, player_B,
                    score_player_A, score_player_B,
                    active_player, throw_1, throw_2, throw_3, legs_played
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                game_mode, playerA, playerB,
                scoreA, scoreB, active_player,
                throw_1, throw_2, throw_3,
                legs_played
            ))
            new_game_id = cursor.lastrowid
            print("Neues Spiel gespeichert")

        conn.commit()
        return jsonify({"success": True, "game_id": new_game_id})

    except Exception as e:
        print(f"Fehler beim Speichern: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        try:
            if cursor: cursor.close()
            if conn and conn.is_connected(): conn.close()
        except:
            pass

@app.route("/chat", methods=["POST"])
# a route to chat with an llm
def chat():
    api_key = os.getenv("GROQ_API_KEY", "")
    if api_key:
            # Groq Client Setup
        client = Groq(
            api_key=api_key
        )
        try:
            # Debug-Ausgabe für die Anfrage
            print("Empfangene Anfrage:", request.json)
            
            # Hole die Nachricht aus der Anfrage
            user_message = request.json.get("message", "")
            if not user_message:
                return jsonify({"error": "Keine Nachricht empfangen"}), 400
                
            print("Verarbeite Nachricht:", user_message)  # Debug-Ausgabe
            
            prompt = """
                        Du bist Mrs. Darts, ein Experte im Dartspielen. Beantworte alle Fragen rund 
                        um das Dartspielen, einschließlich Regeln, Techniken, Ausrüstung und Geschichte. 
                        Sei freundlich und hilfreich."
            """

            # Starte die Nachrichtenliste mit dem Systemprompt
            messages = [{"role": "system", "content": prompt}]

           # Füge bisherige Chat-Historie hinzu
            history = session.get("chat_history", [])

            for entry in history:
                messages.append({"role": "user", "content": entry["user"]})
                messages.append({"role": "assistant", "content": entry["bot"]})

            messages.append({"role": "user", "content": user_message})
            try:
                # Groq API aufrufen
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0.7,
                    max_completion_tokens=1024,
                    top_p=1,
                    stream=False
                )
            except AuthenticationError as auth_error:
                return jsonify({"error": "Unauthorized API key", "details": str(auth_error)}), 401
            
            response = completion.choices[0].message.content
            print("Antwort von Groq API erhalten:", response)  # Debug-Ausgabe
            
            # Chat-Historie speichern in der Session
            chat_entry = {
                "user": user_message,
                "bot": response
            }

            # Wenn noch keine Historie existiert, neue Liste starten
            if "chat_history" not in session:
                session["chat_history"] = []

            session["chat_history"].append(chat_entry)
            session.modified = True  # Wichtig, damit Flask die Session wirklich speichert
            # print("Chat-Historie gespeichert:", session.get("chat_history")) #Debug Assitent um zu Testen ob Historie gespeichert


            return jsonify({
                "response": response
            })
        
        except Exception as e:
            print("Fehler aufgetreten:", str(e))  # Debug-Ausgabe
            print("Fehlertyp:", type(e).__name__)  # Debug-Ausgabe
            return jsonify({
                "error": str(e),
                "error_type": type(e).__name__,
                "details": "Bitte überprüfen Sie die Server-Logs für mehr Details."
            }), 500
    else:
        return jsonify({"response": "This service is currently not available - no api-key provided."}), 401

@app.route("/chat_history", methods=["GET"])
def get_chat_history():
    chat_history = session.get("chat_history", [])
    return jsonify(chat_history)

@app.route("/load_game", methods=["POST"])
# load a previous game from MariaDB by ID
def load_game():
    game_id = request.form.get("game_id")
    if not game_id:
        return jsonify({"error": "No Game-ID provided"}), 400

    conn = aid_functions_sql.get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM game WHERE game_id = %s", (game_id,)) # get all the information linked to the gameID
        game_data = cursor.fetchone()
        
        if not game_data:
            print(f"Kein Spiel mit ID {game_id} gefunden.")
            return jsonify({"error": f"Kein Spiel mit ID {game_id} gefunden."}), 404 # status 404 = nicht gefunden
        session["loaded_game_id"] = game_id  # Spiel-ID merken
        gameRef.start_game(1, game_data["game_mode"], game_data["player_A"], game_data["player_B"])
        gameRef.players[0].total_score = game_data["score_player_A"]
        gameRef.players[1].total_score = game_data["score_player_B"]
        
        playerA_Name  = game_data["player_A"]
        playerB_Name  = game_data["player_B"]
        game_mode = game_data["game_mode"]
        return jsonify({"namePlayerA": playerA_Name,
                        "namePlayerB": playerB_Name,
                        "scorePlayerA": game_data["score_player_A"],
                        "scorePlayerB": game_data["score_player_B"],
                        "gamemode": game_mode, 
                        "redirect_url": f'/game/{playerA_Name}/{playerB_Name}/{game_mode}/1'})
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
