import datetime
import time

import numpy as np
from scipy.ndimage import rotate

from flipdot import FlipDotMatrix
from letter import letter, fat_letter

from typing import *


class DigitalClock:
    def __init__(self, matrix: FlipDotMatrix):
        self.matrix = matrix
        self.matrix.cursor.allow_overflow = False
        self.current_time_string = "      "
        self.font = letter
        self.fat_font = fat_letter
        self.delay = .2

    def update(self):
        t = datetime.datetime.now().__str__()[11:16]
        if self.current_time_string != t:
            roll_indices = [i for i, (new_c, old_c) in enumerate(zip(t, self.current_time_string)) if new_c != old_c]
            new_letters: List[Any] = []
            old_letters: List[Any] = []
            clean_up = self.font[" "]
            x = 1
            y = 0
            for i, (new_c, old_c) in enumerate(zip(t, self.current_time_string)):
                if i == 0:
                    if old_c == "0":
                        old_c_m = self.fat_font[" "]
                    else:
                        old_c_m = self.fat_font[old_c]
                    if new_c == "0":
                        new_c_m = self.fat_font[" "]
                    else:
                        new_c_m = self.fat_font[new_c]

                elif i > 1:
                    new_c_m = self.font[new_c]
                    old_c_m = self.font[old_c]
                else:
                    new_c_m = self.fat_font[new_c]
                    old_c_m = self.fat_font[old_c]
                new_letters += [[x, -self.matrix.height - self.matrix.height // 3, new_c_m]]
                old_letters += [[x, y, old_c_m]]
                x += new_c_m.shape[1] + 1
            for i, (old, new) in enumerate(zip(old_letters, new_letters)):
                x, old_y, old_m = old
                _, new_y, new_m = new
                if i not in roll_indices:
                    self.matrix.set_cursor(x, old_y)
                    self.matrix.matrix_write(old_m)
                    continue
                for offset in range(self.matrix.height + self.matrix.height // 3):
                    self.matrix.set_cursor(x, old_y + offset)
                    self.matrix.matrix_write(old_m)
                    self.matrix.set_cursor(x, old_y + offset - old_m.shape[0])
                    self.matrix.matrix_write(clean_up)
                    self.matrix.set_cursor(x, new_y + offset)
                    self.matrix.matrix_write(new_m)
                    self.matrix.update_matrix()
                    time.sleep(self.delay)
                self.matrix.set_cursor(x, old_y)
                self.matrix.matrix_write(new_m)
                self.matrix.update_matrix()
            self.current_time_string = t


class AnalogClock:
    def __init__(self, matrix: FlipDotMatrix):
        self.matrix = matrix
        self.__minute = 0
        self.__hour = 0
        self.threshold = .35

        self.border = np.array([
            [0., 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0],
        ], dtype=bool)

        self.minute = np.array([
            [0., 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ])

        self.hour = np.array([
            [0., 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ])

    def update(self):
        t = datetime.datetime.now()
        if t.hour % 5 != 0:
            return
        self.__minute = t.minute
        self.__hour = t.hour
        m_h = rotate(self.hour, -(self.__hour % 12 * 30), reshape=False)
        m_m = rotate(self.minute, -(self.__minute // 5 * 30), reshape=False)
        self.matrix.set_cursor(1, 1)
        self.matrix.matrix_write((self.border + m_h > self.threshold) + m_m > self.threshold)
        self.matrix.update_matrix()
