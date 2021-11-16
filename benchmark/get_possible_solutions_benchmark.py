# This file runs the perforamnce of the different verison of GetPossibleSolutions... function.
# With bit map GetAllPossibleSolutions is ~0.29
# With color_map this function is ~0.45
import cProfile
import pstats

from agents import agent
from benchmark import utils


def RunFunc(func, games):
  avg_sol = 0
  for game in games:
    sol = func(game.current_piece, game)
    avg_sol += len(sol)
  avg_sol /= len(games)
  print(func, " ", avg_sol)

def RunBenchmark():
  games = utils.GenRandomGames(50, 25, 6)
  profile_quick_version = cProfile.Profile()
  profile_quick_version.runcall(RunFunc,
                                func=agent.GetPossiblePositionsQuickVersion,
                                games=games)

  profile_normal_version = cProfile.Profile()
  profile_normal_version.runcall(RunFunc,
                                 func=agent.GetAllPossiblePositions,
                                 games=games)

  profile_quick_version_dfs = cProfile.Profile()
  profile_quick_version_dfs.runcall(RunFunc,
                                    func=agent.GetPossiblePositionsQuickVersion2,
                                    games=games)

  stats_quick = pstats.Stats(profile_quick_version)
  stats_quick_dfs = pstats.Stats(profile_quick_version_dfs)
  stats_normal = pstats.Stats(profile_normal_version)

  stats_quick.sort_stats("tottime").print_stats(0.2)
  stats_quick_dfs.sort_stats("tottime").print_stats(0.2)
  stats_normal.sort_stats("tottime").print_stats(0.2)

  print("quick tt", stats_quick.total_tt)
  print("quick dfs tt", stats_quick.total_tt)
  print("normal tt", stats_normal.total_tt)
  print("quick %f%%" % (100 * stats_quick.total_tt / stats_normal.total_tt))
  print("quick dfs %f%%" % (100 * stats_quick_dfs.total_tt / stats_normal.total_tt))

if __name__ == "__main__":
  RunBenchmark()
