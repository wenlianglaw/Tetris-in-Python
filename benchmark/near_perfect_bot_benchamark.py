import cProfile
import pstats

from benchmark import utils
from agents import agent
from agents import near_perfect_bot

def RunAgent(n_games=20, n_moves=50):
  games = utils.GenRandomGames(n_games, random_blocks=20, last_n_lines=6)
  for game in games:
    env = agent.Env(game=game)
    bot = near_perfect_bot.TheNearPerfectAgent(env)
    for i in range(n_moves):
      decision = bot.MakeDecision()
      env.game.ProcessActions(decision)


def RunBenchmark():
  profile = cProfile.Profile()
  profile.runcall(RunAgent)
  stats = pstats.Stats(profile)
  stats.sort_stats("tottime").print_stats(0.6)


if __name__ == "__main__":
  RunBenchmark()
