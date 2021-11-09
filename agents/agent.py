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
  game = game_.copy()
  is_visited = set()
  ret = []

  is_t_shape = isinstance(piece, shape.T)

  def _AppendToRet(ele):
    if ele[0] in is_visited:
      return
    is_visited.add(ele[0])
    add = (ele[0], ele[1] + [actions.Action(dir=actions.HARD_DROP)])
    ret.append(add)

  def _ExecuteThen(then, game, init_path):
    piece = game.current_piece.copy()
    if _AtBottom(game.current_piece, game):
      _AppendToRet((game.current_piece, init_path.copy()))
    if then:
      then(game, init_path)
    game.SpawnPiece(piece)

  def _DropAndRotate(game, init_path, then=None):
    """
    :param then: Callable function, if set it will be execute after the Rotation.
    """
    path = init_path.copy()
    piece = game.current_piece.copy()
    hard_dropped = piece.copy()

    # Drop
    if not _AtBottom(piece, game):
      path.append(actions.Action(dir=actions.SOFT_DROP))
      hard_dropped = _GetHardDroppedPiece(game, piece)
    _AppendToRet((hard_dropped, path.copy()))

    # And Rotate
    for rotation in range(1, 4):
      dropped = hard_dropped.copy()
      game.SpawnPiece(dropped)
      # If rotated and cannot move down anymore, then add to rst.
      if game.Rotate(rotation) and _AtBottom(game.current_piece, game):
        cur_path = path + [actions.Action(rotation=rotation)]
        _AppendToRet((game.current_piece, cur_path.copy()))
        if then:
          then(game, cur_path, None)

    game.SpawnPiece(piece)

  def _Slide(game: game_client.GameClient,
             init_path, then=None):
    """ Slide and do func `then`.
    :param then:  Callable[[piece, game, init_path], None]
    """
    piece = game.current_piece.copy()

    _ExecuteThen(then, game, init_path)
    for y in [-1, 1]:
      cur_path = init_path.copy()
      game.SpawnPiece(piece)
      while game.CheckValidity(game.current_piece, (0, y)):
        game.current_piece.y += y
        cur_path.append(actions.Action(dir=actions.LEFT if y == -1 else actions.RIGHT))
        _ExecuteThen(then, game, cur_path)

    game.SpawnPiece(piece)

  if game.can_swap:
    _AppendToRet((piece, [actions.Action(swap=True)]))

  # Rotate -> slide -> drop -> rotate and slide
  for rotate in range(4):
    game.SpawnPiece(piece)
    # If cannot rotate, continue
    if rotate != 0 and not game.Rotate(rotate):
      continue
    _Slide(game,
           [actions.Action(rotation=rotate)] if rotate != 0 else [],
           partial(_DropAndRotate, then=_Slide))
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
  visit = np.zeros(
    game.color_map.shape + (4,), dtype=bool)

  # Element is (piece, [Actions])

  q = queue.Queue()
  q.put((piece.copy(), []))

  while not q.empty():
    (cur, path) = q.get()
    if visit[cur.x, cur.y, cur.state]:
      continue

    visit[cur.x, cur.y, cur.state] = True

    if _AtBottom(cur, game):
      ret.append((cur.copy(), path + [actions.Action(dir=actions.HARD_DROP)]))

    # Exapands Q
    for (x, y) in [(1, 0), (0, 1), (0, -1)]:
      if not visit[cur.x + x, cur.y + y, cur.state]:
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
          if not visit[piece_to_expand.x, piece_to_expand.y,
                       piece_to_expand.state]:
            q.put((piece_to_expand, path + [action]))

    if _AtBottom(cur, game):
      for rotate in [1, 2, 3]:
        game.SpawnPiece(cur.copy())
        if game.Rotate(rotate):
          if not visit[game.current_piece.x, game.current_piece.y,
                       game.current_piece.state]:
            q.put((game.current_piece.copy(), path + [actions.Action(rotation=rotate)]))

  return ret
