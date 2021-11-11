# Tetr.io hack
import numpy as np
from pynput import keyboard as kb


import time
import game_client
from agents import near_perfect_bot
from agents import agent
import shape
import actions

from tetrio import snapshot_board


# Read settings.bmp to get the box coordination



def SimulateAction(action: actions.Action):
  keyboard = kb.Controller()
  if action.rotation == 1:
    keyboard.press(kb.Key.f2)
    time.sleep(0.01)
    keyboard.release(kb.Key.f2)
  if action.rotation == 2:
    keyboard.press(kb.Key.f1)
    time.sleep(0.01)
    keyboard.release(kb.Key.f1)
  if action.rotation == 3:
    keyboard.press(kb.Key.f3)
    time.sleep(0.01)
    keyboard.release(kb.Key.f3)

  if action.direction == 1 or action.down:
    keyboard.tap(kb.Key.down)
  if action.direction == 2:
    keyboard.tap(kb.Key.left)
  if action.direction == 3:
    keyboard.tap(kb.Key.right)

  # Soft drop
  if action.direction == 4:
    keyboard.press(kb.Key.down)
    time.sleep(0.01)
    keyboard.release(kb.Key.down)

  # Hard drop
  if action.direction == 5:
    keyboard.tap(kb.Key.space)


def Run():
  snapshot = snapshot_board.SnapshotBoard()
  snapshot.Init("settings.bmp")

  game = game_client.GameClient()
  env = agent.Env(game=game)
  bot = near_perfect_bot.TheNearPerfectAgent(env=env)

  while True:
    snapshot.SnapshotGame()
    try:
      map = snapshot.GrabGameBoard()
      cur_piece_id = snapshot.GrabCurrentPiece()
    except ...:
      time.sleep(0.01)
      continue

    print("=========================")
    print(map)
    print("=========================")

    map = np.vstack(
      (np.zeros((game.map_height_padding, game.width), dtype=np.uint8), map)
    )
    game.SetWholeMap(map)
    game.TextDraw()
    if cur_piece_id == 0:
      continue
    game.SpawnPiece(shape.GetShapeFromId(cur_piece_id))
    actions = bot.MakeDecision()
    for action in actions:
      print(action)

    if True:
      time.sleep(0.050)
      for action in actions:
        SimulateAction(action)
        time.sleep(0.050)

    time.sleep(0.01)

if __name__ == "__main__":
  time.sleep(1.5)

  Run()
