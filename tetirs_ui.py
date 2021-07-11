# The front end of the game.  Displays the game status and takes the inputs
# from the keyboard.
#
# Initialize a game with the UI object, and cll UI.Run(), and UI will start
# displaying the game status including the current board, held piece and
# piece list.
#
# DAS and ARR can be set in this file.
#
# Hard drop and rotation actions can not be sent continuously:  They should be
# sent one by one.
# Down, left and right can be sent continuously:  Just keep pressing the keys.
#
# Leveling are set by the front end: (Current level = dropped lines /14)

import time

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import game_client
import shape
import actions

import numpy as np

COLOR_BKGD = np.array((30, 30, 30)) / 255
COLOR_I = np.array((143, 209, 172)) / 255
COLOR_J = np.array((81, 75, 169)) / 255
COLOR_L = np.array((204, 133, 80)) / 255
COLOR_T = np.array((158, 80, 200)) / 255
COLOR_O = np.array((208, 162, 70)) / 255
COLOR_S = np.array((207, 218, 49)) / 255
COLOR_Z = np.array((191, 80, 75)) / 255

BLOCK_SIZE = 15

DAS = 20  # ms
ARR = 80  # ms

# Control keys
SWAP = GLUT_KEY_UP
LEFT = GLUT_KEY_LEFT
RIGHT = GLUT_KEY_RIGHT
DOWN = GLUT_KEY_DOWN
HARD_DROP = b' '
ROTATE90 = b'r'
ROTATE180 = b'w'
ROTATE270 = b'e'
RESTART = b'g'

def GetColorFromPiece(piece):
  if isinstance(piece, shape.I):
    return COLOR_I
  if isinstance(piece, shape.J):
    return COLOR_J
  if isinstance(piece, shape.L):
    return COLOR_L
  if isinstance(piece, shape.T):
    return COLOR_T
  if isinstance(piece, shape.O):
    return COLOR_O
  if isinstance(piece, shape.S):
    return COLOR_S
  if isinstance(piece, shape.Z):
    return COLOR_Z


def GetColorFromID(id):
  color_map = dict({
    0: COLOR_BKGD,
    1: COLOR_I,
    2: COLOR_J,
    3: COLOR_L,
    4: COLOR_O,
    5: COLOR_S,
    6: COLOR_T,
    7: COLOR_Z,
  })
  if id not in color_map.keys():
    return COLOR_BKGD
  return color_map[id]


