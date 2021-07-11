# Ref: https://codemyroad.wordpress.com/2013/04/14/tetris-ai-the-near-perfect-player/

import game_client
from agents import agent

from typing import List

import actions
import numpy as np
import scipy.ndimage


class TheNearPerfectAgent(agent.Agent):
  def __init__(self, env: agent.Env):
    super().__init__(env)



  def MakeDecision(self) -> List[actions.Action]:
    def GetColHeight(col: np.array)->int:
      """Returns the height of a column.
      :param row: A 1-D array
      :returns height of this column.
      """
      row_height = len(col)
      for i in range(len(col) - 1, -1, -1):
        if col[i] != 0:
          row_height = i
      return len(col) - row_height

    state = self.env.get_state()
    ori_game = game_client.CreateGameFromState(state)

    all_possible_solutions = agent.GetPossiblePositionsQuickVersion(
       state.current_piece, ori_game)

    best_move = ()
    best_move_score = -np.inf

    for move in all_possible_solutions:
      # Puts piece
      game = ori_game.copy()
      prev_eliminated = game.accumulated_lines_eliminated
      game.ProcessActions(move[1])

      # Height of each col
      col_heights = [GetColHeight(game.map[:, i]) for i in range(state.width)]

      # aggregate_height
      aggregate_height = np.sum(col_heights)

      # complete lines
      complete_lines = game.accumulated_lines_eliminated - prev_eliminated

      # holes
      _, n = scipy.ndimage.measurements.label(game.map == 0)
      holes = n-1

      # Bumpiness
      bumpiness = 0
      for i in range(game.width-1):
        bumpiness += np.abs(col_heights[i] - col_heights[i+1])

      score = np.dot([-0.510066, 0.760666, -0.35663, -0.184483],
                     [aggregate_height, complete_lines, holes, bumpiness])

      if score > best_move_score:
        best_move = move
        best_move_score = score

    return best_move[1]
