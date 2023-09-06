import time
from typing import Tuple, Text

import PIL
import numpy as np
from PIL import Image
from PIL import ImageFilter
from mss import mss

# This color seems different between MacOS and Windows?
COLORBASE_BOARD = [
  (182, 224, 64),  # Z, 7
  (145, 174, 58),  # S, 5
  (191, 83, 190),  # T, 6
  (216, 122, 52),  # L, 3
  (81, 71, 202),  # J,  2
  (121, 220, 160),  # I, 1
  (225, 191, 59),  # O, 4
]

COLOR_IDS = [7, 5, 6, 3, 2, 1, 4]

PIECE_NAME = "_IJLOSTZ"


def IsBackgroundColor(color: tuple) -> float:
  return np.sum(color) < 100

class SnapshotBoard(object):
  def __init__(self, window_box=(0, 0, 1700, 1700)):
    self.tetr_window_box = window_box
    self.cell_height = 0

    self.hold_box = (0, 0, 0, 0)

    self.board_box = (0, 0, 0, 0)

    self.next_boxes = []

    self.current_box = (0, 0, 0, 0)

    self.im = None

  def SaveImage(self, filename="img.png"):
    if self.im:
      self.im.save(filename)

  def _CaptureScreenshot(self):
    # Capture entire screen
    with mss() as sct:
      monitor = {"top": 0, "left": 0,
                 "width": self.tetr_window_box[2],
                 "height": self.tetr_window_box[3]}
      sct_img = sct.grab(monitor)
      return Image.frombytes(
        'RGB', sct_img.size,
        sct_img.bgra, 'raw', 'BGRX')

  def SnapshotGame(self):
    self.im = self._CaptureScreenshot()
    # self.im.save("im_debug.png")
    # self.im = self.im.crop(self.tetr_window_box)

  def ReadSettings(self, filename: Text):
    im_settings = Image.open(filename)
    im_settings.title = "settings"

    np_im = np.array(im_settings)
    print(np_im.shape)

    r = np_im[:, :, 0]
    g = np_im[:, :, 1]
    b = np_im[:, :, 2]

    r = (r >= 240) & (g <= 10)
    g = (r <= 10) & (g >= 240)
    b = (r <= 10) & (b >= 240)

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
    # im_board_edge.save("im_board_edge.png")
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
      if self._ColorChanged(prev_color, cur_color):
        cells_y.append(i)
      prev_color = cur_color

    for i in range(width):
      cur_color = im_board_edge.getpixel((i, 100))
      if self._ColorChanged(prev_color, cur_color):
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

    self.cell_height = np.average(cell_heights)

  def Init(self, settings_file_name: Text = "settings.bmp"):
    self.ReadSettings(settings_file_name)

  def _RejectOutliers(self, data, m=.5):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / mdev if mdev else 0.
    return data[s < m]

  def _ColorChanged(self, prev_color: Tuple[int, int, int],
                    cur_color: Tuple[int, int, int],
                    threshold: float = 4) -> bool:
    if np.sum(prev_color) == 0:
      return np.sum(cur_color) > 50
    return np.sum(cur_color) / np.sum(prev_color) >= threshold

  def _ColorChanged2(self, prev_color: Tuple[int, int, int],
                     cur_color: Tuple[int, int, int],
                     threshold: float = 500) -> bool:
    """Another experience function to detect color change."""
    var = np.var(np.subtract(prev_color, cur_color))
    return var >= threshold

  def _GetIdFromColor(self, color: Tuple[int, int, int], threshold=20, color_base=COLORBASE_BOARD):
    color_var = []
    for c in color_base:
      color_var.append(np.var(np.subtract(color, c)))
    min = np.argmin(color_var)
    color_var_bg = np.var(color)

    if color_var_bg < color_var[min]:
      return 0
    return COLOR_IDS[min]

  def GrabGameBoard(self) -> np.array:
    map = np.zeros(shape=(20, 10), dtype=np.uint8)
    for x in range(10):
      for y in range(20):
        cell_x = self.board_box[0] + self.cell_height / 2 + x * self.cell_height
        cell_y = self.board_box[1] + self.cell_height / 2 + y * self.cell_height
        color = self._TrimColor(self.im.getpixel((cell_x, cell_y)))
        # print(cell_x, cell_y, color)
        if np.var(color) > 40:
          map[y, x] = self._GetIdFromColor(color, threshold=100)

    return map

  def GrabHold(self) -> int:
    return 0

  def GrabCurrentPiece(self) -> int:
    # Scan for current piece
    colors = []
    cur_shape = np.zeros(shape=(2, 4))
    for i in range(4):
      for j in range(2):
        x = (3.5 + i) * self.cell_height + self.board_box[0]
        y = (-1.5 + j) * self.cell_height + self.board_box[1]
        color = self._TrimColor(self.im.getpixel((x, y)))
        if not IsBackgroundColor(color):
          colors.append(color)
    if not colors:
      print("cur: NULL")
      return 0

    # Color variance compared to the base
    color_variance = []
    colors_avg = np.average(colors, axis=0)
    for color_base in COLORBASE_BOARD:
      color_variance.append(np.var(np.array(colors_avg) - np.array(color_base)))

    id = COLOR_IDS[np.argmin(color_variance)]
    print("cur:", id, PIECE_NAME[id])
    return id

  def _TrimColor(self, color):
    if len(color) == 4:
      color = list(color)
      color.pop()
      color = tuple(color)
    return color


if __name__ == "__main__":
  time.sleep(1.5)
  snap = SnapshotBoard()
  snap.SnapshotGame()
  snap.ReadSettings("settings.png")
  print("current piece:", snap.GrabCurrentPiece())
  map = snap.GrabGameBoard()
  print(map)
