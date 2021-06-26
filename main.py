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

import agent
import mcts_agent
import game_client
import tetirs_ui

import numpy as np

keyboard = False

# Backend game
game = game_client.GameClient()

# Initializes the front end UI with backend game.
ui = tetirs_ui.TetrisUI(game, keyboard=keyboard)
th = threading.Thread(group=None, target=ui.Run, daemon=True)
th.start()


# Initializes the AI environment
# get_state:  Callable[[], game_client.GameState]
#           Observes the game state
# take_actions: Callable[[List[actions.Action]],None]
#           Takes the actions
# restart: Callable[[], None]
#           Resets the game.
env = agent.Env(get_state=game.GetState,
                take_actions=game.ProcessActions,
                restart=game.Restart)

random_agent = agent.Agent(env)
mcts_agent = mcts_agent.MCTSAgent(env)
# Agent being used
agent = mcts_agent
agent_th = threading.Thread(group=None, target=mcts_agent.RunUntilGameEnd, daemon=True)

if not keyboard:
  agent_th.start()


# Runs the game
if keyboard:
  game.Run()

# Exiting...
agent_th.join()
th.join()
