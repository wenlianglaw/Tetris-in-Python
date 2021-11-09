import unittest

import numpy as np

from agents import agent
import game_client
import shape

class AgentTest(unittest.TestCase):
  def setUp(self) -> None:
    self.game = game_client.GameClient(5, 4)
    self.env = agent.Env(game=self.game)
    self.agent = agent.Agent(env=self.env)

  def _CheckPaths(self, rst):
    for(s, ps) in rst:
      self._CheckPath(s, ps)

  def _CheckPath(self, final_state, path):
    # Checks the paths
    if path[0].swap:
      return
    game = self.game.copy()
    game.ProcessActions(path, post_processing=False)
    self.assertEqual(final_state, game.current_piece)

  def test_GetAllPossiblePositions(self):
    t = shape.T()
    t.y = 0
    rst = agent.GetAllPossiblePositions(t, self.game)
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

  def test_GetAllPossiblePositions_BTCanon(self):
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

    rst = agent.GetAllPossiblePositions(t, self.game)

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

  def test_GetAllPossiblePositions_BTCanon2(self):
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

    rst = agent.GetAllPossiblePositions(t, self.game)
    rst_set = set([(p.x, p.y, p.state) for (p, path) in rst])
    self.assertIn((19, 1, 2), rst_set)

  def test_GetAllPossiblePositions_Quick_T(self):
    t = shape.T(start_x=0, start_y=0)
    self.game = game_client.GameClient(height=6, width=5)
    self.game.SetWholeMap(np.array(
      [# 0  1  2  3  4
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
    rst = agent.GetPossiblePositionsQuickVersion(t, self.game)

    # Checks the final states
    # The quick solution is suppose to at least get 4 T-spin rotations.
    self.assertEqual(len(rst), 17)

    # And the T-Spin double should at least be in the ans.
    rst_set = set([(p.x, p.y, p.state) for (p, path) in rst])
    self.assertIn((7, 1, 2), rst_set)

    # Checks the paths
    self._CheckPaths(rst)

  def test_GetAllPossiblePositions_Quick_O(self):
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

    rst = agent.GetPossiblePositionsQuickVersion(o, self.game)

    # Since this is an O shape, there are only 4 + 1(swap) possible solutions.
    self.assertEqual(len(rst), 5)

    self._CheckPaths(rst)

  def test_GetAllPossiblePositions_Quick_Z(self):
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

      rst = agent.GetPossiblePositionsQuickVersion(z, self.game)

      self._CheckPaths(rst)

  def test_GetAllPossiblePositions_Quick_RotSlideRotSlide(self):
    """Tests rotation -> slide -> rotation -> slide."""

    i = shape.I(start_x=2, start_y=0)
    self.game = game_client.GameClient(height=6, width=5)
    self.game.SpawnPiece(i)

    rst = agent.GetPossiblePositionsQuickVersion(i, self.game)
    self._CheckPaths(rst)

    for (s, _) in rst:
      self.game.SpawnPiece(s)
      self.game.TextDraw()

    rst_set = set([(p.x, p.y, p.state) for (p, path) in rst])
    self.assertIn((8, 1, 0), rst_set)

if __name__ == '__main__':
  unittest.main()
