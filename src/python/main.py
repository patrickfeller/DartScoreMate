from flask import Flask, render_template, request, redirect, jsonify, Response
import gamedata
import camera_handling
import cv2 

# Shared thread references, currently not clear why needed
adminRef = gamedata.Admin()
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
    return jsonify({"success": True})

if __name__=="__main__":
    app.run(port=5000,debug=True)
