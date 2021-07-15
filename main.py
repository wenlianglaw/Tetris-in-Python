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
keyboard = True

# Disable this to run the AI in background mode
enable_ui = True

# Backend game
game = game_client.GameClient(width=10, height=20)
game_th = threading.Thread(group=None, target=game.Run, daemon=True)

print(game.height, game.width)

# Initializes the front end UI with backend game.
ui = tetirs_ui.TetrisUI(game, keyboard=keyboard)

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

mcts_agent = mcts_agent.MCTSAgent(env, thread_num=1, iterations_per_move=200)
near_perfect_bot = near_perfect_bot.TheNearPerfectAgent(env, decision_interval=0.01)

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
