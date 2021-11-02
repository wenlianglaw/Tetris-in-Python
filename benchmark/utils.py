import game_client
import random

def _GenOneRandomGame(random_blocks, last_n_lines):
  game = game_client.GameClient(width=10, height=20)

  # Fills some random spots in the last 4 lines
  for i in range(random_blocks):
    (x, y) = (random.randrange(game.height-last_n_lines, game.height-1), random.randrange(0, game.width))
    game.map[x, y] = 1
  return game

def GenRandomGames(n: int, random_blocks=15, last_n_lines=4):
  games = []
  for i in range(n):
    games.append(_GenOneRandomGame(random_blocks, last_n_lines))
  return games
