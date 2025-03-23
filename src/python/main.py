# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, jsonify
import gamedata
import os
from dotenv import load_dotenv
from groq import Groq

# Lade Umgebungsvariablen
load_dotenv()

# Debug-Ausgaben
print("Aktuelles Verzeichnis:", os.getcwd())
print("Umgebungsvariablen geladen:", os.getenv('OPENAI_API_KEY') is not None)
print("API Key Länge:", len(os.getenv('OPENAI_API_KEY', '')))

# Groq Client Setup
client = Groq(
    api_key=os.getenv('OPENAI_API_KEY')
)

# Shared thread references, currently not clear why needed
adminRef = None
gameRef = gamedata.Game()
lockRef = None

# Add session storage for throws and multiplier
current_throws = {1: 0, 2: 0, 3: 0}
current_multiplier = 1

app = Flask(__name__)

@app.route("/")
@app.route("/play")
def play():
    return render_template("play.html")

# Main page for the game
@app.route("/board-status")
def boardstatus():
    return render_template("board-status.html")
 
# Route when Play-button get pressed
@app.route("/new_game", methods=["POST"])
def new_game():
    format = int(request.form['game-type'])
    first_to = int(request.form['legs'])
    playerA = request.form['player1name']
    playerB = request.form['player2name']
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
    
    # Create a dart object
    dart = gamedata.Dart(base_score, multiplier, None)  # Position is None as we don't use camera
    
    # Try to make the throw
    gameRef.dart(dart)
    
    
    # Get updated game state
    scores = gameRef.get_totals()
    current_throws = gameRef.get_scores()
    current_player_throws = current_throws[gameRef.current_leg.player_index]
    
    # Check if player has won
    just_won, winner_index = gameRef.has_just_won()
    
    # Prepare display score
    display_score = f"{multiplier}×{base_score}" if multiplier > 1 else str(base_score)
    
    return jsonify({
        "received": base_score,
        "multiplier": multiplier,
        "displayScore": display_score,
        "scoreA": scores[0],
        "scoreB": scores[1],
        "currentThrows": current_player_throws,
        "isRoundComplete": gameRef.current_leg.change,
        "justWon": just_won,
        "winnerIndex": winner_index if just_won else -1
    })

@app.route("/undo")
def undo_throw():
    # TODO: Implement undo functionality
    return jsonify({"success": True})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        # Debug-Ausgabe für die Anfrage
        print("Empfangene Anfrage:", request.json)
        
        # Hole die Nachricht aus der Anfrage
        user_message = request.json.get("message", "")
        if not user_message:
            return jsonify({"error": "Keine Nachricht empfangen"}), 400
            
        print("Verarbeite Nachricht:", user_message)  # Debug-Ausgabe
        
        # Groq API aufrufen
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Du bist Mrs. Darts, ein Experte im Dartspielen. Beantworte alle Fragen rund um das Dartspielen, einschließlich Regeln, Techniken, Ausrüstung und Geschichte. Sei freundlich und hilfreich."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_completion_tokens=1024,
            top_p=1,
            stream=False
        )
        
        response = completion.choices[0].message.content
        print("Antwort von Groq API erhalten:", response)  # Debug-Ausgabe
        
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

if __name__=="__main__":
    app.run(port=5000,debug=True)
