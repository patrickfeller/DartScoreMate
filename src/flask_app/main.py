# -*- coding: utf-8 -*-
import os
import cv2
from flask import Flask, render_template, request, redirect, jsonify, Response, session
from flask_session import Session
from dotenv import load_dotenv
from mysql.connector.errors import Error
from groq import Groq

import gamedata
import camera_handling
import aid_functions_sql
import recommender

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY', "")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Initialize game references
adminRef = gamedata.Admin()
gameRef = gamedata.Game()

# Flask setup
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")
app.config.update(
    SESSION_TYPE="filesystem",
    SESSION_PERMANENT=False,
)
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
    return render_template('game.html', playerA=playerA, playerB=playerB, format=int(format),
                           scoreA=scores[0], scoreB=scores[1])

@app.route("/throw")
def handle_throw():
    throw_number = int(request.args.get('throwNumber', 1))
    base_score = int(request.args.get('score', 0))
    multiplier = int(request.args.get('multiplier', 1))

    dart = gamedata.Dart(base_score, multiplier, None)
    gameRef.dart(dart)

    scores = gameRef.get_totals()
    current_throws = gameRef.get_scores()
    active_player = gameRef.current_leg.player_index
    recommendation = recommender.get_recommendation(scores[active_player]) if throw_number < 3 else 0

    just_won, winner_index = gameRef.has_just_won()
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
        "winnerIndex": winner_index if just_won else -1,
        "scoreRecommendation": recommendation
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
        return jsonify({"namePlayerA": "Gustaf",
                        "namePlayerB": "Bernd",
                        "scorePlayerA": 300,
                        "scorePlayerB": 200})
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

@app.route("/get_score_recommendation", methods=["POST"])
def get_score_recommendation():
    data = request.get_json()
    current_score = data.get('score')

    if current_score is None:
        return jsonify({'scoreRecommendation': 0}), 400

    return jsonify({'scoreRecommendation': recommender.get_recommendation(current_score)})

@app.route("/chat", methods=["POST"])
def chat():
    if not client:
        return jsonify({"response": "Chat-Service aktuell nicht verfügbar (kein API-Key)."})

    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"error": "Keine Nachricht empfangen"}), 400

    prompt = (
        "Du bist Mrs. Darts, ein Experte im Dartspielen. Beantworte Fragen zu Regeln, Technik, Ausrüstung usw."
    )

    messages = [{"role": "system", "content": prompt}]
    for entry in session.get("chat_history", []):
        messages.extend([
            {"role": "user", "content": entry["user"]},
            {"role": "assistant", "content": entry["bot"]}
        ])
    messages.append({"role": "user", "content": user_message})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_completion_tokens=1024,
            top_p=1,
            stream=False
        )
        response = completion.choices[0].message.content
        session.setdefault("chat_history", []).append({"user": user_message, "bot": response})
        session.modified = True
        return jsonify({"response": response})

    except Exception as e:
        return jsonify({
            "error": str(e),
            "error_type": type(e).__name__,
            "details": "Bitte Server-Logs prüfen."
        }), 500

@app.route("/chat_history", methods=["GET"])
def get_chat_history():
    return jsonify(session.get("chat_history", []))

@app.route("/reset_chat", methods=["POST"])
def reset_chat():
    session.pop("chat_history", None)
    return jsonify({"status": "ok"})

# ------------------------- APP START -------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
