
from src.game.game         import Game
from src.utils.asyncobject import AsyncObject

#

class Component (AsyncObject):


  async def __init__ (self, game : Game):
  #
    self.game = game
    self.slot = None
    self.name = None
  #


  async def Setup (self):
  #
    pass
  #


  async def Handle (self, data : any, form : str):
  #
    pass
  #


  async def Teardown (self):
  #
    pass
  #