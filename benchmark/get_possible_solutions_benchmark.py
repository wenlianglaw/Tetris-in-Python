# This file runs the perforamnce of the different verison of GetPossibleSolutions... function.
import cProfile
from agents import agent
import game_client
import random
import shape
import pstats

def _GenOneRandomGame(random_blocks, last_n_lines):
  game = game_client.GameClient(width=10, height=20)

  # Fills some random spots in the last 4 lines
  for i in range(random_blocks):
    (x, y) = (random.randrange(0, last_n_lines), random.randrange(0, game.width))
    game.map[x, y] = 1
  return game

def GenRandomGames(n: int, random_blocks=15, last_n_lines=4):
  games = []
  for i in range(n):
    games.append(_GenOneRandomGame(random_blocks, last_n_lines))
  return games

def RunFunc(func, games):
  t = shape.T(start_x=0, start_y=0)
  for game in games:
    func(t, game)

games = GenRandomGames(10, 25, 6)
profile_quick_version = cProfile.Profile()
profile_quick_version.runcall(RunFunc,
                              func=agent.GetPossiblePositionsQuickVersion,
                              games=games)


profile_normal_version = cProfile.Profile()
profile_normal_version.runcall(RunFunc,
                               func=agent.GetAllPossiblePositions,
                               games=games)

stats_quick = pstats.Stats(profile_quick_version)
stats_normal = pstats.Stats(profile_normal_version)

stats_quick.sort_stats("tottime").print_stats(0.2)
stats_normal.sort_stats("tottime").print_stats(0.2)

print("quick tt", stats_quick.total_tt)
print("normal tt", stats_normal.total_tt)
print("ratio %f%%" % (100*stats_quick.total_tt / stats_normal.total_tt))
