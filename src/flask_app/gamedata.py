# copied from gitProject, not all of this should be needed

from enum import Enum


class CameraMode(Enum):
    OFF = 'OFF'
    ON = 'ON'
    POSITIONING = 'POSITIONING'
    GAME = 'GAME'


class Admin:
    def __init__(self):
        self.mode = CameraMode.OFF
        self.frames = [None, None, None]
        self.aimbot = None
        self.center_line = False
        self.skills = []


class Dart:
    STRING_REP = ('', 'S', 'D', 'T')

    def __init__(self, score, multiplier, position):
        self.score = int(score)
        self.multiplier = int(multiplier)
        self.position = position

    def value(self):
        return self.score * self.multiplier
    
    def is_double(self):
        return self.multiplier == 2

    def to_string(self):
        return self.STRING_REP[self.multiplier] + str(self.score)
    
    def is_bust(self):
        return False
    
    def get_position(self):
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
    def __init__(self, player):
        self.darts = []
        self.player = player
    
    def dart(self, dart):
        self.darts.append(dart)

    def bust(self, dart):
        for i in self.darts:
            self.player.undo_dart(i)    # undo score of current player
        self.darts.append(Bust(dart))

    def display(self):
        """
        Initialize with three empty throws and fill in actual throws.
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
    

class Leg:
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
        if not self.current_player.is_bust(dart):
            self.current_turn.dart(dart)    # update throws current turn
            self.current_player.dart(dart)  # update score current player
        else:
            self.current_turn.bust(dart)

        if self.current_turn.is_over():
            self.last_completed_throws = self.current_turn.display()
            self.changeover()

    def get_last_turn(self, player):
        for turn in reversed(self.turns):
            if turn.player == player:
                return turn.display()
        
        return ['-', '-', '-']

    def changeover(self):
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
    def __init__(self, name, format):
        self.name = name
        self.format = format
        self.score = format
        self.wins = 0

    def dart(self, dart):
        self.score -= dart.value()

    def undo_dart(self, dart):
        self.score += dart.value()
        
    def is_bust(self, dart):
        result = self.score - dart.value()
        if result < 0: # add if doubl-out is involved: == 1 or result
            return True
        # uncomment if double-out is involved:
        # if result == 0 and not dart.is_double:
        #     return True
        return False
    
    def has_won(self):
        return self.score == 0

    def reset(self):
        self.score = self.format


class Game:
    """
    Game class stores information about the current game being played between two players
    The Front-end and Back-end use a shared Game class object to interface
    """
    def __init__(self):
        self.positions = []
        self.new_positions = []
        self.playing = False
        self.update = False
        self.current_leg = None
        self.is_bust = False
        self.winner_index = None 

    def start_game(self, first_to, format, name_a, name_b):
        """
        Starts a new game between two players and creats class objects Players and Legs.
        :param first_to: The number of legs a player must win to win the game
        :param format: The score format for the game (e.g., 501, 301)
        :param name_a: The name of player A
        :param name_b: The name of player B
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
        self.is_bust = self.current_leg.current_player.is_bust(dart)
        self.current_leg.dart(dart) # Leg([players], current_player 0/1).Dart
        self.has_won()
        self.update = True

    def has_won(self):
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
        """Return current turn's throws"""
        if self.playing and self.current_leg:
            return self.current_leg.current_turn.display()  # Always return current turn's throws
        return ['-', '-', '-']
    
    def get_wins(self):
        if self.playing == True:
            return [self.players[0].wins, self.players[1].wins]
        else:
            return -1
    
    def get_totals(self):
        if self.playing:
            return [self.players[0].score, self.players[1].score]
        else:
            return -1
    
    def new_dart(self, dart):
        self.positions.append(dart)
        self.new_positions.append(dart)

    def get_positions(self):
        return [x.get_position() for x in self.positions]

    def get_new_dart(self):
        if not self.new_positions:
            return None, '-'        
        dart = self.new_positions.pop()
        position = dart.get_position()
        score = dart.to_string()
        return position, score
    
    def change(self):
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
        result = self.clear
        self.clear = False
        return result
    
    def clear_board(self):
        self.clear = True
    
    def is_updated(self):
        result = self.update
        self.update = False
        return result
    
    def reset(self):
        for player in self.players:
            player.reset()

    def undo_last_dart(self):
        if self.playing: # First condition: game must be active
            result = self.current_leg.undo_last_dart() # Delegates to Leg class
            if result:
                # Remove the last position if it exists
                if self.positions:
                    self.positions.pop()
                self.update = True
                return True
        return False