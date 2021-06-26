import unittest

import numpy as np

import actions
import game_client
import shape

class TestShapeRotations(unittest.TestCase):
  def test_I(self):
    i = shape.I()
    self.assertTrue(
      np.array_equal(i.shape, [
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0]]))

    self.assertEqual(0, i.state)

    i.Rotate90()
    self.assertTrue(
      np.array_equal(i.shape, [
        [0, 0, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 0]]))
    self.assertEqual(1, i.state)

    i.Rotate90()
    self.assertTrue(
      np.array_equal(i.shape, [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0]]))
    self.assertEqual(2, i.state)

    i.Rotate90()
    self.assertTrue(
      np.array_equal(i.shape, [
        [0, 1, 0, 0],
        [0, 1, 0, 0],
        [0, 1, 0, 0],
        [0, 1, 0, 0]]))
    self.assertEqual(3, i.state)

  def test_J(self):
    j = shape.J()
    self.assertTrue(
      np.array_equal(j.shape, [
        [1, 0, 0],
        [1, 1, 1],
        [0, 0, 0]]))
    self.assertEqual(0, j.state)

  def test_O(self):
    o = shape.O()
    self.assertTrue(
      np.array_equal(o.shape, [
        [0, 1, 1, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0]]))
    self.assertEqual(0, o.state)

    o.Rotate90()
    self.assertTrue(
      np.array_equal(o.shape, [
        [0, 1, 1, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0]]))
    self.assertEqual(1, o.state)

    o.Rotate90()
    self.assertTrue(
      np.array_equal(o.shape, [
        [0, 1, 1, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0]]))
    self.assertEqual(2, o.state)

    o.Rotate90()
    self.assertTrue(
      np.array_equal(o.shape, [
        [0, 1, 1, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0]]))
    self.assertEqual(3, o.state)

  def test_Eq(self):
    t1 = shape.T()
    t2 = shape.T()
    self.assertEqual(t1, t2)

