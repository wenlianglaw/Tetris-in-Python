import unittest

import game_client
from agents import agent
from agents import near_perfect_bot
import numpy as np

class NearPerfectBotTest(unittest.TestCase):
  def setUp(self) -> None:
    self.game = game_client.GameClient(5, 5)
    self.env = agent.Env(self.game)
    self.agent = near_perfect_bot.TheNearPerfectAgent(env=self.env)

  def test_GetHoles(self):
    self.game.color_map = np.array([
      # 0  1  2  3  4
      [0, 0, 0, 0, 0],  # 0
      [0, 0, 0, 0, 0],  # 1
      [1, 0, 0, 0, 0],  # 2
      [1, 1, 0, 0, 0],  # 3
      [1, 0, 0, 0, 0],  # 4
    ])

    holes = self.agent.GetHoles(self.game)
    self.assertEqual(holes, 1)

    self.game.color_map = np.array([
      # 0  1  2  3  4
      [0, 0, 0, 0, 0],  # 0
      [0, 1, 0, 0, 0],  # 1
      [1, 0, 1, 0, 0],  # 2
      [1, 1, 0, 0, 0],  # 3
      [1, 0, 0, 0, 0],  # 4
    ])
    holes = self.agent.GetHoles(self.game)
    self.assertEqual(holes, 4)

  def test_GetColHeight(self):
    self.game.color_map = np.array([
      # 0  1  2  3  4
      [0, 0, 0, 0, 0],  # 0
      [0, 1, 0, 0, 0],  # 1
      [1, 0, 1, 0, 0],  # 2
      [1, 1, 0, 0, 0],  # 3
      [1, 0, 0, 0, 0],  # 4
    ])

    col_heights = [self.agent.GetColHeight(self.game.color_map[:, i]) for i in range(self.game.width)]
    self.assertListEqual(col_heights, [3, 4, 3, 0, 0])
