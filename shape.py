# This file defines the 7 tetrominoes
# I O J L S Z T
#
# Shapes: https://tetris.fandom.com/wiki/SRS


import copy
import abc

import numpy as np

_SHAPES_I = np.array([
  [(1, 0), (1, 1), (1, 2), (1, 3)],
  [(0, 2), (1, 2), (2, 2), (3, 2)],
  [(2, 0), (2, 1), (2, 2), (2, 3)],
  [(0, 1), (1, 1), (2, 1), (3, 1)],
], dtype=np.uint8)

_SHAPES_J = np.array([
  [(0, 0), (1, 0), (1, 1), (1, 2)],
  [(0, 1), (1, 1), (2, 1), (0, 2)],
  [(1, 0), (1, 1), (1, 2), (2, 2)],
  [(2, 0), (0, 1), (1, 1), (2, 1)],
], dtype=np.uint8)

_SHAPES_L = np.array([
  [(1, 0), (1, 1), (0, 2), (1, 2)],
  [(0, 1), (1, 1), (2, 1), (2, 2)],
  [(1, 0), (1, 1), (1, 2), (2, 0)],
  [(0, 0), (0, 1), (1, 1), (2, 1)],
], dtype=np.uint8)

_SHAPES_O = np.array([
  [(0, 1), (1, 1), (0, 2), (1, 2)],
  [(0, 1), (1, 1), (0, 2), (1, 2)],
  [(0, 1), (1, 1), (0, 2), (1, 2)],
  [(0, 1), (1, 1), (0, 2), (1, 2)],
], dtype=np.uint8)

_SHAPES_S = np.array([
  [(1, 0), (0, 1), (1, 1), (0, 2)],
  [(0, 1), (1, 1), (1, 2), (2, 2)],
  [(1, 1), (1, 2), (2, 0), (2, 1)],
  [(0, 0), (1, 0), (1, 1), (2, 1)],
], dtype=np.uint8)

_SHAPES_T = np.array([
  [(0, 1), (1, 0), (1, 1), (1, 2)],
  [(0, 1), (1, 1), (2, 1), (1, 2)],
  [(1, 0), (1, 1), (1, 2), (2, 1)],
  [(1, 0), (0, 1), (1, 1), (2, 1)],
], dtype=np.uint8)

_SHAPES_Z = np.array([
  [(0, 0), (0, 1), (1, 1), (1, 2)],
  [(1, 1), (2, 1), (1, 2), (0, 2)],
  [(1, 0), (1, 1), (2, 1), (2, 2)],
  [(1, 0), (0, 1), (1, 1), (2, 0)],
], dtype=np.uint8)

# These offsets are stored as global variables to avoid mem copy.
_BIT_SHAPES_I = np.array([[0, 15, 0, 0],
                          [2, 2, 2, 2],
                          [0, 0, 15, 0],
                          [4, 4, 4, 4]], dtype=np.uint8)

_BIT_SHAPES_J = np.array([[8, 14, 0, 0],
                          [6, 4, 4, 0],
                          [0, 14, 2, 0],
                          [4, 4, 12, 0]], dtype=np.uint8)

_BIT_SHAPES_L = np.array([[2, 14, 0, 0],
                          [4, 4, 6, 0],
                          [0, 14, 8, 0],
                          [12, 4, 4, 0]], dtype=np.uint8)

_BIT_SHAPES_O = np.array([[6, 6, 0, 0],
                          [6, 6, 0, 0],
                          [6, 6, 0, 0],
                          [6, 6, 0, 0]], dtype=np.uint8)

_BIT_SHAPES_S = np.array([[6, 12, 0, 0],
                          [4, 6, 2, 0],
                          [0, 6, 12, 0],
                          [8, 12, 4, 0]], dtype=np.uint8)

_BIT_SHAPES_T = np.array([[4, 14, 0, 0],
                          [4, 6, 4, 0],
                          [0, 14, 4, 0],
                          [4, 12, 4, 0]], dtype=np.uint8)

_BIT_SHAPES_Z = np.array([[12, 6, 0, 0],
                          [2, 6, 4, 0],
                          [0, 12, 6, 0],
                          [4, 12, 8, 0]], dtype=np.uint8)

