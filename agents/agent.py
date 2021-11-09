# Base class for all the AI agents
#
# Initialize it with an env, which should provide
#  - game: Game itself.

import time
import queue
import abc

import numpy as np

import actions
import game_client
import shape
from functools import partial

from typing import Callable, List, Tuple

class Env:
  def __init__(self, game: game_client.GameClient):
    self.game = game

class Agent:
  def __init__(self, env: Env, decision_interval: float = 0.1):
    self.env = env
    # Time interval between making two decisions
    self.decision_interval = decision_interval

  @abc.abstractmethod
  def MakeDecision(self) -> List[actions.Action]:
    """Returns a list of actions based on the current game state."""
    raise NotImplementedError()

  def RunGame(self):
    while True:
      start = time.time()
      actions = self.MakeDecision()
      self.env.game.ProcessActions(actions)
      print(f"{(time.time() - start) * 1000} ms")
      time.sleep(self.decision_interval)

def _AtBottom(piece: shape.Shape, game: game_client.GameClient):
  return not game.CheckValidity(piece, offset=(1, 0))

def _GetHardDroppedPiece(game, piece) -> shape.Shape:
  hard_drop_piece = piece.copy()
  while game.CheckValidity(hard_drop_piece, (1, 0)):
    hard_drop_piece.x += 1
  return hard_drop_piece

def GetPossiblePositionsQuickVersion(piece: shape.Shape, game_: game_client.GameClient) -> (
    List[Tuple[shape.Shape, List[actions.Action]]]):
  """ Gets some possible positions.  This is a quicker and simpler version of GetALlPossiblePositions.

  This is intended to run fast.
  :returns (piece inish state, [actions to this state])
  """
  ret = []

  game = game_.copy()
  game.SpawnPiece(piece)

  if game.can_swap:
    action = actions.Action(swap=True)
    ret.append((game.piece_list[0], [action]))

  # visit[x,y,state]
  visit = set()

  # Element is (piece, [Actions])

  q = queue.Queue()
  q.put((piece.copy(), []))

  shape_o_id = shape.O().id

  while not q.empty():
    (cur, path) = q.get()
    if (cur.x, cur.y, cur.state) in visit:
      continue

    visit.add((cur.x, cur.y, cur.state))

    if _AtBottom(cur, game):
      ret.append((cur.copy(), path + [actions.Action(dir=actions.HARD_DROP)]))

    # Exapands Q
    for (x, y) in [(0, 1), (0, -1)]:
      if (cur.x + x, cur.y + y, cur.state) not in visit:
        if game.CheckValidity(cur, (x, y)):
          piece_to_expand = cur.copy()
          piece_to_expand.x += x
          piece_to_expand.y += y

          action = actions.Action()
          if y == 1:
            action.direction = actions.RIGHT
          else:
            action.direction = actions.LEFT
          if (piece_to_expand.x, piece_to_expand.y,
              piece_to_expand.state) not in visit:
            q.put((piece_to_expand, path + [action]))

    # SoftDrop
    piece_to_expand = cur.copy()
    while game.CheckValidity(piece_to_expand, (1,0)):
      piece_to_expand.x += 1
    action = actions.Action(dir=actions.SOFT_DROP)
    if (piece_to_expand.x, piece_to_expand.y,
        piece_to_expand.state) not in visit:
      q.put((piece_to_expand, path + [action]))

    # Expands rotations
    if _AtBottom(cur, game) and cur.id != shape_o_id:
      for rotate in [1, 2, 3]:
        game.SpawnPiece(cur.copy())
        if game.Rotate(rotate):
          if (game.current_piece.x, game.current_piece.y,
              game.current_piece.state) not in visit:
            q.put((game.current_piece.copy(), path + [actions.Action(rotation=rotate)]))

  return ret


def GetAllPossiblePositions(piece: shape.Shape,
                            game_: game_client.GameClient) -> (
    List[Tuple[shape.Shape, List[actions.Action]]]):
  """Gets all possible positions of a piece in the game
  Note still some positions which requires soft-drop to mid screen and then rotate are
  ignored since this will save ~60% time.

  :return: [(final piece status, [List of actions to reach the final status])]
  """

  ret = []

  game = game_.copy()
  game.SpawnPiece(piece)

  if game.can_swap:
    action = actions.Action(swap=True)
    ret.append((game.piece_list[0], [action]))

  # visit[x,y,state]
  visit = set()

  # Element is (piece, [Actions])

  q = queue.Queue()
  q.put((piece.copy(), []))

  while not q.empty():
    (cur, path) = q.get()
    if (cur.x, cur.y, cur.state) in visit:
      continue

    visit.add((cur.x, cur.y, cur.state))

    if _AtBottom(cur, game):
      ret.append((cur.copy(), path + [actions.Action(dir=actions.HARD_DROP)]))

    # Exapands Q
    for (x, y) in [(1, 0), (0, 1), (0, -1)]:
      if (cur.x + x, cur.y + y, cur.state) not in visit:
        tt  = game.CheckValidity(cur, (x, y))
        if game.CheckValidity(cur, (x, y)):
          piece_to_expand = cur.copy()
          piece_to_expand.x += x
          piece_to_expand.y += y

          action = actions.Action()
          if x == 1:
            action.down = True
          elif y == 1:
            action.direction = actions.RIGHT
          else:
            action.direction = actions.LEFT
          if (piece_to_expand.x, piece_to_expand.y,
              piece_to_expand.state) not in visit:
            q.put((piece_to_expand, path + [action]))

    if _AtBottom(cur, game):
      for rotate in [1, 2, 3]:
        game.SpawnPiece(cur.copy())
        if game.Rotate(rotate):
          if (game.current_piece.x, game.current_piece.y,
                       game.current_piece.state) not in visit:
            q.put((game.current_piece.copy(), path + [actions.Action(rotation=rotate)]))

  return ret
