# Base class for all the AI agents
#
# Initialize it with an env, which should provide
#  - get_state function: Gets a game state
#  - take_actions function: Lets the game take a list of actions.
#  - restart:  Restarts a game.

import time
import queue
import abc

import numpy as np

import actions
import game_client
import shape

from typing import Callable, List, Tuple


class Env:
  def __init__(self, get_state: Callable[[], game_client.GameState],
               take_actions: Callable[[List[actions.Action]],None],
               restart: Callable[[], None]):
    self.get_state = get_state
    self.take_actions = take_actions
    self.restart = restart


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
      action = self.MakeDecision()
      self.env.take_actions(action)
      print(f"{(time.time() - start) * 1000} ms")
      time.sleep(self.decision_interval)


def _AtBottom(piece: shape.Shape, game:game_client.GameClient):
  return not game.CheckValidity(piece, offset=(1, 0))

def GetPossiblePositionsQuickVersion(piece: shape.Shape, game: game_client.GameClient) -> (
    List[Tuple[shape.Shape, List[actions.Action]]]):
  """ Gets some possible positions.  This is a quicker and simpler version of GetALlPossiblePositions.

  This is intended to run fast.
  :returns (piece inish state, [actions to this state])
  """

  def GetHardDroppedPiece(piece):
    hard_drop_piece = piece.copy()
    while game.CheckValidity(hard_drop_piece, (1,0)):
      hard_drop_piece.x += 1
    return hard_drop_piece

  def SearchForCurrentState(piece, game, init_path=None):
    path = []

    if init_path is not None:
      path = init_path.copy()

    ret.append((GetHardDroppedPiece(piece), path + [actions.Action(dir=actions.HARD_DROP)]))

    for y in [-1, 1]:
      path = []
      if init_path is not None:
        path = init_path.copy()
      moved_piece = piece.copy()
      while game.CheckValidity(moved_piece, (0, y)):
        moved_piece.y += y
        if y == -1:
          path.append(actions.Action(dir=actions.LEFT))
        else:
          path.append(actions.Action(dir=actions.RIGHT))
        ret.append((GetHardDroppedPiece(moved_piece),
                    path.copy() + [actions.Action(dir=actions.HARD_DROP)]))


  ret = []

  if game.can_swap:
    ret.append((piece, [actions.Action(swap=True)]))

  for rotate in range(4):
    can_break = False
    # For shape I, S and Z, we don't need to rotate it 180 and 270.
    for instance in [shape.I, shape.S, shape.Z]:
      if isinstance(piece, instance) and rotate > 1:
        can_break = True

    # For shape O, we don't need to rotate at all.
    if isinstance(piece, shape.O) and rotate > 0:
      can_break = True

    if can_break:
      break

    rotated_piece = piece.copy()

    rotated_piece.Rotate(rotate)
    if rotate == 0:
      SearchForCurrentState(rotated_piece.copy(), game)
    else:
      SearchForCurrentState(rotated_piece.copy(), game, [actions.Action(rotation=rotate)])

  return ret

def GetAllPossiblePositions(piece:shape.Shape,
                            game_:game_client.GameClient) -> (
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

  visit = np.zeros((game.height, game.width, 4), dtype=bool)

  # Element is (piece, [Actions])

  q = queue.Queue()
  q.put((piece.copy(), []))

  while not q.empty():
    (cur, path) = q.get()
    if visit[cur.x, cur.y, cur.state]:
      continue

    visit[cur.x, cur.y, cur.state] = True

    if _AtBottom(cur, game):
      ret.append((cur.copy(), path  + [actions.Action(dir=actions.HARD_DROP)]))

    # Exapands Q
    for (x, y) in [(1, 0), (0, 1), (0, -1)]:
      if not visit[cur.x + x, cur.y+y, cur.state]:
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
            q.put((piece_to_expand, path+[action]))

      if _AtBottom(cur, game):
        for rotate in [1, 2, 3]:
          game.SpawnPiece(cur.copy())
          if game.Rotate(rotate):
            if not visit[game.current_piece.x, game.current_piece.y,
                         game.current_piece.state]:
              q.put((game.current_piece.copy(), path + [actions.Action(rotation=rotate)]))

  return ret

