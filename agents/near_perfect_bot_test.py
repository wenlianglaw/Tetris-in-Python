import sys
from os.path import abspath, join, dirname

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.append(abspath(join(dirname(__file__), "..")))

import unittest

import numpy as np

from agents import agent
import game_client
import near_perfect_bot
import shape


class NearPerfectBotTest(unittest.TestCase):
  def setUp(self) -> None:
    self.game = game_client.GameClient()
    self.env = agent.Env(self.game)
    self.bot = near_perfect_bot.TheNearPerfectAgent(self.env)

  def SetUpGame(self, height, width):
    self.game = game_client.GameClient(height=height, width=width)
    self.env = agent.Env(self.game)
    self.bot = near_perfect_bot.TheNearPerfectAgent(self.env)

  def test_PlaceT_1(self):
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
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 16
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 17
        [0, 1, 1, 0, 0, 0, 0, 0, 0, 0],  # 18
        [0, 1, 1, 0, 1, 0, 0, 0, 0, 0],  # 19
        [0, 1, 1, 1, 0, 0, 0, 0, 0, 0],  # 20
        [0, 1, 1, 1, 1, 1, 1, 0, 0, 0],  # 21
        [0, 1, 1, 1, 1, 1, 1, 1, 0, 0],  # 22
        [0, 1, 1, 1, 1, 1, 1, 1, 0, 0], ]
    ))
    self.game.SpawnPiece(shape.T())
    actions = self.bot.MakeDecision()

    for a in actions:
      print(a)

    self.game.ProcessActions(actions)
    self.assertEqual(
      self.game.last_put_piece,
      shape.T(start_x=19, start_y=4))

  def test_PlaceT_2(self):
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
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 16
        [0, 1, 0, 0, 1, 1, 1, 1, 1, 0],  # 17
        [0, 1, 1, 0, 1, 1, 1, 0, 0, 0],  # 18
        [0, 1, 1, 0, 0, 1, 1, 0, 0, 0],  # 19
        [1, 1, 1, 0, 1, 1, 1, 0, 0, 0],  # 20
        [1, 1, 1, 0, 1, 1, 1, 0, 0, 0],  # 21
        [1, 1, 1, 0, 1, 1, 1, 0, 0, 0],  # 22
        [1, 1, 1, 0, 1, 1, 1, 0, 1, 1], ]
    ))
    self.game.SpawnPiece(shape.T())
    actions = self.bot.MakeDecision()

    for a in actions:
      print(a)
