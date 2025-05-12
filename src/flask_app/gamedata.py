# copied from gitProject, not all of this should be needed

from enum import Enum


class CameraMode(Enum):
    """Represents the different operational modes of the camera system."""
    OFF = 'OFF'
    ON = 'ON'
    POSITIONING = 'POSITIONING'
    GAME = 'GAME'


class Admin:
    """Manages administrative settings and camera control for the dart system.
    
    Handles camera mode switching, frame buffering, and game assistance features.
    """
    def __init__(self):
        self.mode = CameraMode.OFF
        self.frames = [None, None, None]
        self.aimbot = None
        self.center_line = False
        self.skills = []


class Dart:
    """Represents a single dart throw in the game.
    
    Contains information about the score, multiplier and physical position of the dart.
    
    :param score: The base numerical score of the throw
    :type score: int
    :param multiplier: The score multiplier (1, 2 for double, 3 for triple)
    :type multiplier: int
    :param position: The physical coordinates of where the dart landed
    :type position: tuple
    """
    STRING_REP = ('', 'S', 'D', 'T')

    def __init__(self, score, multiplier, position):
        self.score = int(score)
        self.multiplier = int(multiplier)
        self.position = position

    def value(self):
        """Calculate the total score value of the dart throw.
        
        :return: The product of score and multiplier
        :rtype: int
        """
        return self.score * self.multiplier
    
    def is_double(self):
        """Check if the dart hit a double segment.
        
        :return: True if multiplier is 2, False otherwise
        :rtype: bool
        """
        return self.multiplier == 2

    def to_string(self):
        """Convert the dart throw to its string representation.
        
        :return: String representation of the throw (e.g., 'D20' for double 20)
        :rtype: str
        """
        return self.STRING_REP[self.multiplier] + str(self.score)
    
    def is_bust(self):
        """Check if this dart resulted in a bust.
        
        :return: Always False for regular darts
        :rtype: bool
        """
        return False
    
    def get_position(self):
        """Get the physical position where the dart landed.
        
        :return: Position coordinates of the dart
        :rtype: tuple
        """
        return self.position

class Bust(Dart):
    """
    subclass of Dart that represents a "bust" in darts - a situation where a player's throw results in an invalid score
    In dart games, a "bust" occurs when:
    * The throw would reduce the score below zero
    * The throw would leave exactly 1 point remaining (if double-out is required)
    * The throw would bring the score to zero but wasn't a double (when double-out is required)
    """
    def __init__(self, dart):
        super().__init__(dart.score, dart.multiplier, dart.position)

    def is_bust(self):
        return True
    
    def value(self):
        return 0
    
    def to_string(self):
        return 'BUST'


