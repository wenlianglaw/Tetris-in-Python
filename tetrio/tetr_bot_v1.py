# Tetr.io hack

import PIL
from PIL import ImageGrab
from PIL import ImageFilter
from PIL import Image
from pynput import keyboard as kb
import numpy as np

from typing import Tuple, Text

import time
import game_client
from agents import near_perfect_bot
from agents import agent
import shape
import actions
import tetirs_ui
import threading

COLORBASE_BOARD = [
  (185, 90, 90),  # Z
  (154, 186, 72),  # S
  (174, 97, 172),  # T
  (192, 126, 77),  # L
  (100, 97, 184),  # J
  (102, 175, 135),  # I
  (196, 178, 86),  # O
]

COLORBASE_CUR = [
  (237, 133, 98),  # Z
  (250, 251, 126),  # S
  (239, 145, 194),  # T
  (248, 204, 94),  # L
  (158, 137, 199),  # J
  (169, 249, 196),  # I
  (255, 251, 125),  # O
]

PIECE_NAME = "_IJLOSTZ"

# Read settings.bmp to get the box coordination

class SnapshotBoard(object):
  def __init__(self):
    self.tetr_window_box = (0, 0, 1300, 1300)
    self.cell_height = 0

    self.hold_box = (0, 0, 0, 0)

    self.board_box = (0, 0, 0, 0)

    self.next_boxes = []

    self.current_box = (0, 0, 0, 0)

    self.im = None

  def SnapshotGame(self):
    self.im = ImageGrab.grab()
    self.im = self.im.crop(self.tetr_window_box)

  def ReadSettings(self, filename: Text):
    im_settings = Image.open(filename)
    im_settings.title = "settings"

    # hold_color = (0, 255, 0)
    # board_color = (255, 0, 0)
    # next_color = (0, 0, 255)

    np_im = np.array(im_settings)
    print(np_im.shape)

    r = np_im[:, :, 0]
    g = np_im[:, :, 1]
    b = np_im[:, :, 2]

    r = (r == 255) & (g == 0)
    g = (r == 0) & (g == 255)
    b = (r == 0) & (b == 255)

    board_box = np.nonzero(r)
    board_box_top = board_box[0][0]
    board_box_left = board_box[1][0]
    board_box_bot = board_box[0][-1]
    board_box_right = board_box[1][-1]
    self.board_box = (board_box_left,
                      board_box_top,
                      board_box_right,
                      board_box_bot)
    print("board:", self.board_box)
    self._GetCellSpec(im_settings.crop(self.board_box).convert("L"))
    print("cell height:", self.cell_height)

  def _GetCellSpec(self, im_board: Image):
    im_board_edge = im_board.filter(PIL.ImageFilter.FIND_EDGES)
    # Scan from top to detect the border of each cell
    height = im_board_edge.height
    width = im_board_edge.width
    print("h:", height)
    print("w:", width)
    prev_color = im_board_edge.getpixel((width / 2, 0))
    cells_y = []
    cells_x = []
    for i in range(height):
      cur_color = im_board_edge.getpixel((width / 2, i))
      if self._ColorDrasticalyChanged(prev_color, cur_color):
        cells_y.append(i)
      prev_color = cur_color

    for i in range(width):
      cur_color = im_board_edge.getpixel((i, 100))
      if self._ColorDrasticalyChanged(prev_color, cur_color):
        cells_x.append(i)
      prev_color = cur_color

    merged = cells_y + cells_x
    ori_cell_heights = np.subtract(merged + [0], [0] + merged)
    print(ori_cell_heights)
    cell_heights = self._RejectOutliers(ori_cell_heights, m=1.6)
    print(cell_heights)
    m = 0.5
    while len(cell_heights) == 0:
      m += 0.1
      cell_heights = self._RejectOutliers(ori_cell_heights, m)

    print(cell_heights)
    cell_height = np.median(cell_heights)

    self.cell_height = cell_height

  def Init(self, settings_file_name: Text = "settings.bmp"):
    self.ReadSettings(settings_file_name)

  def _GetIdFromColor(self, color: Tuple[int, int, int], threshold=20, color_base=COLORBASE_BOARD):
    colors_id = [7, 5, 6, 3, 2, 1, 4]
    color_var = []
    for c in color_base:
      color_var.append(np.var(np.subtract(color, c)))
    min = np.argmin(color_var)
    color_var_bg = np.var(color)

    if color_var_bg < color_var[min]:
      return 0
    return colors_id[min]

  def _RejectOutliers(self, data, m=.5):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / mdev if mdev else 0.
    return data[s < m]

  def _ColorDrasticalyChanged(self, prev_color: Tuple[int, int, int],
                              cur_color: Tuple[int, int, int],
                              threshold: float = 4) -> bool:
    if np.sum(prev_color) == 0:
      return np.sum(cur_color) > 50
    return np.sum(cur_color) / np.sum(prev_color) >= threshold

  def GrabGameBoard(self) -> np.array:
    map = np.zeros(shape=(20, 10), dtype=np.uint8)
    for x in range(10):
      for y in range(20):
        cell_x = self.board_box[0] + self.cell_height / 2 + x * self.cell_height
        cell_y = self.board_box[1] + self.cell_height / 2 + y * self.cell_height
        color = self.im.getpixel((cell_x, cell_y))
        # print(cell_x, cell_y, color)
        if np.var(color) > 40:
          map[y, x] = self._GetIdFromColor(color, threshold=100)

    return map

  def GrabHold(self) -> int:
    return 0

  def GetCurrentPiece(self) -> int:
    pos_x = -self.cell_height + (self.board_box[0] + self.board_box[2]) // 2
    pos_y = -1.6 * self.cell_height + self.board_box[1]
    color = self.im.getpixel((pos_x, pos_y))
    id = self._GetIdFromColor(color, color_base=COLORBASE_CUR)
    print("cur pos", pos_x, pos_y, color)
    print("cur:", id, PIECE_NAME[id])
    return id

def SimulateAction(action: actions.Action):
  keyboard = kb.Controller()
  if action.rotation == 1:
    keyboard.tap(kb.Key.f2)
  if action.rotation == 2:
    keyboard.tap(kb.Key.f1)
  if action.rotation == 3:
    keyboard.tap(kb.Key.f3)

  if action.direction == 1 or action.down:
    keyboard.tap(kb.Key.down)
  if action.direction == 2:
    keyboard.tap(kb.Key.left)
  if action.direction == 3:
    keyboard.tap(kb.Key.right)

  # Soft drop
  if action.direction == 4:
    keyboard.tap(kb.Key.down)

  if action.direction == 5:
    keyboard.tap(kb.Key.space)

game = game_client.GameClient()

def Run():
  snapshot_board = SnapshotBoard()
  snapshot_board.Init("settings_40.bmp")

  env = agent.Env(game=game)



  bot = near_perfect_bot.TheNearPerfectAgent(env=env)

  while True:
    snapshot_board.SnapshotGame()
    try:
      map = snapshot_board.GrabGameBoard()
      cur_piece_id = snapshot_board.GetCurrentPiece()
    except ...:
      continue
    finally:
      time.sleep(0.001)
      # print(color_map)

    game.color_map[-20:, :] = map
    if cur_piece_id == 0:
      continue
    game.current_piece = shape.GetShapeFromId(cur_piece_id)
    actions = bot.MakeDecision()
    for action in actions:
      print(action)

    for action in actions:
      SimulateAction(action)
      time.sleep(0.001)

if __name__ == "__main__":
  time.sleep(0.5)

  Run()
