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

        if result == 1 or result < 0:
            return True
        if result == 0 and not dart.is_double:
            return True
        
        return False
    
    def has_won(self):
        return self.score == 0

    def reset(self):
        self.score = self.format