class Turn:
    """Manages a single player's turn of up to three darts.
    
    Tracks dart throws and handles scoring and bust scenarios.
    
    :param player: The player taking the turn
    :type player: Player
    """
    def __init__(self, player):
        self.darts = []
        self.player = player
        self.dart_score_image_frames = {
            "camera_A": {"last_frame": None, "new_actual_frame": None}, 
            "camera_B": {"last_frame": None, "new_actual_frame": None},
            "camera_C": {"last_frame": None, "new_actual_frame": None}
            }
        self.__dart_score_image_frame_buffer = None
    
    def dart(self, dart):
        """Add a new dart throw to the turn.
        
        :param dart: The dart to add to this turn
        :type dart: Dart
        """
        self.darts.append(dart)

    def bust(self, dart):
        """Handle a bust situation in the turn.
        
        Undoes all previous darts in the turn and adds a bust marker.
        
        :param dart: The dart that caused the bust
        :type dart: Dart
        """
        for i in self.darts:
            self.player.undo_dart(i)    # undo score of current player
        self.darts.append(Bust(dart))

    def display(self):
        """Display the current turn's throws as a list of strings.
        
        :return: List of three strings representing the throws ('-' for empty throws)
        :rtype: list[str]
        """
        representation = ['-', '-', '-']
        print(f"Current darts in turn: {len(self.darts)}")
        for i in range(min(3, len(self.darts))):
            print(f"Converting dart {i}: {self.darts[i].to_string()}")
            dart_value = self.darts[i].to_string()
            representation[i] = dart_value       
        print(f"Final representation: {representation}")
        return representation

    def is_over(self):
        if len(self.darts) == 0:
            return False        
        return len(self.darts) >= 3 or self.darts[-1].is_bust()
    
    def undo_last_dart(self):
        if self.darts:
            last_dart = self.darts.pop()
            if not last_dart.is_bust():
                self.player.undo_dart(last_dart)
            else:
                # If it was a bust, restore all previous darts
                for dart in self.darts:
                    self.player.dart(dart)
            return last_dart
        return None
    

    
    def update_current_dart_score_raw_image_frames(self, raw_dart_frame_camera_A, raw_dart_frame_camera_B, raw_dart_frame_camera_C):
        self.dart_score_image_frames["camera_A"]["last_frame"] = self.dart_score_image_frames["camera_A"]["new_actual_frame"]
        self.dart_score_image_frames["camera_B"]["last_frame"] = self.dart_score_image_frames["camera_B"]["new_actual_frame"]
        self.dart_score_image_frames["camera_C"]["last_frame"] = self.dart_score_image_frames["camera_C"]["new_actual_frame"]

        self.dart_score_image_frames["camera_A"]["new_actual_frame"] = raw_dart_frame_camera_A
        self.dart_score_image_frames["camera_B"]["new_actual_frame"] = raw_dart_frame_camera_B
        self.dart_score_image_frames["camera_C"]["new_actual_frame"] = raw_dart_frame_camera_C

    def update_current_dart_score_raw_image_frames_from_buffer(self):
        try:
            self.dart_score_image_frames["camera_A"]["last_frame"] = self.dart_score_image_frames["camera_A"]["new_actual_frame"]
            self.dart_score_image_frames["camera_B"]["last_frame"] = self.dart_score_image_frames["camera_B"]["new_actual_frame"]
            self.dart_score_image_frames["camera_C"]["last_frame"] = self.dart_score_image_frames["camera_C"]["new_actual_frame"]

            self.dart_score_image_frames["camera_A"]["new_actual_frame"] = self.__dart_score_image_frame_buffer["camera_A"]
            self.dart_score_image_frames["camera_B"]["new_actual_frame"] = self.__dart_score_image_frame_buffer["camera_B"]
            self.dart_score_image_frames["camera_C"]["new_actual_frame"] = self.__dart_score_image_frame_buffer["camera_C"]

            self.__clear_dart_score_image_frame_buffer()
        except Exception as e:
            # Logging ?
            raise e

    def set_dart_score_image_frame_buffer(self, raw_dart_frame_camera_A, raw_dart_frame_camera_B, raw_dart_frame_camera_C):
        self.__dart_score_image_frame_buffer = {
            "camera_A": raw_dart_frame_camera_A, 
            "camera_B": raw_dart_frame_camera_B,
            "camera_C": raw_dart_frame_camera_C
            }
        
    def check_dart_score_image_frame_buffer_is_None(self):
        return self.__dart_score_image_frame_buffer == None
    
    def __clear_dart_score_image_frame_buffer(self):
        self.__dart_score_image_frame_buffer = None
    

