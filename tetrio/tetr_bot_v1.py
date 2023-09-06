# Tetr.io hack
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import numpy as np

import time
import game_client
from agents import near_perfect_bot
from agents import agent
import shape

from tetrio import tetr_bot_keyboard as kb

from tetrio import snapshot_board


def Run():
  snapshot = snapshot_board.SnapshotBoard(window_box=(0, 0, 1700, 1700))
  snapshot.Init("settings.png")

  game = game_client.GameClient()
  env = agent.Env(game=game)
  bot = near_perfect_bot.TheNearPerfectAgent(env=env)

  while True:
    t = time.time()
    snapshot.SnapshotGame()
    print(1000 * (time.time() - t), "ms")
    try:
      board = snapshot.GrabGameBoard()
      cur_piece_id = snapshot.GrabCurrentPiece()
    except Exception as _:
      print("Didn't find any gameboard.  Will retry shortly after.")
      continue

    if cur_piece_id == 0:
      continue

    print("Board:", board)
    board = np.vstack(
      (np.zeros((game.map_height_padding, game.width),
                dtype=np.uint8), board)
    )

    game.SpawnPiece(shape.GetShapeFromId(cur_piece_id))
    game.SetWholeMap(board)
    if True:
      actions = bot.MakeDecision()
      for action in actions:
        print(action)

      time.sleep(0.00)
      for action in actions:
        kb.SimulateAction(action)
        time.sleep(0.100)
    if False:
      input()
      print("2..")
      time.sleep(1)
      print("1..")
      time.sleep(1)

    time.sleep(.31)

if __name__ == "__main__":
  time.sleep(1.5)
  Run()
