# This file defines the back end of the Tetris game
#
# GameState is the base class of GameClient.
#
# GameClient.Run() will start two threads:
#  - _ProcessActions:  Process the action list every x seconds
#  - _AutoDrop:  Auto drops the current piece.
#
# GameClient:
#  - current piece
#  - held piece
#  - piece list
#  - color_map: game board
#  - InputActions(...):  Inputs a list of actions.
#  - ProcessActions(...): Lets the game client process a list of actions
#       directly
#  - ProcessAction(...): Lets the game client process one actions directly
#  - PutPiece(...): Puts the current piece if the position is valid.
#  - GetState(...): Gets game state, useful to AI
#  - CheckValidity(...): Checks if a move is valid
#  - SpawnPiece(...):  Sets the current piece.
#  - Restart(...): Restarts the game.
#  - Rotate(...): Alternatively, callers can directly call Rotate to rotate
#       current_piece
#  - Move(...): Alternatively, callers can directly call Move to move the
#       current_piece
#
import copy
import threading
import time
from threading import Lock
from typing import Tuple, List

import numpy as np

import actions
import shape
import queue

# Some global settings
DEFAULT_LENGTH = 20
DEFAULT_WIDTH = 10
MAP_PADDING_SIZE = 4
# When there are less than threshold pieces, spawn a new bag.
REFILL_THRESHOLD = 5

# Disable the auto drop in next few seconds
MAXIMUM_LOCK_TIME = 4
INCREMENTAL_LOCK_TIME = 1

# Scores
SINGLE = 5
DOUBLE = 10
TSS = 20
TRIPLE = 40
QUAD = 50
TSD = 60
TST = 80
PC = 120

# ATTACKS
ATTACK_DOUBLE = 1
ATTACK_TSS = 2
ATTACK_TRIPLE = 2
ATTACK_QUAD = 4
ATTACK_TSD = 4
ATTACK_TST = 6
ATTACK_PC = 10

class InternalError(Exception):
  """Any internal errors."""

class GameState:
  def __init__(self):
    self.height = 0
    self.width = 0
    self.color_map = np.array([])
    self.current_piece = None
    self.held_piece = None
    self.score = 0
    self.piece_list = []
    self.is_gameover = False
    self.can_swap = True
    self.accumulated_lines_eliminated = 0
    self.piece_dropped = 0
    self.blevel_increase = False
    self.level = 0
    self.line_sent = 0
    self.line_received = 0

  def __deepcopy__(self, memodict=None):
    if memodict is None:
      memodict = dict()
    another = copy.copy(self)
    another.color_map = self.color_map.copy()
    if self.current_piece is not None:
      another.current_piece = self.current_piece.copy()
    if self.held_piece is not None:
      another.held_piece = self.held_piece.copy()
    another.piece_list = copy.deepcopy(self.piece_list.copy())
    return another

  def copy(self):
    return self.__deepcopy__()

  def __str__(self):
    ret = ""
    ret += f"""height: {self.height}
width: {self.width}
color_map: {self.color_map}
current_piece: {self.current_piece}
held_piece: {self.held_piece}
score: {self.score}
piece_list: {self.piece_list}
is_gameover: {self.is_gameover}
can_swap: {self.can_swap}
piece_dropped: {self.piece_dropped}
level: {self.level}
    """

