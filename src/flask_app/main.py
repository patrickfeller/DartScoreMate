from flask import Flask, render_template, request, redirect, jsonify
import gamedata

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
    # -> transfer to MariaDB
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
        "currentThrows": current_throws,
        "isRoundComplete": gameRef.current_leg.change,
        "justWon": just_won,
        "winnerIndex": winner_index if just_won else -1
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

if __name__=="__main__":
    app.run(port=5000,debug=True)