class Shape:
  def __init__(self, start_x: int = 2, start_y: int = 3):
    self.shape = None
    self.bit_map = None
    self._start_x = start_x
    self._start_y = start_y
    self.x = start_x
    self.y = start_y
    # 0: spawn state
    # 1: state from rotation90 from spawn state
    # 2: rotation180 from spawn state
    # 3: rotation270 from spawn state
    self.state = 0
    # 1: I
    # 2: J
    # 3: L
    # 4: O
    # 5: S
    # 6: T
    # 7: Z
    self.id = 0

  @abc.abstractmethod
  def Rotate90(self):
    self.state = (self.state + 1) % 4

  @abc.abstractmethod
  def Rotate180(self):
    self.state = (self.state + 2) % 4

  @abc.abstractmethod
  def Rotate270(self):
    self.state = (self.state + 3) % 4

  def Rotate(self, times: int):
    for i in range(times % 4):
      self.Rotate90()

  @abc.abstractmethod
  def Init(self):
    self.x = self._start_x
    self.y = self._start_y
    self.state = 0
    self.shape = [None,
                  _SHAPES_I, _SHAPES_J, _SHAPES_L,
                  _SHAPES_O, _SHAPES_S, _SHAPES_T,
                  _SHAPES_Z][self.id]

    self.bit_map = [None,
                    _BIT_SHAPES_I,
                    _BIT_SHAPES_J,
                    _BIT_SHAPES_L,
                    _BIT_SHAPES_O,
                    _BIT_SHAPES_S,
                    _BIT_SHAPES_T,
                    _BIT_SHAPES_Z][self.id]

  def GetShape(self):
    return self.shape[self.state]

  def GetBitMap(self):
    return self.bit_map[self.state]

  def __eq__(self, other):
    if other is None:
      return False

    # O shape
    if self.id == 4:
      return (self.x == other.x and self.y == other.y)
    else:
      return (self.x == other.x and
              self.y == other.y and
              self.state == other.state)

  def __str__(self):
    ret = "\n".join([
      f"({self.x}, {self.y})",
      f"state:{self.state}", ""
    ])
    display_area = np.zeros((4, 4), dtype=np.uint8)
    for (i, j) in self.GetShape():
      display_area[i, j] = 1
    ret += display_area.__str__()
    return ret

  def __hash__(self):
    # O shape: ignore the rotation
    if self.id == 4:
      return hash(self.x) ^ hash(self.y)
    else:
      return hash(self.state) ^ hash(self.x) ^ hash(self.y)

  def copy(self):
    return copy.copy(self)

class I(Shape):
  def __init__(self, start_x: int = 2, start_y: int = 3):
    Shape.__init__(self, start_x=start_x, start_y=start_y)
    self.id = 1
    self.Init()

class J(Shape):
  def __init__(self, start_x: int = 2, start_y: int = 3):
    Shape.__init__(self, start_x=start_x, start_y=start_y)
    self.id = 2
    self.Init()

class L(Shape):
  def __init__(self, start_x: int = 2, start_y: int = 3):
    Shape.__init__(self, start_x=start_x, start_y=start_y)
    self.id = 3
    self.Init()

class O(Shape):
  def __init__(self, start_x: int = 2, start_y: int = 3):
    Shape.__init__(self, start_x=start_x, start_y=start_y)
    self.id = 4
    self.Init()

class S(Shape):
  def __init__(self, start_x: int = 2, start_y: int = 3):
    Shape.__init__(self, start_x=start_x, start_y=start_y)
    self.id = 5
    self.Init()

class T(Shape):
  def __init__(self, start_x: int = 2, start_y: int = 3):
    Shape.__init__(self, start_x=start_x, start_y=start_y)
    self.id = 6
    self.Init()

class Z(Shape):
  def __init__(self, start_x: int = 2, start_y: int = 3):
    Shape.__init__(self, start_x=start_x, start_y=start_y)
    self.id = 7
    self.Init()

def GetShapeFromId(id: int) -> Shape:
  return [None, I(), J(), L(), O(), S(), T(), Z()][id]
