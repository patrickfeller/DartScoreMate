import threading
import Game
import GameController
import GUI.GameView as GUI
import time

# Create Thread Handler / Lock and the shared resources for parallel processing
threadHandler = threading.Condition()
gameController = GameController()
game = Game()


# Create 3 Threads to run the specific functions, passing the Thread Handler and the shared resources
gui_thread = threading.Thread(
    target=GUI.start_webgui, args=(threadHandler, gameController, game)
)
# here should be the thread for the dart detection
# here should be the thread for start normal, whatever it is


# set the threads as daemon, with this they are background threads and terminate if the main thread terminates
gui_thread.daemon = True
#
#


try:
    # starting the threads
    gui_thread.start()
    #
    #

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nKeyboardInterrupt detected. Program will terminates.")