class Leg:
    """Represents one leg of a dart game.
    
    Manages turns between players until someone wins the leg.
    
    :param players: List containing both players
    :type players: list[Player]
    :param current_player: Index of starting player
    :type current_player: int
    """
    def __init__(self, players, current_player): # is currnet_player index with 0 and 1 of len Leg correct?
        self.current_turn = Turn(players[current_player])
        self.turns = [self.current_turn]
        self.winner = None
        self.players = players
        self.current_player = self.players[current_player]
        self.player_index = current_player
        self.change = False
        self.last_completed_throws = ['-', '-', '-']  # Add this line
    
    def dart(self, dart):
        """Process a dart throw in the current turn.
        
        Updates scores and handles player changes when needed.
        
        :param dart: The dart being thrown
        :type dart: Dart
        """
        if not self.current_player.is_bust(dart):
            self.current_turn.dart(dart)    # update throws current turn
            self.current_player.dart(dart)  # update score current player
        else:
            self.current_turn.bust(dart)

        if self.current_turn.is_over():
            self.last_completed_throws = self.current_turn.display()
            self.changeover()

    def get_last_turn(self, player):
        """Get the display representation of a player's last completed turn.
        
        :param player: The player whose last turn to retrieve
        :type player: Player
        :return: List of three strings representing the throws
        :rtype: list[str]
        """
        for turn in reversed(self.turns):
            if turn.player == player:
                return turn.display()
        
        return ['-', '-', '-']

    def changeover(self):
        """Handle the transition between players at the end of a turn.
        
        Updates the current player and initializes a new turn.
        """
        self.change = True  
        self.last_completed_throws = self.current_turn.display()  # Store last throws before changing
        self.player_index = (self.player_index + 1) % 2
        self.current_player = self.players[self.player_index]
        self.current_turn = Turn(self.current_player)  # Create new turn with empty throws
        self.turns.append(self.current_turn)
    
    def undo_last_dart(self):
        if self.current_turn.darts: # If there are darts in current turn
            return self.current_turn.undo_last_dart()
        elif len(self.turns) > 1: # Or if we can go back to previous turn
            # If current turn is empty, go back to previous turn
            self.turns.pop()  # Remove current empty turn
            self.current_turn = self.turns[-1]
            self.current_player = self.current_turn.player
            self.player_index = self.players.index(self.current_player)
            return self.current_turn.undo_last_dart()
        return None


class Player:
    """Represents a player in the dart game.
    
    Tracks player's score, wins, and handles scoring logic.
    
    :param name: The player's name
    :type name: str
    :param format: The starting score for this game format
    :type format: int
    """
    def __init__(self, name, format):
        self.name = name
        self.format = format
        self.score = format
        self.wins = 0

    def dart(self, dart):
        """Process a dart throw and update the player's score.
        
        :param dart: The dart to process
        :type dart: Dart
        """
        self.score -= dart.value()

    def undo_dart(self, dart):
        """Undo the last dart throw and restore the player's score.
        
        :param dart: The dart to undo
        :type dart: Dart
        """
        self.score += dart.value()
        
    def is_bust(self, dart):
        """Check if a dart throw results in a bust.
        
        :param dart: The dart to check
        :type dart: Dart
        :return: True if the throw results in a bust, False otherwise
        :rtype: bool
        """
        result = self.score - dart.value()
        if result < 0: # add if doubl-out is involved: == 1 or result
            return True
        # uncomment if double-out is involved:
        # if result == 0 and not dart.is_double:
        #     return True
        return False
    
    def has_won(self):
        """Check if the player has won the game.
        
        :return: True if the player's score is zero, False otherwise
        :rtype: bool
        """
        return self.score == 0

    def reset(self):
        """Reset the player's score to the initial format."""
        self.score = self.format


