import random

NONE = 0
DOWN = 1
LEFT = 2
RIGHT = 3
SOFT_DROP = 4
# Hard drop is soft drop with confirmation.
HARD_DROP = 5

class Action:
  def __init__(self, dir:int=NONE, rotation:int=0, swap:bool=False,
               down:bool=False, source_user_or_ai: bool=True):
    self.direction = dir
    self.down = down
    self.rotation = rotation
    self.swap = swap
    # True if this action is from user or ai, Flase if this action is from autodrop
    self.source_user = source_user_or_ai

  def __str__(self):
    ret = f"swap:{self.swap} direction:{self.direction} " \
      f"down:{self.down} rotation:{self.rotation}, from user:{self.source_user}"
    return ret

def RandomAction() -> Action:
  ret = Action()
  ret.direction = random.randint(0, 5)
  if ret.direction == 0:
    ret.down = bool(random.randint(0, 1))
  elif not ret.down:
    ret.rotation = random.randint(1, 3)
  elif ret.rotation == 0:
    ret.swap = bool(random.randint(0, 1))
  return ret
