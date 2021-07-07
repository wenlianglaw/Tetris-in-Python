from agents import agent

from typing import List

import actions


class QuadAgent(agent.Agent):
  def __init__(self, env: agent.Ent):
    super().__init__(env)

  def MakeDecision(self) -> List[actions.Action]:
    pass

