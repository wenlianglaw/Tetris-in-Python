# This file runs the perforamnce of the different verison of GetPossibleSolutions... function.
import cProfile
import pstats

from agents import agent
from benchmark import utils
import shape


def RunFunc(func, games):
  t = shape.T(start_x=0, start_y=0)
  for game in games:
    func(t, game)

def RunBenchmark():
  games = utils.GenRandomGames(10, 25, 6)
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


if __name__ == "__main__":
  RunBenchmark()
