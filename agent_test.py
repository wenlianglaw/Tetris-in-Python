import unittest

import numpy as np

import agent
import game_client
import shape

class AgentTest(unittest.TestCase):
  def setUp(self) -> None:
    self.game = game_client.GameClient(5, 4)
    self.env = agent.Env(self.game.GetState, self.game.ProcessActions,
                    restart=self.game.Restart)
    self.agent = agent.Agent(env=self.env)

  def test_GetAllPossiblePositions(self):
    t = shape.T()
    t.y = 0
    rst = self.agent.GetAllPossiblePositions(t, self.game.GetState())
    print(rst)

    self.assertEqual(len(rst), 11)

#    (6, 0)
#    state: 0
#    0 1 0
#    1 1 1
#    0 0 0
#
#    [0 0 0 0]
#    [0 0 0 0]
#    [0 0 0 0]
#    [0 0 0 0]
#    [0 0 0 0]
#    [0 0 0 0]
#    [0 6 0 0]
#    [6 6 6 0]
    exp = [(6, 0, 0), (6, 1, 0),
           (5, 0, 2), (5, 1, 2),
           (5, -1, 1), (5, 0, 1), (5, 1, 1),
           (5, 0, 3), (5, 1, 3), (5, 2, 3),
           # swap
           (1,3,0)]

    for (p, action_list) in rst:
      self.assertTrue((p.x, p.y, p.state) in exp)


  def test_GetAllPossiblePositions_BTCanon(self):
    t =shape.T()
    (t.x, t.y) = (0, -1)
    t.Rotate90()

    self.game.width = 5
    self.game.map = np.array([
      #0  1  2  3  4
      [0, 0, 1, 1, 1],  # 0
      [0, 0, 1, 1, 1],  # 1
      [0, 0, 0, 1, 1],  # 2
      [1, 1, 0, 1, 1],  # 3
      [1, 0, 0, 1, 1],  # 4
      [1, 0, 0, 0, 1],  # 5
      [1, 1, 0, 1, 1],  # 6
      [1, 1, 0, 1, 1],  # 7
    ])

    rst = self.agent.GetAllPossiblePositions(t, self.game.GetState())

#   (4, 1)
#   state:2
#   0 0 0
#   1 1 1
#   0 1 0
#   [0 0 1 1 1]
#   [0 0 1 1 1]
#   [0 0 0 1 1]
#   [1 1 0 1 1]
#   [1 0 0 1 1]
#   [1 6 6 6 1]
#   [1 1 6 1 1]
#   [1 1 0 1 1]

    rst_set = set([(p.x, p.y, p.state) for (p, path) in rst])
    self.assertTrue((4,1,2) in rst_set)

  def test_GetAllPossiblePositions_BTCanon2(self):
    t = shape.T()
    self.game = game_client.GameClient()
    self.game.SpawnPiece(t)
    self.game.piece_list = [shape.T()] + self.game.piece_list

    self.game.map = np.array(
      [# 0  1  2  3  4  5  6  7  8  9
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
    )


    rst = self.agent.GetAllPossiblePositions(t, self.game.GetState())
    rst_set = set([(p.x, p.y, p.state) for (p, path) in rst])
    self.assertTrue((19, 1, 3) in rst_set)

if __name__ == '__main__':
  unittest.main()
