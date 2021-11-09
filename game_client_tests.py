import unittest

import numpy as np

import actions
import game_client
import shape

def _PrintBitMap(bit_map):
  for x in bit_map:
    print(bin(x))

class TestGameClient(unittest.TestCase):
  def setUp(self):
    self.game = game_client.GameClient(height=5, width=10)

  def test_CheckValidity(self):
    game = game_client.GameClient(height=5, width=5, map_height_padding=4)

    game.SetMap((3,3), shape.O().id)
    print(game.color_map)
    _PrintBitMap(game.bit_map)

    t = shape.T()
    t.x = 0
    t.y = 0
    self.assertTrue(game.CheckValidity(t))

    t.x += 1
    self.assertTrue(game.CheckValidity(t))

    t.x += 1
    self.assertTrue(game.CheckValidity(t))

    t.y += 1
    self.assertFalse(game.CheckValidity(t))

    t.x = 2
    t.y = 0
    self.assertTrue(game.CheckValidity(t))
    self.assertFalse(game.CheckValidity(t, offset=(0, 1)))

  def test_CheckValidity2(self):
    game = game_client.GameClient(height=5, width=5, map_height_padding=4)

    for i in range(4):
      game.SetMap((2, i), shape.O().id)


    i = shape.I()
    i.x = 0
    i.y = 0
    self.assertTrue(game.CheckValidity(i))
    game.SpawnPiece(i)
    game.TextDraw()
    self.assertFalse(game.CheckValidity(i, (1,0)))




  def test_PutPiece(self):
    self.game = game_client.GameClient(height=8, width=10, map_height_padding=0)
    i = shape.I()
    (i.x, i.y) = (0, 3)
    self.game.SpawnPiece(i)
    self.game.TextDraw()
    self.game.PutPiece(i)
    self.game.TextDraw()
    _PrintBitMap(self.game.bit_map)
    self.assertTrue(
      #                0  1  2  3  4  5  6  7  8  9
      np.array_equal([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0
                      [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],  # 1
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 2
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 3
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 4
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 5
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 6
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], self.game.color_map))

  def test_FailToPutPiece(self):
    self.game = game_client.GameClient(height=4, width=10)
    i = shape.I()
    i.y = 8
    self.assertFalse(self.game.PutPiece(i))

  def test_RotationOK(self):
    self.game = game_client.GameClient(height=6, width=4)

    t = shape.T()
    (t.x, t.y) = (4 + self.game.map_height_padding, 0)
    # Rotate 1
    self.game.SpawnPiece(t)
    self.assertTrue(self.game.Rotate(1))
    expected = shape.T(3 + self.game.map_height_padding, -1)
    expected.state = 1
    self.assertEqual(self.game.current_piece, expected)

    # Rotate 2
    self.game.SpawnPiece(t)
    self.assertTrue(self.game.Rotate(2))
    expected = shape.T(3 + self.game.map_height_padding, 0)
    expected.state = 2
    self.assertEqual(self.game.current_piece, expected)

    # Rotate 3
    self.game.SpawnPiece(t)
    self.assertTrue(self.game.Rotate(3))
    expected = shape.T(3 + self.game.map_height_padding, 1)
    expected.state = 3
    print(self.game.current_piece)
    print(expected)
    self.assertEqual(self.game.current_piece, expected)

  def test_SpawnPieceFail(self):
    self.game = game_client.GameClient(height=4, width=3)
    i = shape.I()
    (i.x, i.y) = (0, 0)
    self.assertFalse(self.game.SpawnPiece(i))

  def test_RotationFail(self):
    self.game = game_client.GameClient(height=4, width=3)
    i = shape.I()
    (i.x, i.y) = (3, 0)
    i.Rotate90()
    self.assertTrue(self.game.SpawnPiece(i))
    self.assertFalse(self.game.Rotate(1))

  def test_I_Spin1(self):
    i = shape.I()
    i.Rotate90()
    i.y = 7

    self.game.SpawnPiece(i)
    self.game.TextDraw()

    self.game.Rotate(1)
    self.game.TextDraw()

    self.assertEqual(self.game.current_piece.x, i.x)
    self.assertEqual(self.game.current_piece.y, i.y - 1)
    self.assertEqual(self.game.current_piece.state, 2)

  def test_I_Spin2(self):
    self.game = game_client.GameClient(height=8, width=10)
    i = shape.I()
    i.Rotate270()
    i.x = 4 + 4
    i.y = 8
    print(i)

    self.game.SetWholeMap(np.array([
      #0  1  2  3  4  5  6  7  8  9
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # -4
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # -3
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # -2
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # -1
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 2
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 3
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 4
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 5
      [0, 0, 0, 0, 0, 2, 2, 2, 0, 0],  # 6
      [0, 0, 0, 0, 0, 2, 0, 0, 0, 0]]  # 7
    ))

    self.game.SpawnPiece(i)
    self.game.TextDraw()

    self.game.Rotate(3)
    self.game.TextDraw()
    self.assertEqual(self.game.current_piece.x, i.x + 1)
    self.assertEqual(self.game.current_piece.y, i.y - 2)
    self.assertEqual(self.game.current_piece.state, 2)

    self.game.Rotate(1)
    self.assertEqual(self.game.current_piece.x, i.x)
    self.assertEqual(self.game.current_piece.y, i.y)
    self.assertEqual(self.game.current_piece.state, 3)

  def test_TSD270(self):
    self.game = game_client.GameClient(height=8, width=10)
    t = shape.T()
    t.Rotate270()
    (t.x, t.y) = (5 + 4, 5)
    self.game.SpawnPiece(t)

    self.game.SetWholeMap(np.array([
      # 0  1  2  3  4  5  6  7  8  9
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # -4
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # -3
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # -2
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # -1
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 2
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 3
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 4
      [2, 2, 2, 2, 2, 0, 0, 2, 2, 2],  # 5
      [2, 2, 2, 2, 2, 0, 0, 0, 2, 2],  # 6
      [2, 2, 2, 2, 2, 2, 0, 2, 2, 2]],  # 7
    ))
    self.game.TextDraw()

    self.game.Rotate(3)
    self.assertEqual(self.game.current_piece.x, 5 + 4)
    self.assertEqual(self.game.current_piece.y, 5)
    self.assertEqual(self.game.current_piece.state, 2)

  def test_TSD901(self):
    self.game = game_client.GameClient(height=8, width=10)
    t = shape.T()
    t.Rotate90()
    (t.x, t.y) = (4 + 4, 4)
    self.game.SpawnPiece(t)

    self.game.SetWholeMap(np.array([
      # 0  1  2  3  4  5  6  7  8  9
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # -4
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # -3
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # -2
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # -1
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 2
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 3
      [0, 0, 0, 0, 2, 0, 0, 2, 0, 0],  # 4
      [2, 2, 2, 2, 2, 0, 0, 2, 2, 2],  # 5
      [2, 2, 2, 2, 2, 0, 0, 0, 2, 2],  # 6
      [2, 2, 2, 2, 2, 2, 0, 2, 2, 2]]
    ))

    self.game.Rotate(1)
    self.assertEqual(self.game.current_piece.x, 5 + 4)
    self.assertEqual(self.game.current_piece.y, 5)
    self.assertEqual(self.game.current_piece.state, 2)

  def test_TSD902(self):
    self.game = game_client.GameClient(height=8, width=10)
    t = shape.T()
    t.Rotate270()
    (t.x, t.y) = (5 + 4, 5)
    self.game.SpawnPiece(t)

    self.game.SetWholeMap(np.array([
      # 0  1  2  3  4  5  6  7  8  9
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # -4
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # -3
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # -2
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # -1
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 2
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 3
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 4
      [2, 2, 2, 2, 2, 0, 0, 2, 2, 2],  # 5
      [2, 2, 2, 2, 2, 0, 0, 0, 2, 2],  # 6
      [2, 2, 2, 2, 2, 2, 0, 2, 2, 2]]
    ))

    self.game.Rotate(3)
    print(self.game.current_piece)

    self.assertEqual(self.game.current_piece.x, 5 + 4)
    self.assertEqual(self.game.current_piece.y, 5)
    self.assertEqual(self.game.current_piece.state, 2)

  def test_TST(self):
    self.game = game_client.GameClient(height=8, width=10)
    t = shape.T()
    (t.x, t.y) = (2 + 4, 5)
    self.game.SpawnPiece(t)

    self.game.SetWholeMap(np.array([
      # 0  1  2  3  4  5  6  7  8  9
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # -4
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # -3
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # -2
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # -1
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1
      [0, 0, 0, 0, 2, 2, 0, 0, 0, 0],  # 2
      [0, 0, 0, 0, 2, 0, 0, 0, 0, 0],  # 3
      [0, 0, 0, 0, 2, 0, 2, 2, 2, 2],  # 4
      [2, 2, 2, 2, 2, 0, 0, 2, 2, 2],  # 5
      [2, 2, 2, 2, 2, 0, 2, 2, 2, 2],  # 6
      [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]]
    ))

    self.game.TextDraw()

    self.assertEqual(self.game.current_piece.x, 2 + 4)
    self.assertEqual(self.game.current_piece.y, 5)
    self.assertEqual(self.game.current_piece.state, 0)

    self.game.Rotate(1)
    self.assertEqual(self.game.current_piece.x, 4 + 4)
    self.assertEqual(self.game.current_piece.y, 4)
    self.assertEqual(self.game.current_piece.state, 1)

    self.game.Rotate(3)
    self.assertEqual(self.game.current_piece.x, 2 + 4)
    self.assertEqual(self.game.current_piece.y, 5)
    self.assertEqual(self.game.current_piece.state, 0)

  def test_MoveDown(self):
    i = shape.I()
    i.x = 2
    i.y = 0
    print(i)
    self.game.SpawnPiece(i)
    self.game.TextDraw()

    self.game.Move(actions.Action(down=True))
    self.assertEqual(self.game.current_piece.x, 3)

    self.game.Move(actions.Action(down=True))
    self.assertEqual(self.game.current_piece.x, 4)

    # Set to bottom
    i.x = self.game.height + self.game.map_height_padding - 2
    self.game.SpawnPiece(i)
    self.game.TextDraw()
    self.game.Move(actions.Action(down=True))
    self.assertEqual(self.game.current_piece.x, i.x)


  def test_MoveLeft(self):
    i = shape.I()
    i.y = 1
    self.game.SpawnPiece(i)

    self.game.Move(actions.Action(dir=actions.LEFT))
    self.assertEqual(self.game.current_piece.y, 0)

    self.game.Move(actions.Action(dir=actions.LEFT))
    self.assertEqual(self.game.current_piece.y, 0)

  def test_Swap(self):
    p = self.game.current_piece
    p.Rotate90()
    next_p = self.game.piece_list[0]

    self.assertIsNone(self.game.held_piece)
    self.game.Swap()
    self.assertEqual(p, self.game.held_piece)
    self.assertEqual(self.game.current_piece, next_p)

    # Put a piece so that we can swap again
    self.game.PutPiece()
    print(self.game.can_swap)

    # Swap again, and expect the piece to be reset
    current_piece = self.game.held_piece.copy()
    current_piece.Init()
    self.game.Swap()
    self.assertEqual(current_piece, self.game.current_piece)

  def test_IsGameOver(self):
    self.game = game_client.GameClient(height=4, width=10)
    self.game.color_map = np.array([
      # 0  1  2  3  4  5  6  7  8  9
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0
      [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],  # 1
      [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],  # 2
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 3
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 4
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 5
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 6
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]  # 7
    )
    self.assertTrue(self.game.CheckGameOver())

    self.game.color_map = np.array([
      # 0  1  2  3  4  5  6  7  8  9
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1
      [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],  # 2
      [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],  # 3
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 4
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 5
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 6
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]  # 7
    )
    self.assertTrue(self.game.CheckGameOver())

    self.game.color_map = np.array([
      # 0  1  2  3  4  5  6  7  8  9
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 2
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 3
      [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],  # 4
      [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],  # 5
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 6
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]  # 7
    )
    self.assertFalse(self.game.CheckGameOver())

  def test_LineClear(self):
    self.game = game_client.GameClient(height=8, width=10)
    o = shape.O()
    o.x = 4

    self.game.color_map = np.array([
      # 0  1  2  3  4  5  6  7  8  9
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 2
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 3
      [2, 2, 2, 2, 0, 0, 2, 2, 2, 2],  # 4
      [2, 2, 2, 2, 0, 0, 2, 2, 2, 2],  # 5
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 6
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]  # 7
    )

    self.game.SpawnPiece(o)
    self.game.PutPiece()
    self.assertTrue(np.all(self.game.color_map == 0))
    self.assertEqual(self.game.color_map.shape, (self.game.height, self.game.width))

  def test_GameCopy(self):
    game = self.game.copy()

    nodes = dict()

    game1 = game.copy()
    game2 = game.copy()
    game3 = game.copy()

    nodes[game] = {game1, game2, game3}

    game.ProcessAction(actions.Action(down=True))

    for (k, v) in nodes.items():
      for g in v:
        self.assertEqual(g.current_piece, self.game.current_piece)

  def test_SetMap_BitMap_OK(self):
    self.game = game_client.GameClient(height=5, width=5)

    for x in self.game.bit_map:
      print(bin(x))
    print(self.game.color_map)

    self.game.SetMap((0,0), 1)
    self.assertEqual(self.game.bit_map[0], 0b1111_10000_1111)
    self.assertTrue(np.array_equal(self.game.color_map[0],
                                   np.array([1,0,0,0,0])))

    self.game.SetMap((1, 2), 1)
    self.assertEqual(self.game.bit_map[1], 0b1111_00100_1111)
    self.assertTrue(np.array_equal(self.game.color_map[1],
                                   np.array([0, 0, 1, 0, 0])))

    self.game.SetMap((1, 2), 0)
    self.assertEqual(self.game.bit_map[1], 0b1111_00000_1111)
    self.assertTrue(np.array_equal(self.game.color_map[1],
                                   np.array([0, 0, 0, 0, 0])))

  def test_SetWholeMap_ColorMapOK(self):
    self.game = game_client.GameClient(height=5, width=5)

    v = np.array([
      [0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0],
      [1, 1, 2, 2, 3],
      [1, 1, 2, 2, 3],
      [1, 1, 2, 2, 3],
      [1, 1, 2, 2, 3],
      [1, 1, 2, 2, 3],
    ])

    self.game.SetWholeMap(v)
    self.assertTrue(np.array_equal(self.game.color_map, v))


  def test_SetWholeMap_BitMapOK(self):
    game = game_client.GameClient(height=5, width=5)
    v = np.array([
      [0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0],
      [1, 1, 2, 2, 0],
      [1, 1, 2, 0, 3],
      [1, 1, 0, 2, 3],
      [1, 0, 2, 2, 3],
      [0, 1, 2, 2, 3],
    ])
    game.SetWholeMap(v)

    print(game.bit_map)
    for x in game.bit_map:
      print(bin(x))

    for i in range(game.map_height_padding):
      self.assertEqual(game.bit_map[i],
                       0b1111000001111)

    self.assertEqual(game.bit_map[4],
                     0b1111111101111)

    self.assertEqual(game.bit_map[5],
                     0b1111111011111)

  def test_SetWholeMap_Fail(self):
    # Fail when the value size doesn't match the color_map size.
    self.game = game_client.GameClient(height=5, width=5)

    v = np.array([
      [0, 0, 0, 0],
      [0, 0, 0, 0],
      [0, 0, 0, 0],
      [0, 0, 0, 0],
      [1, 2, 2, 3],
      [1, 2, 2, 3],
      [1, 2, 2, 3],
      [1, 2, 2, 3],
      [1, 2, 2, 3],
    ])

    # Width doesn't match
    with self.assertRaises(game_client.InternalError) as _:
      self.game.SetWholeMap(v)

  def test_GetMapArea(self):
    self.game = game_client.GameClient(height=5, width=5)

    v = np.array([
      [0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0],
      [1, 2, 2, 3, 4],
      [1, 2, 2, 3, 4],
      [1, 2, 2, 3, 4],
      [1, 2, 2, 3, 4],
      [1, 2, 2, 3, 4],
    ])

    self.game.SetWholeMap(v)

    expected = np.array([
      [1, 2],
      [1, 2],
    ])

    self.assertTrue(np.array_equal(self.game.GetMapArea((4, 0), (2, 2)), expected))

    rst = self.game.GetMapArea((0, 0), (20, 20))
    self.assertTrue(np.array_equal(rst, v))

  def test_GetCell(self):
    self.game = game_client.GameClient(height=5, width=5)

    v = np.array([
      [0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0],
      [1, 2, 2, 3, 4],
      [1, 2, 2, 3, 4],
      [1, 2, 2, 3, 4],
      [1, 2, 2, 3, 4],
      [1, 2, 2, 3, 4],
    ])

    self.game.SetWholeMap(v)

    self.assertEqual(0, self.game.GetCell(0, 0))
    self.assertEqual(2, self.game.GetCell(5, 1))
    self.assertEqual(3, self.game.GetCell(6, 3))

    with self.assertRaises(IndexError) as _:
      self.assertEqual(3, self.game.GetCell(0, 7))

  def test_GetMap(self):
    self.game = game_client.GameClient(height=5, width=5)

    v = np.array([
      [0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0],
      [1, 2, 2, 3, 4],
      [1, 2, 2, 3, 4],
      [1, 2, 2, 3, 4],
      [1, 2, 2, 3, 4],
      [1, 2, 2, 3, 4],
    ])

    self.game.SetWholeMap(v)
    self.assertTrue(np.array_equal(self.game.GetMap(), v))

  def test_Nump(self):
    l = 5
    w = 5
    init_row = (0b1111 << (4 + w)) | 0b1111
    print(init_row)
    print(bin(init_row))

    map = np.array((l + 8) * [init_row])
    for r in map:
      print(bin(r))

    print(map.size)

    i = 1
    j = 2

    i = 4 + i
    j = 3 + w - j

    mask = 1 << j
    print(map[i] & mask)

    map[i] |= mask
    print(map[i] & mask != 0)
    for r in map:
      print(bin(r))

  def test_InitMap(self):
    game = game_client.GameClient(height=10, width=8)
    for row in game.bit_map:
      print(bin(row))

    init_row = 0b1111_00000000_1111
    for i in range(game.height + game.map_height_padding):
      self.assertEqual(game.bit_map[i], init_row)

    padding = 0b1111_11111111_1111
    for i in range(game.map_height_padding):
      self.assertEqual(
        game.bit_map[i + game.map_height_padding + game.height], padding)

if __name__ == "__main__":
  unittest.main()
