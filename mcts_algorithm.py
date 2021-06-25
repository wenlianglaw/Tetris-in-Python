
# Ref:
# [1]: https://gist.github.com/qpwo/c538c6f73727e254fdc7fab81024f6e1
# [2]: https://en.wikipedia.org/wiki/Monte_Carlo_tree_search
from abc import ABC, abstractmethod
from collections import defaultdict
import math

class Node(ABC):
  """
  A representation of a single board state.
  MCTS works by constructing a tree of these Nodes.
  Could be e.g. a chess or checkers board state.
  """

  @abstractmethod
  def FindChildren(self):
    "All possible successors of this board state"
    return set()

  @abstractmethod
  def FindRandomChild(self):
    "Random successor of this board state (for more efficient simulation)"
    return None


  def PlayUntilTermination(self)->float:
    """Plays the game until termination.
    :returns rewards on termination."""
    return 0

  @abstractmethod
  def IsTerminal(self):
    "Returns True if the node has no children"
    return True

  @abstractmethod
  def __hash__(self):
    "Nodes must be hashable"
    return 123456789

  @abstractmethod
  def __eq__(node1, node2):
    "Nodes must be comparable"
    return True


class MCTS():
  def __init__(self, exploration_weight:float=1):
    self.q = defaultdict(int)  # total reward of each node
    self.n = defaultdict(int)  # total visit count for each node
    self.children = dict()  # children of each node
    self.exploration_weight = exploration_weight
    self.saved_solutions = dict()


  def Choose(self, node:Node):
    """Choose the best successor of node. (Choose a move in the game)"""
    if node.IsTerminal():
      return node

    if node not in self.children:
      return node.FindRandomChild()

    def score(n):
      if self.n[n] == 0:
        return float("-inf")  # avoid unseen moves
      return self.q[n] / self.n[n]  # average reward

    for n in self.children[node]:
      print(f"{self.q[n]} / {self.n[n]} {score(n)}")
    return max(self.children[node], key=score)

  def Rollout(self, node):
    import actions
    "Make the tree one layer better. (Train for one iteration.)"
    path = self._Select(node)
    leaf = path[-1]
    self._Expand(leaf)
    reward = self._Simulate(leaf)
    self._Backpropagate(path, reward)

  def _Select(self, node):
    "Find an unexplored descendent of `node`"
    path = []
    while True:
      path.append(node)
      if node not in self.children or not self.children[node]:
        # node is either unexplored or terminal
        return path
      unexplored = self.children[node] - self.children.keys()
      if unexplored:
        n = unexplored.pop()
        path.append(n)
        return path
      node = self._UctSelect(node)  # descend a layer deeper

  def _Expand(self, node):
    "Update the `children` dict with the children of `node`"
    if node in self.children:
      return  # already expanded
    self.children[node] = node.FindChildren()

  def _Simulate(self, node):
    "Returns the reward for a random simulation (to completion) of `node`"
    return node.PlayUntilTermination()


  def _Backpropagate(self, path, reward):
      "Send the reward back up to the ancestors of the leaf"
      for node in reversed(path):
          self.n[node] += 1
          old_q = self.q[node]
          self.q[node] += reward

  def _UctSelect(self, node):
    "Select a child of node, balancing exploration & exploitation"

    # All children of node should already be expanded:
    assert all(n in self.children for n in self.children[node])

    log_n_vertex = math.log(self.n[node])

    def Uct(n):
      "Upper confidence bound for trees"
      return self.q[n] / self.n[n] + self.exploration_weight * math.sqrt(
        log_n_vertex / self.n[n]
      )

    return max(self.children[node], key=Uct)
