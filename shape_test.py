import unittest

import numpy as np

import game_client
import shape


class TestShapeRotations(unittest.TestCase):
  def setUp(self):
    self.game = game_client.GameClient(height=5, width=10)

  def test_I(self):
    i = shape.I()
    print(i)
    (i.x, i.y) = (0, 0)

    self.game.SpawnPiece(i)
    self.game.PutPiece(i)
    self.assertTrue(
      np.array_equal(self.game.GetMapArea((0, 0), (4, 4)), i.id * np.array([
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0]])))

  def test_IRot90(self):
    i = shape.I()
    i.Rotate90()
    print(i)
    (i.x, i.y) = (0, 3)

    self.game.SpawnPiece(i)
    self.game.PutPiece()
    self.assertTrue(
      np.array_equal(self.game.GetMapArea((0, 3), (4, 4)), i.id * np.array([
        [0, 0, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 0]])))
    self.assertEqual(1, i.state)

  def test_IRot180(self):
    i = shape.I()
    i.Rotate180()
    print(i)

    (i.x, i.y) = (0, 3)
    self.game.SpawnPiece(i)
    self.game.PutPiece(i)
    self.assertTrue(
      np.array_equal(self.game.GetMapArea((0, 3), (4, 4)), i.id * np.array([
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0]])))
    self.assertEqual(2, i.state)

  def test_IRot270(self):
    i = shape.I()
    i.Rotate270()
    print(i)

    (i.x, i.y) = (0, 3)

    self.game.SpawnPiece(i)
    self.game.PutPiece(i)
    self.assertTrue(
      np.array_equal(self.game.GetMapArea((0, 3), (4, 4)), i.id * np.array([
        [0, 1, 0, 0],
        [0, 1, 0, 0],
        [0, 1, 0, 0],
        [0, 1, 0, 0]])))
    self.assertEqual(3, i.state)

  def test_J(self):
    j = shape.J()

    (j.x, j.y) = (0, 3)
    self.game.SpawnPiece(j)
    self.game.PutPiece()

    self.assertTrue(
      np.array_equal(self.game.GetMapArea((0, 3), (4, 4)), j.id * np.array([
        [1, 0, 0, 0],
        [1, 1, 1, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]])))
    self.assertEqual(0, j.state)

  def test_O(self):
    o = shape.O()

    (o.x, o.y) = (0, 3)
    self.game.SpawnPiece(o)
    self.game.PutPiece()

    self.assertTrue(
      np.array_equal(self.game.GetMapArea((0, 3), (4, 4)), o.id * np.array([
        [0, 1, 1, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]])))
    self.assertEqual(0, o.state)

  def test_Eq(self):
    t1 = shape.T()
    t2 = shape.T()
    self.assertEqual(t1, t2)

  def test_Copy(self):
    t1 = shape.T()
    t2 = t1
    t2.x += 1
    self.assertEqual(t1, t2)

    t2 = t1.copy()
    t2.x += 1
    self.assertNotEqual(t1, t2)
