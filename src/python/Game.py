# Game class stores information about the current game being played between two players
# The Front-end and Back-end use a shared Game class object to interface

import Player
from gamedata import Leg

class Game:
    def __init__(self):
        self.positions = []
        self.new_positions = []
        self.playing = False
        self.update = False

    def start_game(self, first_to, format, name_a, name_b):
        self.first_to = first_to
        self.legs_played = []
        self.format = format
        self.players = (Player(name_a, format), Player(name_b, format))
        self.current_leg = Leg(self.players, len(self.legs_played) % 2)
        self.playing = True
        self.update = True
        self.clear = False
        self.just_won = False

    def dart(self, dart):
        self.current_leg.dart(dart)
        self.has_won()
        self.update = True

    def has_won(self):
        for player in self.players:
            if player.has_won():
                self.current_leg.winner = player
                player.wins += 1
                self.reset()
                self.legs_played.append(self.current_leg)
                self.current_leg = Leg(self.players, len(self.legs_played) % 2)
                self.just_won = True
    
    def get_scores(self):
        if self.playing == True:
            return [self.current_leg.get_last_turn(self.players[0]), self.current_leg.get_last_turn(self.players[1])]
        else:
            return -1
        
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
        result = self.just_won
        self.just_won = False
        return result, self.current_leg.player_index
    
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