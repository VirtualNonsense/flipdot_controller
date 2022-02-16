import datetime
import time

from flipdot import FlipDotMatrix
from letter import letter


class Clock:
    def __init__(self, matrix: FlipDotMatrix):
        self.matrix = matrix
        self.matrix.cursor.allow_overflow = False
        self.current_time_string = None
        self.font = letter
        self.delay = .2

    def update(self):
        t = datetime.datetime.now().__str__()[11:16]
        if self.current_time_string is None:
            self.current_time_string = t
            self.matrix.write(t, self.font)
            return

        if self.current_time_string != t:
            roll_indices = [i for i, (new_c, old_c) in enumerate(zip(t, self.current_time_string)) if new_c != old_c]
            new_letters = []
            old_letters = []
            x = 0
            y = 0
            for i, (new_c, old_c) in enumerate(zip(t, self.current_time_string)):
                new_c_m = self.font[new_c]
                old_c_m = self.font[old_c]
                new_letters += [[x, -self.matrix.height - 1, new_c_m]]
                old_letters += [[x, y, old_c_m]]
                x += new_c_m.shape[1] + 1

            offset = 0
            for i, (old, new) in enumerate(zip(old_letters, new_letters)):
                x, old_y, old_m = old
                _, new_y, new_m = new
                if i not in roll_indices:
                    self.matrix.set_cursor(x, old_y)
                    self.matrix.matrix_write(old_m)
                    continue
                for offset in range(self.matrix.height):
                    self.matrix.set_cursor(x, new_y + offset)
                    self.matrix.matrix_write(new_m)
                    self.matrix.set_cursor(x, old_y + offset)
                    self.matrix.matrix_write(old_m)
                    self.matrix.update_matrix()
                    time.sleep(self.delay)
                self.matrix.set_cursor(x, old_y)
                self.matrix.matrix_write(new_m)
                self.matrix.update_matrix()
            self.current_time_string = t
