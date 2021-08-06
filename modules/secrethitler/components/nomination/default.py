
from src.game.component.component import Component

#

class SecrethitlerComponentNominationDefault (Component):


  async def __init__ (self, game):
  #
    await super().__init__(game)
  #


  async def Setup (self):
  #
    pres = self.NextPresident()
  #


  async def Handle (self):
  #
    pass
  #


  async def Teardown (self):
  #
    pass
  #


  def NextPresident (self, current):
  #
    pass
  #