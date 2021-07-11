# This file defines the 7 tetrominoes
# I O J L S Z T
#
# Shapes: https://tetris.fandom.com/wiki/SRS


import copy
import abc

import numpy as np

# These offsets are stored as global variables to avoid mem copy.
_SHAPES_I = np.array([
  [(1,0), (1,1), (1,2), (1,3)],
  [(0,2), (1,2), (2,2), (3,2)],
  [(2,0), (2,1), (2,2), (2,3)],
  [(0,1), (1,1), (2,1), (3,1)],
  ], dtype=np.int)

_SHAPES_J = np.array([
  [(0,0), (1,0), (1,1), (1,2)],
  [(0,1), (1,1), (2,1), (0,2)],
  [(1,0), (1,1), (1,2), (2,2)],
  [(2,0), (0,1), (1,1), (2,1)],
  ], dtype=np.int)

_SHAPES_L = np.array([
  [(1,0), (1,1), (0,2), (1,2)],
  [(0,1), (1,1), (2,1), (2,2)],
  [(1,0), (1,1), (1,2), (2,0)],
  [(0,0), (0,1), (1,1), (2,1)],
  ], dtype=np.int)

_SHAPES_O = np.array([
  [(0,1), (1,1), (0,2), (1,2)],
  [(0,1), (1,1), (0,2), (1,2)],
  [(0,1), (1,1), (0,2), (1,2)],
  [(0,1), (1,1), (0,2), (1,2)],
  ], dtype=np.int)

_SHAPES_S = np.array([
  [(1,0), (0,1), (1,1), (0,2)],
  [(0,1), (1,1), (1,2), (2,2)],
  [(1,1), (1,2), (2,0), (2,1)],
  [(0,0), (1,0), (1,1), (2,1)],
  ], dtype=np.int)

_SHAPES_T = np.array([
  [(0,1), (1,0), (1,1), (1,2)],
  [(0,1), (1,1), (2,1), (1,2)],
  [(1,0), (1,1), (1,2), (2,1)],
  [(1,0), (0,1), (1,1), (2,1)],
  ], dtype=np.int)

_SHAPES_Z = np.array([
  [(0,0), (0,1), (1,1), (1,2)],
  [(1,1), (2,1), (1,2), (0,2)],
  [(1,0), (1,1), (2,1), (2,2)],
  [(1,0), (0,1), (1,1), (2,0)],
  ], dtype=np.int)

class Shape:
  def __init__(self, start_x: int = 1, start_y: int = 3):
    self.shape = None
    self.start_x = start_x
    self.start_y = start_y
    self.x = start_x
    self.y = start_y
    # 0: spawn state
    # 1: state from rotation90 from spawn state
    # 2: rotation180 from spawn state
    # 3: rotation270 from spawn state
    self.state = 0
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
    for i in range(times%4):
      self.Rotate90()

  @abc.abstractmethod
  def Init(self):
    self.x = self.start_x
    self.y = self.start_y
    self.state = 0

  def GetShape(self):
    return self.shape[self.state]

  def __eq__(self, other):
    if other is None:
      return False

    return (self.x == other.x and
            self.y == other.y and
            self.state == other.state)

  def __str__(self):
    ret = "\n".join([
      f"({self.x}, {self.y})",
      f"state:{self.state}", ""
    ])
    display_area = np.zeros((4,4), dtype=np.int)
    for (i,j) in self.GetShape():
      display_area[i,j] = 1
    ret += display_area.__str__()
    return ret

  def __hash__(self):
    return hash(self.state) ^ hash(self.x) ^ hash(self.y)

  def copy(self):
    return copy.copy(self)

class I(Shape):
  def __init__(self, start_x: int = 1, start_y: int = 3):
    Shape.__init__(self, start_x=start_x, start_y=start_y)
    self.id = 1
    self.Init()

  def Init(self):
    super().Init()
    self.shape = _SHAPES_I

class J(Shape):
  def __init__(self, start_x: int = 1, start_y: int = 3):
    Shape.__init__(self, start_x=start_x, start_y=start_y)
    self.Init()
    self.id = 2

  def Init(self):
    super().Init()
    self.shape = _SHAPES_J

class L(Shape):
  def __init__(self, start_x: int = 1, start_y: int = 3):
    Shape.__init__(self, start_x=start_x, start_y=start_y)
    self.Init()
    self.id = 3

  def Init(self):
    super().Init()
    self.shape = _SHAPES_L

class O(Shape):
  def __init__(self, start_x: int = 1, start_y: int = 3):
    Shape.__init__(self, start_x=start_x, start_y=start_y)
    self.Init()
    self.id = 4

  def Init(self):
    super().Init()
    self.shape = _SHAPES_O

class S(Shape):
  def __init__(self, start_x: int = 1, start_y: int = 3):
    Shape.__init__(self, start_x=start_x, start_y=start_y)
    self.Init()
    self.id = 5

  def Init(self):
    super().Init()
    self.shape = _SHAPES_S

class T(Shape):
  def __init__(self, start_x: int = 1, start_y: int = 3):
    Shape.__init__(self, start_x=start_x, start_y=start_y)
    self.Init()
    self.id = 6

  def Init(self):
    super().Init()
    self.shape = _SHAPES_T

class Z(Shape):
  def __init__(self, start_x: int = 1, start_y: int = 3):
    Shape.__init__(self, start_x=start_x, start_y=start_y)
    self.Init()
    self.id = 7

  def Init(self):
    super().Init()
    self.shape = _SHAPES_Z

