import unittest

import numpy as np
from parameterized import parameterized

import actions
import game_client
import shape
from agents import agent


class AgentTest(unittest.TestCase):
  def setUp(self) -> None:
    self.game = game_client.GameClient(5, 4)
    self.env = agent.Env(game=self.game)
    self.agent = agent.Agent(env=self.env)

  def _CheckPaths(self, rst):
    for (s, ps) in rst:
      self._CheckPath(s, ps)

  def _CheckPath(self, final_state, path):
    # Checks the paths
    if path[0].swap:
      return
    game = self.game.copy()
    game.ProcessActions(path, post_processing=False)
    self.assertEqual(final_state, game.current_piece)

  @parameterized.expand([
    [agent.GetAllPossiblePositions],
    [agent.GetPossiblePositionsQuickVersion],
    [agent.GetPossiblePositionsQuickVersion2],
  ])
  def test_GetAllPossiblePositions(self, test_fn):
    t = shape.T()
    t.y = 0
    rst = test_fn(t, self.game)
    for r in rst:
      print(r[0])

    self.assertEqual(len(rst), 11)

    #    (6, 0)
    #    state: 0
    #    0 1 0
    #    1 1 1
    #    0 0 0
    #
    #    [0 0 0 0] 0
    #    [0 0 0 0] 1
    #    [0 0 0 0] 2
    #    [0 0 0 0] 3
    #    [0 0 0 0] 4
    #    [0 0 0 0] 5
    #    [0 0 0 0] 6
    #    [0 6 0 0] 7
    #    [6 6 6 0] 8
    exp = [(7, 0, 0), (7, 1, 0),
           (6, -1, 1), (6, 0, 1), (6, 1, 1),
           (6, 0, 2), (6, 1, 2),
           (6, 0, 3), (6, 1, 3), (6, 2, 3),
           # swap
           (1, 0, 0)]

    for (p, action_list) in rst:
      if not action_list[0].swap:
        self.assertTrue((p.x, p.y, p.state) in exp)

  @parameterized.expand([
    [agent.GetAllPossiblePositions],
    [agent.GetPossiblePositionsQuickVersion],
    [agent.GetPossiblePositionsQuickVersion2],
  ])
  def test_GetAllPossiblePositions_BTCanon(self, test_fn):
    self.game = game_client.GameClient(height=8, width=4)

    t = shape.T()
    (t.x, t.y) = (4, -1)
    t.Rotate90()

    self.game.SetWholeMap(np.array([
      # 0  1  2  3
      [0, 0, 0, 0],  # -4
      [0, 0, 0, 0],  # -3
      [0, 0, 0, 0],  # -2
      [0, 0, 0, 0],  # -1
      [0, 0, 1, 1],  # 0
      [0, 0, 1, 1],  # 1
      [0, 0, 0, 1],  # 2
      [1, 1, 0, 1],  # 3
      [1, 0, 0, 1],  # 4
      [1, 0, 0, 0],  # 5
      [1, 1, 0, 1],  # 6
      [1, 1, 0, 1],  # 7
    ]))

    rst = test_fn(t, self.game)

    #   (4, 1)
    #   state:2
    #   0 0 0
    #   1 1 1
    #   0 1 0
    #   [0 0 1 1]
    #   [0 0 1 1]
    #   [0 0 1 1]
    #   [0 0 0 1]
    #   [1 1 0 1]
    #   [1 0 0 1]
    #   [1 6 6 6]
    #   [1 1 6 1]
    #   [1 1 0 1]

    rst_set = set([(p.x, p.y, p.state) for (p, path) in rst])
    self.assertTrue((8, 1, 2) in rst_set)

  @parameterized.expand([
    [agent.GetAllPossiblePositions],
    [agent.GetPossiblePositionsQuickVersion],
    [agent.GetPossiblePositionsQuickVersion2],
  ])
  def test_GetAllPossiblePositions_BTCanon2(self, test_fn):
    t = shape.T()
    self.game = game_client.GameClient(width=10, height=19)
    self.game.SpawnPiece(t)
    self.game.piece_list = [shape.T()] + self.game.piece_list

    self.game.SetWholeMap(np.array(
      [  # 0  1  2  3  4  5  6  7  8  9
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 2
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 3
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 4
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 5
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 6
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 7
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 8
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 9
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 10
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 11
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 12
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 13
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 14
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 15
        [0, 0, 1, 1, 1, 1, 1, 1, 1, 1],  # 16
        [0, 0, 0, 1, 1, 1, 1, 1, 1, 1],  # 17
        [1, 1, 0, 1, 1, 1, 1, 1, 1, 1],  # 18
        [1, 0, 0, 1, 1, 1, 1, 1, 1, 1],  # 19
        [1, 0, 0, 0, 1, 1, 1, 1, 1, 1],  # 20
        [1, 1, 0, 1, 1, 1, 1, 1, 1, 1],  # 21
        [1, 1, 0, 1, 1, 1, 1, 1, 1, 1], ]
    ))

    rst = test_fn(t, self.game)
    rst_set = set([(p.x, p.y, p.state) for (p, path) in rst])
    self.assertIn((19, 1, 2), rst_set)

  @parameterized.expand([
    [agent.GetAllPossiblePositions],
    [agent.GetPossiblePositionsQuickVersion],
    [agent.GetPossiblePositionsQuickVersion2],
  ])
  def test_GetAllPossiblePositions_Quick_T(self, test_fn):
    t = shape.T(start_x=0, start_y=0)
    self.game = game_client.GameClient(height=6, width=5)
    self.game.SetWholeMap(np.array(
      [  # 0  1  2  3  4
        [0, 0, 0, 0, 0, ],  # -4
        [0, 0, 0, 0, 0, ],  # -3
        [0, 0, 0, 0, 0, ],  # -2
        [0, 0, 0, 0, 0, ],  # -1
        [0, 0, 0, 0, 0, ],  # 0
        [0, 0, 0, 0, 0, ],  # 1
        [0, 0, 0, 0, 0, ],  # 2
        [2, 2, 0, 0, 2, ],  # 3
        [2, 0, 0, 0, 2, ],  # 4
        [2, 2, 0, 2, 2, ],  # 5
      ]
    ))

    self.game.SpawnPiece(t)
    rst = test_fn(t, self.game)

    for (x, p) in rst:
      print(x)
    # Checks the final states
    # The quick solution is suppose to at least get 4 T-spin rotations.
    self.assertEqual(len(rst), 18)

    # And the T-Spin double should at least be in the ans.
    rst_set = set([(p.x, p.y, p.state) for (p, path) in rst])
    self.assertIn((7, 1, 2), rst_set)

    # Checks the paths
    self._CheckPaths(rst)

  @parameterized.expand([
    [agent.GetAllPossiblePositions],
    [agent.GetPossiblePositionsQuickVersion],
    [agent.GetPossiblePositionsQuickVersion2],
  ])
  def test_GetAllPossiblePositions_Quick_O(self, test_fn):
    o = shape.O(start_x=2, start_y=0)
    self.game = game_client.GameClient(height=6, width=5)
    self.game.color_map = np.array(
      [  # 0  1  2  3  4
        [0, 0, 0, 0, 0, ],  # -4
        [0, 0, 0, 0, 0, ],  # -3
        [0, 0, 0, 0, 0, ],  # -2
        [0, 0, 0, 0, 0, ],  # -1
        [0, 0, 0, 0, 0, ],  # 0
        [0, 0, 0, 0, 0, ],  # 1
        [0, 0, 0, 0, 0, ],  # 2
        [0, 0, 0, 0, 0, ],  # 3
        [0, 0, 0, 0, 0, ],  # 4
        [0, 0, 0, 0, 0, ],  # 5
      ]
    )

    self.game.SpawnPiece(o)

    rst = test_fn(o, self.game)

    # Since this is an O shape, there are only 4 + 1(swap) possible solutions.
    self.assertEqual(len(rst), 5)

    self._CheckPaths(rst)

  @parameterized.expand([
    [agent.GetAllPossiblePositions],
    [agent.GetPossiblePositionsQuickVersion],
    [agent.GetPossiblePositionsQuickVersion2],
  ])
  def test_GetAllPossiblePositions_Quick_Z(self, test_fn):
    z = shape.Z(start_x=0, start_y=0)
    self.game = game_client.GameClient(height=6, width=5)
    self.game.SpawnPiece(z)

    self.game.color_map = np.array(
      [  # 0  1  2  3  4
        [0, 0, 0, 0, 0, ],  # 0
        [0, 0, 0, 0, 0, ],  # 1
        [0, 0, 0, 0, 0, ],  # 2
        [6, 0, 0, 0, 0, ],  # 3
        [6, 6, 2, 0, 0, ],  # 4
        [6, 6, 6, 3, 3, ],  # 5
      ]
    )

    rst = test_fn(z, self.game)

    self._CheckPaths(rst)

  @parameterized.expand([
    [agent.GetAllPossiblePositions],
    [agent.GetPossiblePositionsQuickVersion],
    [agent.GetPossiblePositionsQuickVersion2],
  ])
  def test_GetAllPossiblePositions_Quick_RotSlideRotSlide(self, test_fn):
    """Tests rotation -> slide -> rotation -> slide."""
    i = shape.I(start_x=2, start_y=0)
    self.game = game_client.GameClient(height=6, width=5)
    self.game.SpawnPiece(i)

    rst = test_fn(i, self.game)
    self._CheckPaths(rst)

    for (s, _) in rst:
      self.game.SpawnPiece(s)
      self.game.TextDraw()

    rst_set = set([(p.x, p.y, p.state) for (p, path) in rst])
    self.assertIn((8, 1, 0), rst_set)

  def test_CleanedPath(self):
    rst = [
      (shape.T(), [actions.Action(dir=actions.SOFT_DROP), actions.Action(dir=actions.HARD_DROP)]),
      (shape.T(),
       [actions.Action(dir=actions.LEFT), actions.Action(dir=actions.RIGHT), actions.Action(dir=actions.SOFT_DROP),
        actions.Action(dir=actions.HARD_DROP)]),
    ]

    self.assertEqual(len(rst[0][1]), 2)
    self.assertEqual(len(rst[1][1]), 4)
    agent.CleanRst(rst)
    self.assertEqual(len(rst[0][1]), 1)
    self.assertEqual(len(rst[1][1]), 1)

if __name__ == '__main__':
  unittest.main()
