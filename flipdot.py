import socket
from typing import List, Dict

import numpy as np


class Cursor:
    def __init__(self, x: int, y: int, x_max: int, y_max: int, allow_overflow: bool):
        self.__x = x
        self.__max_x = x_max
        self.__y = y
        self.__max_y = y_max
        self.allow_overflow = allow_overflow

    def to_tuple(self):
        return self.x, self.y

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value: int):
        if value < 0:
            if self.allow_overflow:
                self.__x = self.__max_x - 1 - (value % self.__max_x)
                return
            self.__x = value
            return

        if self.allow_overflow:
            self.__x = (value % self.__max_x)
            return
        self.__x = value

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value: int):
        if value < 0:
            if self.allow_overflow:
                self.__y = self.__max_y - 1 - (value % self.__max_y)
                return
            self.__y = value
            return

        if self.allow_overflow:
            self.__y = (value % self.__max_y)
            return
        self.__y = value

    def __add__(self, other: List[int]):
        new = Cursor(self.x, self.y, self.__max_x, self.__max_y, self.allow_overflow)
        new.x += other[0]
        new.y += other[1]
        return new

    def __sub__(self, other: List[int]):
        new = Cursor(self.x, self.y, self.__max_x, self.__max_y, self.allow_overflow)
        new.x -= other[0]
        new.y -= other[1]
        return new


class FlipDotMatrix:
    def __init__(self, ip: str, udp_port: int):
        self.ip = ip
        self.udp_port = udp_port
        self.width = 28
        self.height = 14
        self.cursor = Cursor(0, 0, self.width, self.height, allow_overflow=True)
        self.matrix: np.ndarray = np.zeros(shape=(self.height, self.width), dtype=bool)
        self.module_shape = (7, 28)

    def update_matrix(self):

        module_rows = self.module_shape[0]
        bytestring = bytes("", "utf-8")
        for module in range(self.height // module_rows):
            for column in range(self.module_shape[1]):
                c_segment: np.ndarray = self.matrix[module * module_rows:(module + 1) * module_rows, column]
                bytestring += np.packbits(c_segment, bitorder='little')[0]
        opened_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        opened_socket.sendto(bytestring, (self.ip, self.udp_port))
        opened_socket.close()

    def set_value(self, column: int, row: int, value: bool, update: bool = False):
        self.matrix[row, column] = value
        if update:
            self.update_matrix()

    def set_all(self, value: bool, update: False):
        if value:
            self.matrix = np.ones(shape=self.matrix.shape, dtype=bool)
        else:
            self.matrix = np.zeros(shape=self.matrix.shape, dtype=bool)
        if update:
            self.update_matrix()

    def get_value(self, column: int, row: int) -> bool:
        return self.matrix[row, column]

    def matrix_write(self, other_matrix):
        x, y = self.cursor.to_tuple()
        try:
            self.matrix[y:y + other_matrix.shape[0], x:x + other_matrix.shape[1]] = other_matrix
        except (IndexError, ValueError):
            for i_y in range(other_matrix.shape[0]):
                for i_x in range(other_matrix.shape[1]):
                    if 0 <= i_y + y < self.height and 0 <= i_x + x < self.width:
                        self.matrix[i_y + y, i_x + x] = other_matrix[i_y, i_x]

    def write(self, string: str, font: Dict[str, np.ndarray]):
        for char in string:
            c = font[char]
            self.matrix_write(c)
            self.cursor += [(c.shape[1] + 1), 0]
        self.set_cursor(0, 0)
        self.update_matrix()

    def set_cursor(self, x, y):
        self.cursor.x = x
        self.cursor.y = y