class TetrisUI:
  def __init__(self, game: game_client.GameClient, keyboard: bool = False,
               instant_soft_drop=True):
    self.game = game
    self.keyboard = keyboard
    self.input_buffer = []
    self.input_buffter_interval = 1
    self.input_last_sent = 0
    self.key_pressed = dict({
      "LEFT": False,
      "RIGHT": False,
      "DOWN": False,
      "SWAP": False,
    })
    self.das = DAS
    self.last_input = time.time()
    self.first_input = True
    self.arr = ARR
    self._rotation_active = True  # No DAS for rotation.  Controlled by this variable.
    self._hard_drop_active = True  # No DAS for hard_drop.  Controlled by this variable.

    # Used to count the sprint and 40 lines.
    self.start_time = time.time()
    self.sprint40_target_completed = False
    self.blitz_target_completed = False

    self.width = 1000
    self.height = 1000

    self.score = 0

    self.instant_soft_drop = instant_soft_drop
    self.already_instant_soft_dropped = False
    self._last_put_piece = None

  def _GlInit(self):
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glColor3f(0.2, 0.5, 0.4)
    glPointSize(5.0)
    glRotatef(-90, 0, 0, 1)
    gluOrtho2D(0, 1000, 0, 1000)
    glScale(1.5, 1.5, 0)

    # Moves camera up and left
    glTranslate(200, 250, 0)

  def _DrawBlock(self, i: int, j: int, color=(0.0, 0.0, 0.0), block_size: int = BLOCK_SIZE):
    glBegin(GL_QUADS)
    glColor3f(color[0], color[1], color[2])
    glVertex2f(i * block_size, j * block_size)
    glVertex2f((i + 1) * block_size, j * block_size)
    glVertex2f((i + 1) * block_size, (j + 1) * block_size)
    glVertex2f(i * block_size, (j + 1) * block_size)
    glEnd()

  def _GetShadowPiece(self) -> shape.Shape:
    piece = self.game.current_piece.copy()
    while self.game.CheckValidity(piece, (1, 0)):
      piece.x += 1
    return piece

  def _DrawPiece(self, piece: shape.Shape, color=None, offset_i: int = 0,
                 offset_j: int = 0, block_size: int = BLOCK_SIZE):
    if not piece:
      return

    if color is None:
      color = (0, 0, 0, 1.0)

    for (i,j) in piece.GetShape():
      self._DrawBlock(offset_i + i + piece.x, offset_j + j + piece.y,
                      color, block_size)

  def _DrawMap(self):
    for (i, row) in enumerate(self.game.map):
      for (j, cell) in enumerate(row):
        self._DrawBlock(i, j, GetColorFromID(cell))

  def _DrawPieceList(self):
    for (i, p) in enumerate(self.game.piece_list):
      self._DrawPiece(p, GetColorFromPiece(p), i * 3, 15, int(BLOCK_SIZE * 0.8))

  def _PrintScore(self):
    if self.keyboard:
      current_score = self.game.score
      if current_score != self.score:
        self.score = current_score
        print(current_score)

  def _SetLevel(self):
    if self.keyboard:
      self.game.SetLevel(int(self.game.piece_dropped / 14))

  def _Sprint40Record(self):
    if self.game.accumulated_lines_eliminated >= 40:
      if not self.sprint40_target_completed:
        print("40 lines:", time.time() - self.start_time)
        self.sprint40_target_completed = True

  def _BlitzRecord(self):
    if time.time() - self.start_time >= 120:
      if not self.blitz_target_completed:
        print("Blitz:", self.game.score)
        self.blitz_target_completed = True

  def display(self):
    glClear(GL_COLOR_BUFFER_BIT)

    self._PrintScore()
    self._Sprint40Record()
    self._BlitzRecord()
    self._SetLevel()
    self._ProcessKeys()
    self._DrawMap()
    self._DrawPiece(self._GetShadowPiece(),
                   0.08 * GetColorFromPiece(self.game.current_piece) + 0.3)
    self._DrawPiece(self.game.current_piece,
                    GetColorFromPiece(self.game.current_piece))

    self._DrawPiece(self.game.held_piece, GetColorFromPiece(self.game.held_piece),
                    -2, -8)

    self._DrawPieceList()

    glFlush()
    glutSwapBuffers()

  def _ProcessKeys(self):
    action = actions.Action()
    for (k, v) in self.key_pressed.items():
      if v:
        if k == "SWAP":
          action.swap = True
        elif k == "DOWN":
          action.down = True
        elif k == "LEFT":
          action.direction = actions.LEFT
        elif k == "RIGHT":
          action.direction = actions.RIGHT

        # Instant soft drop
        if (action.down and
            self.instant_soft_drop and
            not self.already_instant_soft_dropped):
          for _ in range(20):
            self.input_buffer.append(actions.Action(down=True))
          self.already_instant_soft_dropped = True

        if self.last_input + self.das / 1000 < time.time():
          self.input_buffer.append(action)
          self.last_input = time.time()

          if self.first_input:
            self.last_input = time.time() + self.arr / 1000
            self.first_input = False

    self.input_last_sent += 1
    if self.input_last_sent >= self.input_buffter_interval:
      self.game.InputActions(self.input_buffer)
      self.input_last_sent = 0
      self.input_buffer.clear()

    if self.game.last_put_piece != self._last_put_piece:
      self._last_put_piece = self.game.last_put_piece
      self.already_instant_soft_dropped = False

  def _SpecialInput(self, key, x, y):
    if key == SWAP:
      self.key_pressed["SWAP"] = True
    if key == DOWN:
      self.key_pressed["DOWN"] = True
    if key == LEFT:
      self.key_pressed["LEFT"] = True
    if key == RIGHT:
      self.key_pressed["RIGHT"] = True

  def _SpecialUpInput(self, key, x, y):
    if key == SWAP:
      self.key_pressed["SWAP"] = False
    if key == DOWN:
      self.key_pressed["DOWN"] = False
    if key == LEFT:
      self.key_pressed["LEFT"] = False
    if key == RIGHT:
      self.key_pressed["RIGHT"] = False
    self.first_input = True
    self.last_input = 0

  def _RestartGame(self):
    self.game.Restart()
    self.start_time = time.time()
    self.sprint40_target_completed = False
    self.blitz_target_completed = False

  def keyboardFunc(self, key, x, y):
    if key == ROTATE90:
      if self._rotation_active:
        self.input_buffer.append(actions.Action(rotation=1))
        self._rotation_active = False
    if key == ROTATE270:
      if self._rotation_active:
        self.input_buffer.append(actions.Action(rotation=3))
        self._rotation_active = False
    if key == ROTATE180:
      if self._rotation_active:
        self.input_buffer.append(actions.Action(rotation=2))
        self._rotation_active = False
    if key == HARD_DROP:
      if self._hard_drop_active:
        self.input_buffer.append(actions.Action(dir=actions.HARD_DROP))
        self._hard_drop_active = False
    if key == RESTART:
      self._RestartGame()

  def _KeyboardUpFunc(self, key, x, y):
    if key in (ROTATE90, ROTATE180, ROTATE270):
      self._rotation_active = True
    if key == HARD_DROP:
      self._hard_drop_active = True

    self.first_input = True
    self.last_input = 0

  def Run(self):
    glutInit()
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize(self.width, self.height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow("Tetris")
    self._GlInit()
    glutDisplayFunc(self.display)
    glutIdleFunc(self.display)
    if self.keyboard:
      glutKeyboardFunc(self.keyboardFunc)
      glutKeyboardUpFunc(self._KeyboardUpFunc)
      glutSpecialFunc(self._SpecialInput)
      glutSpecialUpFunc(self._SpecialUpInput)
    glutMainLoop()
