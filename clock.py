import datetime

from flipdot import FlipDotMatrix


class Clock:
    def __init__(self, matrix: FlipDotMatrix):
        self.matrix = matrix
        self.current_time_string = ""

    def update(self):
        t = datetime.datetime.now().__str__()[11:16]
        if self.current_time_string != t:
            self.current_time_string = t
            self.matrix.write(t)