class Game:
    """Manages the complete dart game session.
    
    Controls game flow, player turns, and scoring across multiple legs.
    """
    def __init__(self):
        self.positions = []
        self.new_positions = []
        self.playing = False
        self.update = False
        self.current_leg = None
        self.is_bust = False
        self.winner_index = None
        self.dart_score_basis_image_frames = {
            "camera_A": None, 
            "camera_B": None,
            "camera_C": None
            }

    def start_game(self, first_to, format, name_a, name_b):
        """Initialize a new game with the specified parameters.
        
        :param first_to: Number of legs needed to win the match
        :type first_to: int
        :param format: Starting score (e.g., 501)
        :type format: int
        :param name_a: First player's name
        :type name_a: str
        :param name_b: Second player's name
        :type name_b: str
        """
        self.first_to = first_to
        self.players = (Player(name_a, format), Player(name_b, format))   
        self.legs_played = []
        self.current_leg = Leg(self.players, len(self.legs_played) % 2)
        self.format = format             
        self.playing = True
        self.update = True
        self.clear = False
        self.just_won = False

    def dart(self, dart):
        """Process a dart throw in the current game.
        
        :param dart: The dart being thrown
        :type dart: Dart
        """
        self.is_bust = self.current_leg.current_player.is_bust(dart)
        self.current_leg.dart(dart) # Leg([players], current_player 0/1).Dart
        self.has_won()
        self.update = True

    def has_won(self):
        """Check if any player has won the current leg.
        
        Updates the winner and resets the game state if a player has won.
        """
        for i, player in enumerate(self.players):
            if player.has_won():
                self.current_leg.winner = player
                player.wins += 1
                self.winner_index = i  # Store the winning player's index
                self.reset()
                self.legs_played.append(self.current_leg)
                self.current_leg = Leg(self.players, len(self.legs_played) % 2)
                self.just_won = True
    
    def get_scores(self):
        """Retrieve current turn's dart throws.
        
        :return: List of three strings representing current throws
        :rtype: list[str]
        """
        if self.playing and self.current_leg:
            return self.current_leg.current_turn.display()  # Always return current turn's throws
        return ['-', '-', '-']
    
    def get_wins(self):
        """Get the current win count for both players.
        
        :return: List of wins for both players or -1 if game not active
        :rtype: list[int] or int
        """
        if self.playing == True:
            return [self.players[0].wins, self.players[1].wins]
        else:
            return -1
    
    def get_totals(self):
        """Get current scores for both players.
        
        :return: List of current scores or -1 if game not active
        :rtype: list[int] or int
        """
        if self.playing:
            return [self.players[0].score, self.players[1].score]
        else:
            return -1
    
    def new_dart(self, dart):
        """Register a new dart throw in the game.
        
        :param dart: The new dart to be added
        :type dart: Dart
        """
        self.positions.append(dart)
        self.new_positions.append(dart)

    def get_positions(self):
        """Get the positions of all thrown darts.
        
        :return: List of positions for all darts thrown
        :rtype: list[tuple]
        """
        return [x.get_position() for x in self.positions]

    def get_new_dart(self):
        """Retrieve and remove the most recently thrown dart.
        
        :return: Tuple containing position and score string, or (None, '-') if no new darts
        :rtype: tuple
        """
        if not self.new_positions:
            return None, '-'        
        dart = self.new_positions.pop()
        position = dart.get_position()
        score = dart.to_string()
        return position, score
    
    def change(self):
        """Check if a player change has occurred and reset the change flag.
        
        :return: True if a player change occurred, False otherwise
        :rtype: bool
        """
        result =  self.current_leg.change
        self.current_leg.change = False
        return result
    
    def has_just_won(self):
        """
        checks if the player just won
        :return True/False from func just_won
        :return player index that just won
        """
        result = self.just_won
        self.just_won = False
        return result, self.winner_index  # Return stored winner index
    
    def is_clear(self):
        """Check if the board needs to be cleared and reset the clear flag.
        
        :return: True if board should be cleared, False otherwise
        :rtype: bool
        """
        result = self.clear
        self.clear = False
        return result
    
    def clear_board(self):
        """Set the flag to clear the dartboard display."""
        self.clear = True
    
    def is_updated(self):
        """Check if the game state has been updated and reset the update flag.
        
        :return: True if game state was updated, False otherwise
        :rtype: bool
        """
        result = self.update
        self.update = False
        return result
    
    def reset(self):
        """Reset all players' scores to their initial values."""
        for player in self.players:
            player.reset()

    def undo_last_dart(self):
        """Remove the last thrown dart and update scores accordingly.
        
        :return: True if a dart was successfully removed, False otherwise
        :rtype: bool
        """
        if self.playing: # First condition: game must be active
            result = self.current_leg.undo_last_dart() # Delegates to Leg class
            if result:
                # Remove the last position if it exists
                if self.positions:
                    self.positions.pop()
                self.update = True
                return True
        return False
    
    def initialize_basis_dart_score_raw_image_frames(self, raw_dart_frame_camera_A, raw_dart_frame_camera_B, raw_dart_frame_camera_C):
        self.dart_score_basis_image_frames["camera_A"] = raw_dart_frame_camera_A
        self.dart_score_basis_image_frames["camera_B"] = raw_dart_frame_camera_B
        self.dart_score_basis_image_frames["camera_C"] = raw_dart_frame_camera_C


    def get_basis_dart_score_raw_image_frames(self):
        return self.dart_score_basis_image_frames