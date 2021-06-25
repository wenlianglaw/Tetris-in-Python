# Base class for all the AI agents
#
# Initialize it with an env, which should provide
#  - get_state function: Gets a game state
#  - take_actions function: Lets the game take a list of actions.
#  - restart:  Restarts a game.

import time
import queue

import numpy as np

import actions
import game_client
import random
import shape


from typing import Callable, List, Tuple

class Env:
  def __init__(self, get_state: Callable[[], game_client.GameState],
               take_actions: Callable[[List[actions.Action]],None],
               restart: Callable[[], None]):
    self.get_state = get_state
    self.take_actions = take_actions
    self.restart = restart

def _AtBottom(piece: shape.Shape, game:game_client.GameClient):
  return not game.CheckValidity(piece, offset=(1, 0))

def _InRange(x:int, y:int, len: int, wid:int):
  return (x >= 0 and y >= 0 and x < len and y < wid)

def _PossibleContact(piece:shape.Shape, map:np.array):
  (l, w) = piece.shape.shape
  (x, y) = (piece.x, piece.y)
  for i in range(l):
    for j in range(w):
      if (not _InRange(x + i, y+j, map.shape[0], map.shape[1])
          or map[i+x][y+j] != 0):
        return True
  return False

def GetAllPossiblePositions(piece:shape.Shape,
                            state:game_client.GameState) -> (
    List[Tuple[shape.Shape, List[actions.Action]]]):
  """Gets all possible positions of a piece in the game
  :return: [(final piece status, [List of actions to reach the final status])]
  """

  ret = []

  game = game_client.CreateGameFromState(state)
  game.SpawnPiece(piece)

  if game.can_swap:
    game.Swap()
    action = actions.Action(swap=True)
    ret.append((game.current_piece, [action]))
    game.Swap()

  visit = np.zeros((game.length, game.width, 4), dtype=bool)

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

    if _PossibleContact(cur, game.map):
      for rotate in [1,2,3]:
        game.SpawnPiece(cur.copy())
        if game.Rotate(rotate):
          if not visit[game.current_piece.x, game.current_piece.y,
                       game.current_piece.state]:
            q.put((game.current_piece.copy(), path + [actions.Action(rotation=rotate)]))

  return ret

class Agent:
  def __init__(self, env: Env):
    self.env = env
    # Time interval between making two decisions
    self.decision_interval = 100 / 1000

  def MakeDecision(self) -> List[actions.Action]:
    state = self.env.get_state()
    possible_actions = self.GetAllPossiblePositions(state.current_piece, state)
    return random.choice(possible_actions)[1]


  def GetAllPossiblePositions(self, piece:shape.Shape,
                              state:game_client.GameState) -> (
      List[Tuple[shape.Shape, List[actions.Action]]]):
    return GetAllPossiblePositions(piece, state)

  def RunUntilGameEnd(self):
    state = self.env.get_state()
    while not state.is_gameover:
      start = time.time()
      action = self.MakeDecision()
      self.env.take_actions(action)
      print(f"{(time.time() - start) * 1000} ms")
      time.sleep(self.decision_interval)
    print("Game Over")


