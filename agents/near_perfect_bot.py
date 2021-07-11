# Ref: https://codemyroad.wordpress.com/2013/04/14/tetris-ai-the-near-perfect-player/

import game_client
from agents import agent
import shape

from typing import List, Tuple

import actions
import numpy as np


class TheNearPerfectAgent(agent.Agent):
  def __init__(self, env: agent.Env,
               weights: Tuple[float, float,float,float] =
               (-0.510066, 0.760666, -0.35663, -0.184483),
               decision_interval: float = 0.1):
    super().__init__(env, decision_interval)
    self.weights = weights



  def MakeDecision(self) -> List[actions.Action]:
    def GetColHeight(col: np.array)->int:
      """Returns the height of a column.
      :param row: A 1-D array
      :returns height of this column.
      """
      row_height = len(col)
      for i in range(len(col)):
        if col[i] != 0:
          row_height = i
          break
      return len(col) - row_height

    def GetHoles(game: game_client.GameClient) -> int:
      total_cnt = 0
      for c in range(game.map.shape[1]):
        has_block = False
        for r in range(game.map.shape[0]):
          if game.map[r,c] != 0:
            has_block = True

          if game.map[r,c] == 0 and has_block:
            total_cnt += 1
      return total_cnt

    def FindBestMove(ori_game):
      all_possible_solutions = agent.GetPossiblePositionsQuickVersion(
        state.current_piece, ori_game)

      best_move = ()
      best_move_score = -np.inf

      for move in all_possible_solutions:
        game = ori_game.copy()

        if move[1][0].swap:
          continue

        # Puts piece
        prev_eliminated = game.accumulated_lines_eliminated
        game.PutPiece(move[0])

        # holes
        holes = GetHoles(game)

        # Height of each col
        col_heights = [GetColHeight(game.map[:, i]) for i in range(state.width)]

        # aggregate_height
        aggregate_height = np.sum(col_heights)

        # complete lines
        complete_lines = game.accumulated_lines_eliminated - prev_eliminated


        # Bumpiness
        bumpiness = 0
        for i in range(game.width-1):
          bumpiness += np.abs(col_heights[i] - col_heights[i+1])

        score = np.dot(self.weights,
                       [aggregate_height, complete_lines, holes, bumpiness])


        if score >= best_move_score:
          best_move = move
          best_move_score = score
      return (best_move_score, best_move)

    state = self.env.get_state()
    ori_game = game_client.CreateGameFromState(state)
    (best_move_score, best_move) = FindBestMove(ori_game)
    print("line eliminated:", ori_game.accumulated_lines_eliminated)
    return best_move[1]
