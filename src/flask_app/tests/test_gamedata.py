import unittest
from src.flask_app.gamedata import Dart, Bust, Player, Turn, Leg, Game

class TestDartAndBust(unittest.TestCase):

    def test_dart_value_and_string(self):
        dart = Dart(20, 3, (100, 100))
        self.assertEqual(dart.value(), 60)
        self.assertEqual(dart.to_string(), "T20")
        self.assertEqual(dart.get_position(), (100, 100))
        self.assertFalse(dart.is_bust())

    def test_bust_behavior(self):
        dart = Dart(20, 2, (50, 50))
        bust = Bust(dart)
        self.assertEqual(bust.value(), 0)
        self.assertTrue(bust.is_bust())
        self.assertEqual(bust.to_string(), "BUST")

class TestPlayer(unittest.TestCase):

    def test_player_scoring_and_undo(self):
        player = Player("Alice", 301)
        dart = Dart(20, 3, (0, 0))  # 60
        player.dart(dart)
        self.assertEqual(player.score, 241)
        player.undo_dart(dart)
        self.assertEqual(player.score, 301)

    def test_player_bust_logic(self):
        player = Player("Bob", 20)
        bust_dart = Dart(15, 2, (0, 0))  # 30 points
        self.assertTrue(player.is_bust(bust_dart))
        good_dart = Dart(10, 1, (0, 0))  # 10 points
        self.assertFalse(player.is_bust(good_dart))

    def test_player_win_condition(self):
        player = Player("Winner", 60)
        dart = Dart(20, 3, (0, 0))  # 60
        player.dart(dart)
        self.assertTrue(player.has_won())

class TestTurn(unittest.TestCase):

    def test_turn_adds_darts_and_marks_over(self):
        player = Player("TurnTester", 100)
        turn = Turn(player)
        for _ in range(3):
            turn.dart(Dart(10, 1, (0, 0)))
        self.assertTrue(turn.is_over())
        self.assertEqual(len(turn.darts), 3)
        self.assertEqual(turn.display(), ["S10", "S10", "S10"])

    def test_turn_bust_handling(self):
        player = Player("TurnBuster", 100)
        turn = Turn(player)
        dart = Dart(50, 3, (0, 0))
        turn.bust(dart)
        self.assertTrue(turn.darts[-1].is_bust())
        self.assertTrue(turn.is_over())

def test_turn_undo_logic(self):
    player = Player("UndoTester", 100)
    turn = Turn(player)
    dart1 = Dart(20, 1, (0, 0))
    dart2 = Dart(15, 2, (0, 0))

    turn.dart(dart1)
    turn.dart(dart2)

    # At this point, the Turn should contain 2 darts
    self.assertEqual(len(turn.darts), 2)
    self.assertEqual(turn.darts[0].to_string(), 'S20')
    self.assertEqual(turn.darts[1].to_string(), 'D15')

    # Now undo last dart
    last = turn.undo_last_dart()
    self.assertEqual(last.to_string(), 'D15')
    self.assertEqual(len(turn.darts), 1)

    # Score should remain unchanged because Turn doesn't alter score
    self.assertEqual(player.score, 100)  # No score change expected

class TestLeg(unittest.TestCase):

    def test_leg_switches_players_after_turn(self):
        players = [Player("P1", 301), Player("P2", 301)]
        leg = Leg(players, 0)
        for _ in range(3):
            leg.dart(Dart(10, 1, (0, 0)))
        self.assertEqual(leg.current_player.name, "P2")

    def test_leg_undo_across_turns(self):
        p1 = Player("Undo1", 301)
        p2 = Player("Undo2", 301)
        leg = Leg([p1, p2], 0)
        # Full turn for p1
        leg.dart(Dart(20, 1, (0, 0)))
        leg.dart(Dart(20, 1, (0, 0)))
        leg.dart(Dart(20, 1, (0, 0)))
        # p2's turn begins
        self.assertEqual(leg.current_player.name, "Undo2")
        # Undo 3 darts to go back to p1's last turn
        leg.undo_last_dart()
        leg.undo_last_dart()
        leg.undo_last_dart()       
        self.assertEqual(leg.current_player.name, "Undo1")
        self.assertEqual(p1.score, 301)
        self.assertEqual(len(leg.current_turn.darts), 0)


if __name__ == '__main__':
    unittest.main()