class TestGameClient(unittest.TestCase):
  def setUp(self):
    self.game = game_client.GameClient(width=10, length=5)

  def test_PutPiece(self):
    i = shape.I()
    self.game.PutPiece(i)
    self.game.TextDraw()
    self.assertTrue(
      np.array_equal([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], self.game.map))

  def test_FailToPutPiece(self):
    i = shape.I()
    i.y = 9
    self.assertFalse(self.game.PutPiece(i))

  def test_RotationOK(self):
    self.game = game_client.GameClient(width=4, length=5)
    t = shape.T()
    (t.x, t.y) = (6,1)
    self.game.SpawnPiece(t)
    self.assertTrue(self.game.Rotate(1))

  def test_RotationFail(self):
    self.game = game_client.GameClient(width=3, length=4)
    i = shape.I()
    (i.x, i.y) = (0,0)
    i.Rotate90()
    self.game.SpawnPiece(i)
    self.assertFalse(self.game.Rotate(1))

  def test_I_Spin1(self):
    i = shape.I()
    i.Rotate90()
    i.y = 7

    self.game.SpawnPiece(i)
    self.game.TextDraw()

    self.game.Rotate(1)

    self.assertEqual(self.game.current_piece.x, i.x)
    self.assertEqual(self.game.current_piece.y, i.y-1)
    self.assertEqual(self.game.current_piece.state, 2)

  def test_I_Spin2(self):
    i = shape.I()
    i.Rotate270()
    i.x = 4
    i.y = 8
    print(i)

    self.game.map = np.array([
      #0  1  2  3  4  5  6  7  8  9
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 2
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 3
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 4
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 5
      [0, 0, 0, 0, 0, 2, 2, 2, 0, 0],  # 6
      [0, 0, 0, 0, 0, 2, 0, 0, 0, 0]]  # 7
    )

    self.game.SpawnPiece(i)
    self.game.TextDraw()

    self.game.Rotate(3)
    self.assertEqual(self.game.current_piece.x, 5)
    self.assertEqual(self.game.current_piece.y, 6)
    self.assertEqual(self.game.current_piece.state, 2)

    self.game.Rotate(1)
    self.assertEqual(self.game.current_piece.x, 4)
    self.assertEqual(self.game.current_piece.y, 8)
    self.assertEqual(self.game.current_piece.state, 3)

  def test_TSD270(self):
    t = shape.T()
    t.Rotate270()
    (t.x, t.y) = (5, 5)
    self.game.SpawnPiece(t)


    self.game.map = np.array([
      #0  1  2  3  4  5  6  7  8  9
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 2
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 3
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 4
      [2, 2, 2, 2, 2, 0, 0, 2, 2, 2],  # 5
      [2, 2, 2, 2, 2, 0, 0, 0, 2, 2],  # 6
      [2, 2, 2, 2, 2, 2, 0, 2, 2, 2]], # 7
    )

    self.game.Rotate(3)
    self.assertEqual(self.game.current_piece.x, 5)
    self.assertEqual(self.game.current_piece.y, 5)
    self.assertEqual(self.game.current_piece.state, 2)


  def test_TSD901(self):
    t = shape.T()
    t.Rotate90()
    (t.x, t.y) = (4, 4)
    self.game.SpawnPiece(t)


    self.game.map = np.array([
      #0  1  2  3  4  5  6  7  8  9
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 2
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 3
      [0, 0, 0, 0, 2, 0, 0, 2, 0, 0],  # 4
      [2, 2, 2, 2, 2, 0, 0, 2, 2, 2],  # 5
      [2, 2, 2, 2, 2, 0, 0, 0, 2, 2],  # 6
      [2, 2, 2, 2, 2, 2, 0, 2, 2, 2]]
    )

    self.game.Rotate(1)
    self.assertEqual(self.game.current_piece.x, 5)
    self.assertEqual(self.game.current_piece.y, 5)
    self.assertEqual(self.game.current_piece.state, 2)

  def test_TSD902(self):
    t = shape.T()
    t.Rotate270()
    (t.x, t.y) = (5, 5)
    self.game.SpawnPiece(t)


    self.game.map = np.array([
      #0  1  2  3  4  5  6  7  8  9
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 2
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 3
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 4
      [2, 2, 2, 2, 2, 0, 0, 2, 2, 2],  # 5
      [2, 2, 2, 2, 2, 0, 0, 0, 2, 2],  # 6
      [2, 2, 2, 2, 2, 2, 0, 2, 2, 2]]
    )

    self.game.Rotate(3)
    print(self.game.current_piece)

    self.assertEqual(self.game.current_piece.x, 5)
    self.assertEqual(self.game.current_piece.y, 5)
    self.assertEqual(self.game.current_piece.state, 2)

  def test_TST(self):
    t = shape.T()
    (t.x, t.y) = (2, 5)
    self.game.SpawnPiece(t)

    self.game.map = np.array([
      #0  1  2  3  4  5  6  7  8  9
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1
      [0, 0, 0, 0, 2, 2, 0, 0, 0, 0],  # 2
      [0, 0, 0, 0, 2, 0, 0, 0, 0, 0],  # 3
      [0, 0, 0, 0, 2, 0, 2, 2, 2, 2],  # 4
      [2, 2, 2, 2, 2, 0, 0, 2, 2, 2],  # 5
      [2, 2, 2, 2, 2, 0, 2, 2, 2, 2],  # 6
      [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]]
    )

    self.game.TextDraw()

    self.assertEqual(self.game.current_piece.x, 2)
    self.assertEqual(self.game.current_piece.y, 5)
    self.assertEqual(self.game.current_piece.state, 0)

    self.game.Rotate(1)
    self.assertEqual(self.game.current_piece.x, 4)
    self.assertEqual(self.game.current_piece.y, 4)
    self.assertEqual(self.game.current_piece.state, 1)

    self.game.Rotate(3)
    self.assertEqual(self.game.current_piece.x, 2)
    self.assertEqual(self.game.current_piece.y, 5)
    self.assertEqual(self.game.current_piece.state, 0)

  def test_MoveDown(self):
    i = shape.I()
    i.x = 5
    self.game.SpawnPiece(i)

    self.game.Move(actions.Action(down=True))
    self.assertEqual(self.game.current_piece.x, 6)

    self.game.Move(actions.Action(down=True))
    self.assertEqual(self.game.current_piece.x, 6)

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
    self.game.map = np.array([
      #0  1  2  3  4  5  6  7  8  9
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

    self.game.map = np.array([
      #0  1  2  3  4  5  6  7  8  9
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

    self.game.map = np.array([
      #0  1  2  3  4  5  6  7  8  9
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 2
      [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],  # 3
      [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],  # 4
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 5
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 6
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]  # 7
    )
    self.assertFalse(self.game.CheckGameOver())

  def test_LineClear(self):
    o = shape.O()
    o.x = 4

    self.game.map = np.array([
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
    self.assertTrue(np.all(self.game.map==0))
    self.assertEqual(self.game.map.shape, (self.game.length, self.game.width))

  def test_GameCopy(self):
    game = self.game.copy()

    nodes = dict()

    game1 = game.copy()
    game2 = game.copy()
    game3 = game.copy()

    nodes[game] = {game1, game2, game3}

    game.ProcessAction(actions.Action(down=True))

    for (k,v) in nodes.items():
      for g in v:
        self.assertEqual(g.current_piece, self.game.current_piece)

if __name__ == "__main__":
  unittest.main()
