# MCTS to search for a best move.

import time

import numpy as np

import agent
import actions
import mcts_algorithm
import game_client
import shape
import threading

import random

import scipy.ndimage


from typing import List, Set, Dict, Tuple

class MCTSNode(mcts_algorithm.Node):
  def __init__(self, game:game_client.GameClient=None,
               init_line_dropped:int=0,
               saved_solutions:
               Dict[mcts_algorithm.Node,
                    Tuple[shape.Shape, List[actions.Action]]] = None,
               root_score : float = 0.0):
    super().__init__()

    self.saved_solutions = saved_solutions
    if self.saved_solutions is None:
      self.saved_solutions = dict()

    self.action_list = []
    self.game = game
    # game used for simulation
    self.init_line_dropped = init_line_dropped
    self.root_score = root_score

  def FindChildren(self)->Set[mcts_algorithm.Node]:
    if self.game is None:
      return set()

    all_possible_solutions = (None, [])
    if self in self.saved_solutions.keys():
      all_possible_solutions = self.saved_solutions[self]

    else:
      all_possible_solutions = agent.GetAllPossiblePositions(
        self.game.current_piece, self.game)
      self.saved_solutions[self] = all_possible_solutions

    ret = set()

    for solution in all_possible_solutions:
      game = self.game.copy()
      game.ProcessActions(solution[1])
      node = MCTSNode(game, self.init_line_dropped, root_score=self.root_score)
      node.action_list = solution[1]
      ret.add(node)

    return ret

  def FindRandomChild(self):
    "Random successor of this board state (for more efficient simulation)"

    game = self.game.copy()
#    all_possible_actions = agent.GetAllPossiblePositions(
#      game.current_piece, game)
    all_possible_actions = agent.SimulateGetPossiblePositions(
      game.current_piece, game)
    acts = random.choice(all_possible_actions)[1]
    game.ProcessActions(acts)

    ret = MCTSNode(game, self.init_line_dropped)
    return ret

  def _Connected0Area(self, map: np.array) -> int:
    _, n = scipy.ndimage.measurements.label(map == 0)
    return n

  def _CountHoles(self, map: np.array) -> int:
    return self._Connected0Area(map) - 1

  def _CountSubHoles(self, map: np.array) -> int:
    sum = 0
    for i in range(0, self.game.length, 2):
      sum += self._CountHoles(map[i:i+1, :])
    return sum

  def _Compactness(self, map: np.array) -> int:
    """Height compactness + col compactness.  The lower the better."""
    ret = 0
    rows = np.sum(map!=0, axis=0)
    for i in range(len(rows)-1):
      if rows[i] != 0 and rows[i+1] != 0:
        ret += np.abs(rows[i] - rows[i+1])


    cols = np.sum(map!=0, axis=1)
    for i in range(len(cols)-1):
      if cols[i] != 0 and cols[i+1] != 0:
        ret += np.abs(cols[i] - cols[i+1])
    return ret


  def Reward(self, game: game_client.GameClient)->float:
    holes = self._CountHoles(game.map)
    sub_holes = self._CountSubHoles(game.map)
    compactness = self._Compactness(game.map)

    if game.is_gameover:
      return -10000
    return (game.score * 10 + game.line_dropped -4*(holes-1)
            -2*sub_holes - 1 * compactness)

  def IsTerminal(self):
    "Returns True if the node has no children"
    return self.game.CheckGameOver()

  def PlayUntilTermination(self)->float:
    game = self.game.copy()
    while not game.is_gameover and game.line_dropped - self.init_line_dropped < 2:
      all_possible_actions = agent.GetAllPossiblePositions(
        game.current_piece, game.GetState())
      acts = random.choice(all_possible_actions)[1]
      game.ProcessActions(acts)
    return self.Reward(game)

  def __hash__(self):
    "Nodes must be hashable"
    return (int.from_bytes(self.game.map.data.tobytes(), "little") ^
            hash(self.game.current_piece) ^ hash(self.game.held_piece) ^
            hash(len(self.action_list)))

  def __eq__(node1, node2):
    "Nodes must be comparable"
    if len(node1.action_list) != len(node2.action_list):
      return False
    for i in range(len(node1.action_list)):
      if node1.action_list[i] != node2.action_list[i]:
        return False

    return (np.array_equal(node1.game.map, node2.game.map) and
            node1.game.current_piece == node2.game.current_piece and
            node1.game.held_piece == node2.game.held_piece)


class MCTSAgent(agent.Agent):
  def __init__(self, env: agent.Env):
    super().__init__(env)

  def MakeDecision(self) -> List[actions.Action]:
    state = self.env.get_state()
    game = game_client.CreateGameFromState(state)
    tree = MCTSNode(game, game.line_dropped)
    mcts = mcts_algorithm.MCTS()

    print(game.line_dropped)
    print(game.score)
    game.TextDraw()

    def SingleThreadRollout():
      for _ in range(100):
        start_time = time.time()
        tree.root_score = game.score
        mcts.Rollout(tree)
        print(f"iteration: {_}, {(time.time() - start_time) * 1000}ms")

    threads = []
    thread_num = 1
    for i in range(thread_num):
      threads.append(threading.Thread(target=SingleThreadRollout))
      threads[-1].start()

    for th in threads:
      th.join()

    best_choice = mcts.Choose(tree)
    return best_choice.action_list

