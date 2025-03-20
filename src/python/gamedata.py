# copied from gitProject, not all of this should be needed

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
            self.player.undo_dart(i)
        self.darts.append(Bust(dart))

    def display(self):
        representation = ['-', '-', '-']

        for i in range(min(3, len(self.darts))):
            representation[i] = self.darts[i].to_string()
        
        return representation
    
    def is_over(self):
        if len(self.darts) == 0:
            return False
        
        return len(self.darts) >= 3 or self.darts[-1].is_bust()

class Leg:
    def __init__(self, players, current_player):
        self.current_turn = Turn(players[current_player])
        self.turns = [self.current_turn]
        self.winner = None
        self.players = players
        self.current_player = self.players[current_player]
        self.player_index = current_player
        self.change = False
    
    def dart(self, dart):
        if not self.current_player.is_bust(dart):
            self.current_turn.dart(dart)
            self.current_player.dart(dart)
        else:
            self.current_turn.bust(dart)

        if self.current_turn.is_over():
            self.changeover()

    def get_last_turn(self, player):
        for turn in reversed(self.turns):
            if turn.player == player:
                return turn.display()
        
        return ['-', '-', '-']

    def changeover(self):
        self.player_index = (self.player_index + 1) % 2
        self.current_player = self.players[(self.player_index)]
        self.current_turn = Turn(self.current_player)
        self.turns.append(self.current_turn)
        self.change = True