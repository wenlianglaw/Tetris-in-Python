# This file defines the 7 tetrominoes
# I O J L S Z T

import copy

import numpy as np

class Shape:
  def __init__(self, start_x: int = 1, start_y: int = 3):
    self.shape = np.ascontiguousarray([[]])
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

  def Rotate90(self):
    self.shape = np.rot90(self.shape)
    self.shape = np.rot90(self.shape)
    self.shape = np.rot90(self.shape)
    self.state = (self.state + 1) % 4

  def Rotate180(self):
    self.shape = np.rot90(self.shape)
    self.shape = np.rot90(self.shape)
    self.state = (self.state + 2) % 4

  def Rotate270(self):
    self.shape = np.rot90(self.shape)
    self.state = (self.state + 3) % 4

  def Init(self):
    self.x = self.start_x
    self.y = self.start_y
    self.state = 0

  def __eq__(self, other):
    if other is None:
      return False

    return (self.x == other.x and
            self.y == other.y and
            np.array_equal(self.shape, other.shape))

  def __str__(self):
    ret = "\n".join([
      f"({self.x}, {self.y})",
      f"state:{self.state}", ""
    ])
    for i in self.shape:
      for j in i:
        ret += str(j) + " "
      ret += "\n"
    return ret

  def __hash__(self):
    return (int.from_bytes(self.shape.data.tobytes(), "little")
            ^ hash(self.x) ^ hash(self.y))

  def copy(self):
    return copy.deepcopy(self)

class I(Shape):
  def __init__(self, start_x: int = 1, start_y: int = 3):
    Shape.__init__(self, start_x=start_x, start_y=start_y)
    self.id = 1
    self.Init()

  def Init(self):
    super().Init()
    self.shape = np.ascontiguousarray([
      [0, 0, 0, 0],
      [1, 1, 1, 1],
      [0, 0, 0, 0],
      [0, 0, 0, 0]])

class J(Shape):
  def __init__(self, start_x: int = 1, start_y: int = 3):
    Shape.__init__(self, start_x=start_x, start_y=start_y)
    self.Init()
    self.id = 2

  def Init(self):
    super().Init()
    self.shape = np.ascontiguousarray([
      [1, 0, 0],
      [1, 1, 1],
      [0, 0, 0]])

class L(Shape):
  def __init__(self, start_x: int = 1, start_y: int = 3):
    Shape.__init__(self, start_x=start_x, start_y=start_y)
    self.Init()
    self.id = 3

  def Init(self):
    super().Init()
    self.shape = np.ascontiguousarray([
      [0, 0, 1],
      [1, 1, 1],
      [0, 0, 0]])

class O(Shape):
  def __init__(self, start_x: int = 1, start_y: int = 3):
    Shape.__init__(self, start_x=start_x, start_y=start_y)
    self.Init()
    self.id = 4

  def Init(self):
    super().Init()
    self.shape = np.ascontiguousarray([
      [0, 1, 1, 0],
      [0, 1, 1, 0],
      [0, 0, 0, 0]])

  def Rotate90(self):
    self.state = (self.state + 1) % 4

  def Rotate180(self):
    self.state = (self.state + 2) % 4

  def Rotate270(self):
    self.state = (self.state + 3) % 4

class S(Shape):
  def __init__(self, start_x: int = 1, start_y: int = 3):
    Shape.__init__(self, start_x=start_x, start_y=start_y)
    self.Init()
    self.id = 5

  def Init(self):
    super().Init()
    self.shape = np.ascontiguousarray([
      [0, 1, 1],
      [1, 1, 0],
      [0, 0, 0]])

class T(Shape):
  def __init__(self, start_x: int = 1, start_y: int = 3):
    Shape.__init__(self, start_x=start_x, start_y=start_y)
    self.Init()
    self.id = 6

  def Init(self):
    super().Init()
    self.shape = np.ascontiguousarray([
      [0, 1, 0],
      [1, 1, 1],
      [0, 0, 0]])

class Z(Shape):
  def __init__(self, start_x: int = 1, start_y: int = 3):
    Shape.__init__(self, start_x=start_x, start_y=start_y)
    self.Init()
    self.id = 7

  def Init(self):
    super().Init()
    self.shape = np.ascontiguousarray([
      [1, 1, 0],
      [0, 1, 1],
      [0, 0, 0]])
