
from src.game.component.component import Component

#

class SecrethitlerComponentPowerEmpty (Component):


  async def __init__ (self, game):
  #
    await super().__init__(game)
  #

  
  async def Setup (self):
  #
    self.game.UpdateTo("nomination")
  #
