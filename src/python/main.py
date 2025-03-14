from flask import Flask, render_template, request, redirect, jsonify
import gamedata

# Shared thread references, currently not clear why needed
adminRef = None
gameRef = None
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
    return redirect('/game/'+playerA+'/'+playerB+'/'+str(format)+'/'+str(first_to))

# Route bevore new_game starts
@app.route('/game/<playerA>/<playerB>/<format>/<first_to>')
def game(playerA, playerB, format, first_to):
    # not sure why these are not working
    # a_wins = gameRef.players[0].wins
    # b_wins = gameRef.players[1].wins
    return render_template('game.html', playerA=playerA, playerB=playerB, total=format)

# Route for handling throws
@app.route("/throw")
def handle_throw():
    throw_number = int(request.args.get('throwNumber', 1))
    base_score = int(request.args.get('score', 0))
    multiplier = int(request.args.get('multiplier', 1))
    
    # Calculate final score with multiplier
    final_score = base_score * multiplier
    
    # Store the throw
    current_throws[throw_number] = final_score
    
    # Calculate running total
    current_total = sum(current_throws.values())
    
    # Prepare display score (e.g., "2×20" for double 20)
    display_score = f"{multiplier}×{base_score}" if multiplier > 1 else str(base_score)
    
    # If this was the third throw, reset for next round
    is_round_complete = throw_number == 3
    if is_round_complete:
        current_throws.update({1: 0, 2: 0, 3: 0})
    
    return jsonify({
        "received": base_score,
        "multiplier": multiplier,
        "displayScore": display_score,
        "total": current_total,
        "isRoundComplete": is_round_complete
    })

if __name__=="__main__":
    app.run(port=5000,debug=True)
