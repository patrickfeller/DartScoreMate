# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, jsonify, Response, session
import gamedata
import camera_handling
import cv2 
import os
from dotenv import load_dotenv
from groq import Groq
import aid_functions_sql 
from mysql.connector.errors import Error
import recommender
from flask_session import Session




# load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY',"")# fallback value emptystring

if GROQ_API_KEY:
    # Debug-Ausgaben
    print("Aktuelles Verzeichnis:", os.getcwd())
    print("Umgebungsvariablen geladen:", os.getenv('OPENAI_API_KEY') is not None)
    print("API Key Länge:", len(os.getenv('OPENAI_API_KEY', '')))

    # Groq Client Setup
    client = Groq(
        api_key=GROQ_API_KEY
    )

# Shared thread references, currently not clear why needed
adminRef = gamedata.Admin()
gameRef = gamedata.Game()
lockRef = None

# Add session storage for throws and multiplier
current_throws = {1: 0, 2: 0, 3: 0}
current_multiplier = 1

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Kann auch aus .env kommen
app.config["SESSION_TYPE"] = "filesystem"  # Damit wird die Session serverseitig gespeichert
app.config["SESSION_PERMANENT"] = False
Session(app)

Session(app)


@app.route("/")
@app.route("/play")
def play():
    return render_template("play.html")


# Main page for the game
@app.route("/board-status")
def boardstatus():
    cam = camera_handling.camera()
    available_cameras = cam.get_available_cameras()
    # TODO: Camera settings are not yet implemented
    resulution_options = cam.resulution_options
    fps_options = cam.fps_options    
    return render_template("board-status.html", avaiable_cameras = available_cameras, resulution_options = resulution_options, fps_options = fps_options)   

# Convert still camera frames to video
def generate_frames(camera_id):
    camera = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    try:
        while True:
            success, frame = camera.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpeg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                      b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        camera.release() 

# Routing for video feed
@app.route('/video_feed')
def video_feed():
    camera_id = request.args.get('camera_id', default=0, type=int)
    return Response(generate_frames(camera_id), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

# Route when Play-button get pressed
@app.route("/new_game", methods=["POST"])
def new_game():
    format = int(request.form['game-type'])
    first_to = int(request.form['legs'])
    playerA = request.form['player1name']
    playerB = request.form['player2name']
    # -> transfer to MariaDB
    # Initialize new game with player names and format
    gameRef.start_game(first_to, format, playerA, playerB)
    return redirect('/game/'+playerA+'/'+playerB+'/'+str(format)+'/'+str(first_to))


# Route bevore new_game starts
@app.route('/game/<playerA>/<playerB>/<format>/<first_to>')
def game(playerA, playerB, format, first_to):
    format = int(format)
    scores = gameRef.get_totals()
    return render_template('game.html', playerA=playerA, playerB=playerB, format=format, 
                         scoreA=scores[0], scoreB=scores[1])


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

    # Check if player has won
    just_won, winner_index = gameRef.has_just_won()

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
        "isBust": gameRef.is_bust,  # Add this new flag
        "justWon": just_won,
        "winnerIndex": winner_index if just_won else -1,
        "scoreRecommendation": score_recommendation
    })


# Route to undo the last dart throw, if possible
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

@app.route("/next")
def next_player():
    # TODO: Implement next functionality, if needed
    return jsonify({"success": True})

@app.route("/chat", methods=["POST"])
def chat():
    if GROQ_API_KEY:
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
 
            # Groq API aufrufen
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_completion_tokens=1024,
                top_p=1,
                stream=False
            )
            
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
        return jsonify({"response": "This service is currently not available - no api-key provided."})

@app.route("/chat_history", methods=["GET"])
def get_chat_history():
    chat_history = session.get("chat_history", [])
    return jsonify(chat_history)

@app.route("/save_game", methods=["POST"])
def save_game():
    # list of scores for each player
    score_player_A, score_player_B = gameRef.get_totals()
    # list of players
    player_A, player_B = [player.name for player in gameRef.players]
    
    # played gamemode eg. 501
    game_mode = gameRef.format
    
    conn = aid_functions_sql.get_db_connection()
    cursor = conn.cursor()
   
    try:
        cursor.execute("INSERT INTO game (game_mode, player_A, player_B, score_player_A, score_player_B) VALUES (%s, %s, %s, %s, %s)", (game_mode, player_A, player_B, score_player_A, score_player_B))
        conn.commit()
    
    except Error as e:
        print(f"An error occured, {str(e)}")
        return jsonify({"sucess": False})
    
    finally:
        cursor.close()
        conn.close()

    return jsonify({"success": True})


@app.route('/get_score_recommendation', methods=["POST"])
def get_score_recommendation():
    # Get the incoming data (the current score)
    data = request.get_json()  # This will be the JSON sent from the frontend
    current_score = data.get('score')

    if current_score:
        # Get the recommendations based on the current score
        recommendations = recommender.get_recommendation(current_score)

        # Return the recommendations as a JSON response
        return jsonify({'scoreRecommendation': recommendations})
    else:
        # If no score is provided, return an empty array or error message
        return jsonify({'scoreRecommendation': 0}), 400


@app.route("/current-game")
def return_to_game():
    # Check if there's an active game
    if gameRef.playing:
        scores = gameRef.get_totals()
        if scores != -1:  # Game exists
            playerA = gameRef.players[0].name
            playerB = gameRef.players[1].name
            format = gameRef.format
            first_to = gameRef.first_to
            return redirect(f'/game/{playerA}/{playerB}/{format}/{first_to}')
    # If no active game, redirect to new game page
    return redirect('/play')

@app.route("/reset_chat", methods=["POST"])
def reset_chat():
    session.pop("chat_history", None)
    return jsonify({"status": "ok"})

@app.route("/load_game",methods=["POST"])
def load_game():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
