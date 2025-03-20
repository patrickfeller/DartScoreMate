import CameraMode

class GameController:
    def __init__(self):
        self.mode = CameraMode.OFF
        self.frames = [None, None, None]
        self.aimbot = None
        self.center_line = False
        self.skills = []