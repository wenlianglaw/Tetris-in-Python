# Tetris implementation for AI
#
# Map size: 10 * 20
# Length buffer lines: 3
# Bags: 7-Bag random
# Sliding: Yes
# Locking: Yes
# - 1s incremental locking time
# - 3s maximum locking time
#
# Spins:
# -  T-Spin
# -  ZS Spin: Yes
# -  LJ Spin: Yes
# -  I Spin: Yes
# -  O Spin: NO since I don't know how it works,
#      and its rarely used in real games.
#
# B2B: No
#
# Rotations:
# - 90 Degree rotation: Yes
# - 180 Degree rotation: Yes. No wall-kicks
# - 270 Degree rotation: Yes
#
# Backend: game_client
# Frontend: PyOPenGL
#   DAS: YES
#   ARR: YES
#
#
# Run
# To play with keyboard.  Set keyboard=True
# To play with an idiot AI, set keyboard = False and pass the agent with
# the AI you want.
#
#
# Reference:
#   Spins: https://tetris.fandom.com/wiki/SRS
#
# Wenliang
# 2021.06

import threading

from agents import agent
from agents import mcts_agent
from agents import near_perfect_bot

import game_client
import tetirs_ui

# Other I/O settings can be configured in the tetris_ui.py file
keyboard = False

# Disable this to run the AI in background mode
enable_ui = True

# Backend game
game = game_client.GameClient(width=10, height=20)
import shape
game.SpawnPiece(shape.T())
game.piece_list = [shape.O()] + game.piece_list
game_th = threading.Thread(group=None, target=game.Run, daemon=True)

print(game.height, game.width)

# Initializes the front end UI with backend game.
ui = tetirs_ui.TetrisUI(game, keyboard=keyboard)

# Initializes the AI environment
env = agent.Env(game=game)

random_agent = agent.Agent(env)
mcts_agent = mcts_agent.MCTSAgent(env, thread_num=1, iterations_per_move=200)
near_perfect_bot = near_perfect_bot.TheNearPerfectAgent(env, decision_interval=0.001)

# Agent being used
agent = near_perfect_bot
agent_th = threading.Thread(group=None, target=agent.RunGame, daemon=True)

if not keyboard:
  agent_th.start()

# Runs the game
if keyboard:
  game_th.start()

if enable_ui:
  ui.Run()

# Exiting...
agent_th.join()

if keyboard:
  game_th.join()