class GameClient(GameState):
  def __init__(self, height: int = DEFAULT_LENGTH, width: int = DEFAULT_WIDTH, map_height_padding=MAP_PADDING_SIZE,
               map_side_padding=MAP_PADDING_SIZE):
    super().__init__()

    self.height = height
    self.width = width
    self.map_height_padding = map_height_padding
    self.map_side_padding = map_side_padding

    self.dtype = np.uint8
    self.dtype_length = 8
    if self.width + 2 * map_side_padding > 8:
      self.dtype = np.uint16
      self.dtype_length = 16
    if self.width + 2 * map_side_padding > 16:
      self.dtype = np.uint32
      self.dtype_length = 32
    if self.width + 2 * map_side_padding > 32:
      self.dtype = np.uint64
      self.dtype_length = 64
    if self.width + 2 * map_side_padding > 64:
      self.dtype = np.uint128
      self.dtype_length = 128
    if self.width + 2 * map_side_padding > 128:
      raise InternalError(
        "width too long to support bit map.  Consider chaning it to a smaller value.")

    # Lock time settings
    # When the lock is enabled, count the lock time.
    # When the accumulated lock time is greater than the current maximum lock time,
    # force to perform the auto drop.  Otherwise autodop is disabled for this turn.
    # When current locktime is reached but an refresh lock time request is genertaed.
    # increase the current maximum lock time by incremental lock time.
    self.maximum_lock_time = MAXIMUM_LOCK_TIME
    self.current_maximum_lock_time = 0
    self.incremental_lock_time = INCREMENTAL_LOCK_TIME
    self.accumulate_lock_time = 0
    # Only when move  or rotate at bottom locks the auto drop
    self._enable_lock_time = False

    # Color map marks the color for each cell.
    self.color_map = np.array([[]], dtype=self.dtype)

    # Bit map for a better performance in some calculation.
    self.bit_map = np.array([], dtype=self.dtype)

    # Lock for current_piece
    self.mutex_current_piece = Lock()
    self.last_put_piece = None
    # List of actions to process
    self.action_list = queue.Queue()
    self._init_spawn_interval = 500  # 500 ms at level 0
    self._current_spawn_interval = 500
    # actions.Action
    self.last_action = None
    self.disable_autodrop = False
    self.line_tobesent = 0

    # Used when calculate the auto drop interval decrease based on current level.
    # Generated from the sigmoid function
    # x = np.linspace(0, 40, 40)
    # interval_decrease = 110 / (1 + np.exp(0.16 * x))
    # interval_decrease = np.cumsum(interval_decrease)
    # print(repr(np.cumsum(interval_decrease)))
    self.interval_decrease = np.array(
      [55., 100.49727968, 150.55179446, 190.28030383,
       230.85041422, 260.47244367, 290.38990828, 320.86947489,
       345.19115272, 350.63934095, 380.49515164, 400.03022699,
       410.5020957, 420.15098155, 430.19789113, 440.8437644,
       450.26946046, 455.63636342, 461.08741849, 465.74844074,
       469.72957119, 473.12678557, 476.02338748, 478.4914391,
       480.59310001, 482.38185737, 483.90364044, 485.19781892,
       486.29808909, 487.23325451, 488.02790975, 488.70303602,
       489.27651798, 489.76359062, 490.17722443, 490.52845671,
       490.82667585, 491.07986489, 491.2948099, 491.47727802])

    self._RefillPieces()
    self._TakePieceFromList()
    self.accumulated_lines_eliminated = 0

    # When soft-dropping, temporarily disable auto-drop
    self.soft_drop = False
    self.piece_dropped = 0

    # Must be put after the initializations above
    self._InitMap()

  def _InitMap(self):
    side_padding = (1<<self.map_side_padding) - 1
    init_row = (side_padding << (self.map_side_padding + self.width)) | side_padding
    bottom_padding = (1 << (self.width + 2 * self.map_side_padding)) - 1
    self.bit_map = np.concatenate((
      np.array((self.map_height_padding + self.height) * [init_row], dtype=self.dtype),
      np.array(self.map_height_padding * [bottom_padding], dtype=self.dtype)), dtype=self.dtype)


    self.color_map = np.array([[0 for i in range(self.width)] for x in range(self.height + self.map_height_padding)],
                              dtype=self.dtype)

  def Restart(self):
    self._InitMap()
    self.piece_list = []
    self.held_piece = None
    self.current_piece = None
    # Lock of the game state
    self.mutex_current_piece = Lock()
    self.is_gameover = False
    self.last_put_piece = None
    # List of actions to process
    self.action_list = queue.Queue()
    self._init_spawn_interval = 500.0
    self._current_spawn_interval = 500.0
    # actions.Action
    self.last_action = []
    self.can_swap = True
    self.score = 0
    self.accumulate_lock_time = 0
    self.accumulated_lines_eliminated = 0
    self.soft_drop = False
    self.piece_dropped = 0
    self.line_sent = 0
    self.line_received = 0
    self.line_tobesent = 0

    self._enable_lock_time = False

    self._RefillPieces()
    self._TakePieceFromList()

  def Run(self):
    auto_drop_th = threading.Thread(target=self.AutoDrop, name="auto_drop", daemon=True)
    process_input_th = threading.Thread(target=self._ProcessActionsThread, daemon=True)
    if not self.disable_autodrop:
      auto_drop_th.start()
    process_input_th.start()

    if not self.disable_autodrop:
      auto_drop_th.join()
    process_input_th.join()
    print("game ends")

  def GetState(self) -> GameState:
    """Gets game state.
      Returns the objects ref instead of copy For better performance.
    """
    return copy.deepcopy(super())

  def GetCell(self, i: int, j: int) -> int:
    """Gets cell at [i,j].
    Notes: This function doesn't check the index out of boundary error.
    """
    return self.color_map[i, j]

  def GetMap(self):
    """Gets whole color_map."""
    return self.color_map

  def GetMapArea(self, corner: Tuple[int, int],
                 size: Tuple[int, int]) -> np.array:
    """Gets an area of
    :param top_left:
    :param bottom_right:
    :return: The area of the color_map.
    """
    size = (np.min([size[0], self.color_map.shape[0] - corner[0]]),
            np.min([size[1], self.color_map.shape[1] - corner[1]]))

    return self.color_map[corner[0]: corner[0] + size[0],
           corner[1]: corner[1] + size[1]]

  def SetMap(self, pos: Tuple[int, int], v: int, map: np.array = None):
    """Sets the cell at [i,j] to value v."""
    (i, j) = pos
    bit_map = self.bit_map.copy()
    if map is None or map is self.color_map:
      map = self.color_map
      bit_map = self.bit_map
    map[i, j] = v

    # Set a bit to value: Clear to bit to 0 and then set to value
    bit_v = 0 if v == 0 else 1
    bit_j_pos = self.width + self.map_side_padding - 1 - j
    bit_map[i] = (bit_map[i] & ~(1 << bit_j_pos)) | (bit_v << bit_j_pos)

  def SetWholeMap(self, map: np.array):
    if map.shape != self.color_map.shape:
      raise InternalError(
        f"Map shape {map.shape}"
        f" must match the color_map shape: {self.color_map.shape}")

    self.color_map = map

    # Convert the map to Bollean map
    bit_color_map = map != 0

    # Revert the order and padding, then call the packbits(..., order="little") fn
    bit_color_map = bit_color_map[:, ::-1]
    bit_color_map = np.pad(
      bit_color_map,
      ((0, 0), (self.map_side_padding, self.map_side_padding)),
      "constant", constant_values=(1,))

    padding0_len = self.dtype_length - bit_color_map.shape[1]
    bit_color_map = np.pad(bit_color_map, ((0,0), (0, padding0_len)),
                     "constant", constant_values=(0,))

    int_color_map = np.packbits(bit_color_map, bitorder="little").view(self.dtype)
    self.bit_map[0:self.map_height_padding + self.height] = int_color_map
    print(int_color_map)
    print(self.bit_map)


  def copy(self):
    another = copy.copy(self)
    another.last_action = copy.copy(self.last_action)
    if self.last_put_piece is not None:
      another.last_put_piece = self.last_put_piece.copy()
    another.color_map = np.copy(self.color_map)
    another.bit_map = np.copy(self.bit_map)
    another.action_list = copy.copy(self.action_list)
    another.piece_list = self.piece_list.copy()
    another.current_piece = self.current_piece.copy()
    if self.held_piece is None:
      another.held_piece = None
    else:
      another.held_piece = self.held_piece.copy()
    return another

  def AutoDrop(self):
    while True:
      if self.soft_drop:
        # If it is soft dropping, we don't perform auto drop.
        self.soft_drop = False
      else:
        if self.CheckValidity(self.current_piece, offset=(1, 0)):
          self.Move(actions.Action(down=True, source_user_or_ai=False))
        else:
          if (not self._enable_lock_time or
              self.accumulate_lock_time >= self.current_maximum_lock_time):
            self.PutPiece()
          else:
            self.accumulate_lock_time += self._current_spawn_interval / 1000

      time.sleep(self._current_spawn_interval / 1000)

  def InputActions(self, acts: List[actions.Action]):
    if self.is_gameover:
      return

    if len(acts) > 30:
      print("len:", len(acts))
      acts = acts[-30:]

    for act in acts:
      if self.action_list.qsize() > 50:
        break
      self.action_list.put(act)

  def ProcessActions(self, actions: List[actions.Action], post_processing=True):
    for a in actions:
      self.ProcessAction(a, post_processing=post_processing)

  def ProcessAction(self, action: actions.Action, post_processing=True):
    if self.is_gameover:
      return
    # print(f"Processed action: {action.direction}, {action.rotation}, {action.swap}")
    # self.test += 1
    # print(self.test)
    if action.swap:
      self.Swap()
    self.Rotate(action.rotation)
    self.Move(action, post_processing=post_processing)

  def _ProcessActionsThread(self):
    while True:
      while not self.action_list.empty():
        act = self.action_list.get()
        self.ProcessAction(act)
        self.action_list.task_done()
      time.sleep(0.001)

  def SetLevel(self, level: int = 0):
    """Let the front end set!"""
    self.level = level

    i = min(len(self.interval_decrease), self.level)
    self._current_spawn_interval = max(
      10, self._init_spawn_interval - self.interval_decrease[i])

  def IncreaseLevel(self, inc: int = 1):
    """Let the front end decide!"""
    self.level += inc
    self.SetLevel(self.level)

  def Move(self, action: actions.Action, post_processing=True) -> bool:
    """Moves the current piece.
    :param direction: Direction to move
    :param post_processing: if True, put the piece to color_map and
           apply line eliminate. Otherwise just update the current_piece's states.
    :return True if moved; False otherwise
    """
    if (action.direction == actions.NONE and
        not action.down):
      return False

    moved = False
    if action.down:
      try:
        self.mutex_current_piece.acquire()
        if self.CheckValidity(self.current_piece, (1, 0)):
          self.current_piece.x += 1
          moved = True
          self.soft_drop = True
      finally:
        self.mutex_current_piece.release()

    if action.direction == actions.LEFT:
      try:
        self.mutex_current_piece.acquire()
        if self.CheckValidity(self.current_piece, (0, -1)):
          self.current_piece.y += -1
          moved = True
      finally:
        self.mutex_current_piece.release()

    if action.direction == actions.RIGHT:
      try:
        self.mutex_current_piece.acquire()
        if self.CheckValidity(self.current_piece, (0, 1)):
          self.current_piece.y += 1
          moved = True
      finally:
        self.mutex_current_piece.release()
    if action.direction == actions.HARD_DROP or action.direction == actions.SOFT_DROP:
      try:
        self.mutex_current_piece.acquire()
        while self.CheckValidity(self.current_piece, (1, 0)):
          self.current_piece.x += 1
          moved = True
      finally:
        self.mutex_current_piece.release()
        if post_processing and action.direction == actions.HARD_DROP:
          self.PutPiece()

    if moved:
      self.last_action = action

    at_bottom = not self.CheckValidity(self.current_piece, (1, 0))
    if (at_bottom and action.direction != actions.HARD_DROP and
        action.source_user):
      self._RefreshLockTime()

    return moved

  def _RefreshLockTime(self):
    self._enable_lock_time = True
    if self.accumulate_lock_time >= self.current_maximum_lock_time:
      self.current_maximum_lock_time = min(
        self.current_maximum_lock_time + self.incremental_lock_time,
        self.maximum_lock_time)

  def _ResetLockTime(self):
    self._enable_lock_time = False
    self.accumulate_lock_time = 0
    self.current_maximum_lock_time = 0

  def Swap(self):
    """Swaps the held piece and the current if its swappable"""
    if not self.can_swap:
      return

    try:
      self.mutex_current_piece.acquire()
      t = self.held_piece
      self.held_piece = self.current_piece
      self.current_piece = t

      if not self.current_piece:
        self._TakePieceFromList()

      self.current_piece.Init()
      self.held_piece.Init()
      self.can_swap = False
    finally:
      self.mutex_current_piece.release()

  def CheckGameOver(self):
    self.is_gameover = np.any(
      self.GetMapArea((0, 0), (self.map_height_padding, self.width)) != 0)

    return self.is_gameover

  def _AnalyzeElimination(self, n_eliminate: int) -> int:
    ret = 0
    is_last_put_t = isinstance(self.last_put_piece, shape.T)
    if n_eliminate == 1:
      if (is_last_put_t and self.last_action and self.last_action.rotation != 0):
        print("TSS")
        ret += TSS
        self.line_tobesent += ATTACK_TSS
      else:
        ret += SINGLE

    if n_eliminate == 2:
      # TSD
      if (is_last_put_t and self.last_action and self.last_action.rotation != 0):
        print("TSD")
        ret += TSD
        self.line_tobesent += ATTACK_TSD
      # Normal Double
      else:
        ret += DOUBLE
        self.line_tobesent += ATTACK_DOUBLE
    if n_eliminate == 3:
      # TST
      if (is_last_put_t and self.last_action and self.last_action.rotation != 0):
        print("TST")
        ret += TST
        self.line_tobesent += ATTACK_TST
      else:
        ret += TRIPLE
        self.line_tobesent += ATTACK_TRIPLE

    if n_eliminate == 4:
      ret += QUAD
      self.line_tobesent += ATTACK_QUAD

    # Checks for PC
    if np.all(self.color_map == 0):
      print("PC")
      ret += PC
      self.line_tobesent += ATTACK_PC

    return ret * (self.level + 3)

  def _LineClear(self):
    elimated_lines = []
    elimated_cnt = 0
    # Checks the 4 lines... This is not adapt to shape with higher than 4 lines
    # but that's not a part of this game.  I don't have plan to support custom
    # shapes.
    for row in range(4):
      if not (self.last_put_piece.x + row >= 0 and
              self.last_put_piece.x + row < self.height + self.map_height_padding):
        continue
      if np.all(self.color_map[self.last_put_piece.x + row, :] != 0):
        elimated_lines.append(row + self.last_put_piece.x)
        elimated_cnt += 1

    self.color_map = np.vstack((np.zeros((elimated_cnt, self.width),
                                         dtype=self.dtype),
                                np.delete(self.color_map, elimated_lines, axis=0)))

    # Updates the bit_map
    side_padding = (1<<self.map_side_padding) - 1
    init_row = (side_padding << (self.map_side_padding + self.width)) | side_padding
    self.bit_map = np.concatenate((elimated_cnt * [init_row],
                                   np.delete(self.bit_map, elimated_lines))).astype(self.dtype)

    self.accumulated_lines_eliminated += elimated_cnt
    self.score += self._AnalyzeElimination(n_eliminate=elimated_cnt)

  def _SendAttack(self):
    """Send attack to target."""
    # This feature has not been implemented yet.
    self.line_sent += self.line_tobesent
    self.line_tobesent = 0

  def PutPiece(self, piece: shape.Shape = None):
    """ Puts a piece to color_map if it is a valid placement then execute the post processing.

    :param piece: The piece to put, if None, put the self.current_piece
    :param color_map: The color_map where the piece puts, if None, self.color_map will be used.
    :returns: True if the piece has been put.  False otherwise.
    """
    if self._PrePutPiece(piece):
      self._PostPutPiece(piece)
      return True
    else:
      return False

  def _PrePutPiece(self, piece: shape.Shape = None, map: np.array = None):
    """ Puts a piece to color_map if it is a valid placement.
      Post put processing such as self._LineClear will not be executed

    :param piece: The piece to put, if None, put the self.current_piece
    :param map: The color_map where the piece puts, if None, self.color_map will be used.
    :returns: True if the piece has been put.  False otherwise.
    """
    try:
      if not piece:
        self.mutex_current_piece.acquire()
        piece = self.current_piece

      if map is None:
        map = self.color_map

      if not self.CheckValidity(piece):
        return False

      for (i, j) in piece.GetShape():
        self.SetMap((piece.x + i, piece.y + j), piece.id, map)
      return True
    finally:
      if self.mutex_current_piece.locked():
        self.mutex_current_piece.release()

  def _PostPutPiece(self, piece: shape.Shape = None):
    if piece is not None:
      self.last_put_piece = piece
    else:
      self.last_put_piece = self.current_piece

    # LineClear should be called prior to SendAttack
    self._LineClear()
    if piece is None:
      self._TakePieceFromList()

    self.CheckGameOver()
    self._ResetLockTime()
    self._SendAttack()
    self.can_swap = True
    self.piece_dropped += 1

  def TextDraw(self):
    preview_map = self.color_map.copy()
    self._PrePutPiece(self.current_piece, preview_map)
    for i in preview_map:
      print(i)
    print()

  def SpawnPiece(self, piece: shape.Shape = None) -> bool:
    if not piece:
      self._TakePieceFromList()
    else:
      self.current_piece = piece.copy()

    return self.CheckValidity(self.current_piece)

  def _FindFittedPiece(self, piece: shape.Shape = None, num_90rotations: int = 0):
    """Finds a location that fits this piece with n 90rotations.
    Ref: https://tetris.fandom.com/wiki/SRS
    :param piece: The piece to be put in the color_map.  If none, it will be set to the current_piece
    :param num_90rotations: How many 90 rotations
    :return: piece - shape.Shape: the piece with rotations that fits the color_map.
    """
    if not piece:
      piece = self.current_piece

    def _IsJLSTZ(piece: shape.Shape):
      jlstz = [shape.J, shape.L, shape.S, shape.T, shape.Z]
      for s in jlstz:
        if isinstance(piece, s):
          return True
      return False

    # The 180 rotation wall kick table is copied from
    # https://tetris.fandom.com/wiki/SRS#180.C2.B0_rotation
    # which is origined from
    # https://github.com/JoshuaWebb/nullpomino/blob/master/src/mu/nu/nullpo/game/subsystem/wallkick/StandardWallkick.java
    offset_map_jlstz = [
      # state 0
      ([(0, 0), (0, -1), (-1, -1), (2, 0), (2, -1)],  # 0>>1
       # 0>>2, 180 rotation
       [(1, 0), (2, 0), (1, 1), (2, 1), (-1, 0), (-2, 0), (-1, 1), (-2, 1), (0, -1), (3, 0), (-3, 0)],
       [(0, 0), (0, 1), (-1, 1), (2, 0), (2, 1)]),  # 0>>3

      # state 1
      ([(0, 0), (0, 1), (1, 1), (-2, 0), (-2, 1)],  # 1>>2
       # l>>3, 180 rotation
       [(0, 1), (0, 2), (-1, 1), (-1, 2), (0, -1), (0, -2), (-1, -1), (-1, -2), (1, 0), (0, 3), (0, -3)],
       [(0, 0), (0, 1), (1, 1), (-2, 0), (-2, 1)]),  # 1>>0

      # state 2
      ([(0, 0), (0, 1), (-1, 1), (2, 0), (2, 1)],  # 2>>3
       [(-1, 0), (-2, 0), (-1, -1), (-2, -1), (1, 0), (2, 0), (1, -1), (2, -1), (0, 1), (-3, 0), (3, 0)],  # 2>>0,
       [(0, 0), (0, -1), (-1, -1), (2, 0), (2, -1)]),  # 2>>1

      # state 3
      ([(0, 0), (0, -1), (1, -1), (2, 0), (-2, -1)],  # 3>>0
       # 3>>1, 180 rotation
       [(0, 1), (0, 2), (1, 1), (1, 2), (0, -1), (0, -2), (1, -1), (1, -2), (-1, 0), (0, 3), (0, -3)],
       [(0, 0), (0, -1), (1, -1), (2, 0), (-2, -1)]),  # 3>>2
    ]

    offset_map_i = [
      # state 0
      [[(0, 0), (0, -2), (0, 1), (1, -2), (-2, 1), ],  # 0>>1
       [(-1, 0), (-2, 0), (1, 0), (2, 0), (0, 1)],  # 0>>2, 180 rotation
       [(0, 0), (0, -1), (0, 2), (-2, -1), (1, 2)]],  # 0>>3

      # state 1
      [[(0, 0), (0, -1), (0, 2), (-2, -1), (1, 2)],  # 1>>2
       [(0, 1), (0, 2), (0, -1), (0, -2), (-1, 0)],  # 1>>3, 180 rotation,
       [(0, 0), (0, 2), (0, -1), (-1, 2), (2, -1)]],  # 1>>0

      # state 2
      [[(0, 0), (0, 2), (0, -1), (-1, 2), (2, -1)],  # 2>>3
       [(1, 0), (2, 0), (-1, 0), (-2, 0), (0, -1)],  # 2>>0, 180 rotation
       [(0, 0), (0, 1), (0, -2), (2, 1), (-1, -2)]],  # 2>>1

      # state 3
      [[(0, 0), (0, 1), (0, -2), (2, 1), (-1, -2)],  # 3>>0
       [(0, 1), (0, 2), (0, -1), (0, -2), (1, 0)],  # 3>>1, 180 rotation
       [(0, 0), (0, -2), (0, 1), (1, -2), (2, 1)]],  # 3>>2
    ]

    state = piece.state
    num_90rotations %= 4
    offset_piece = piece.copy()
    ori_x = offset_piece.x
    ori_y = offset_piece.y

    for _ in range(num_90rotations):
      offset_piece.Rotate90()

    if num_90rotations == 0:
      if self.CheckValidity(offset_piece):
        return offset_piece
    num_90rotations -= 1

    if _IsJLSTZ(piece):
      for (offset_x, offset_y) in offset_map_jlstz[state][num_90rotations]:
        offset_piece.x = ori_x + offset_x
        offset_piece.y = ori_y + offset_y
        if (offset_piece.y >= self.width or
            offset_piece.x >= self.height + self.map_height_padding):
          continue
        if self.CheckValidity(offset_piece):
          return offset_piece
    else:
      for (offset_x, offset_y) in offset_map_i[state][num_90rotations]:
        offset_piece.x = ori_x + offset_x
        offset_piece.y = ori_y + offset_y
        if (offset_piece.y >= self.width or
            offset_piece.x >= self.height + self.map_height_padding):
          continue
        if self.CheckValidity(offset_piece):
          return offset_piece

    return None

  def Rotate(self, n: int) -> bool:
    """Rotates the current piece.
    :param n:  rotations, in range [0,4)
    :return: True if the current piece can be rotated.  False otherwise.
    """
    n %= 4
    if n == 0:
      return False

    fitted_piece = self._FindFittedPiece(num_90rotations=n)
    if fitted_piece:
      self.current_piece = fitted_piece
      self.last_action = actions.Action(dir=0, rotation=n)

    if not self.CheckValidity(self.current_piece, (1, 0)):
      self._RefreshLockTime()

    return fitted_piece is not None

  def CheckValidity(self, piece: shape.Shape, offset: Tuple[int, int] = (0, 0)):
    """Checks if the piece with offset can be put in the color_map
    :param piece: The piece to be put.
    :param offset: The inital offset to the piece
    :return: True if the current state can fit into the color_map.  False otherwise.
    """
    (ox, oy, os) = (piece.x, piece.y, piece.state)
    piece.x += offset[0]
    piece.y += offset[1]

    a = self.bit_map[piece.x : piece.x + 4]
    b = self.width - piece.y
    c = piece.GetBitMap().astype(self.dtype)
    d = c << b
    e = a & d
    check_rst = e == 0
    (piece.x, piece.y, piece.state) = (ox, oy, os)
    return np.all(check_rst)

  def _GetNextBag(self):
    start_y = int((self.width - 3) / 2)
    assert start_y >= 0

    bag = [shape.I(start_y=start_y),
           shape.J(start_y=start_y),
           shape.L(start_y=start_y),
           shape.O(start_y=start_y),
           shape.S(start_y=start_y),
           shape.T(start_y=start_y),
           shape.Z(start_y=start_y)]
    np.random.shuffle(bag)
    return bag

  def _RefillPieces(self):
    """
    When there are less than REFILL_THRESHOLD pieces in the list,
    refill it with a new bag.
    """
    if len(self.piece_list) <= REFILL_THRESHOLD:
      self.piece_list.extend(self._GetNextBag())

  def _TakePieceFromList(self):
    self._RefillPieces()
    self.current_piece = self.piece_list[0].copy()
    self.piece_list = self.piece_list[1:]

def CreateGameFromState(state: GameState) -> GameClient:
  game = GameClient(height=state.height, width=state.width)
  game.color_map = np.copy(state.color_map)
  game.current_piece = state.current_piece.copy()
  if state.held_piece is not None:
    game.held_piece = state.held_piece.copy()
  else:
    game.held_piece = None
  game.score = state.score
  game.piece_list = state.piece_list.copy()
  game.can_swap = state.can_swap
  game.is_gameover = state.is_gameover
  game.accumulated_lines_eliminated = state.accumulated_lines_eliminated
  game.piece_dropped = state.piece_dropped
  game.line_sent = state.line_sent
  game.line_received = state.line_received
  return game
