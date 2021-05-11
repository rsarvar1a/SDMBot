
from src.game.game                import Game
from src.game.component.component import Component

#

class SecrethitlerComponentPostpolicyDefault (Component):


  async def __init__ (self, game : Game):
  #
    await super().__init__(game)
  #


  async def Setup (self):
  #
    policy = self.game.properties["last-policy-played"]

    if policy is not None:
    #
      index  = self.game.properties["policies-index"][policy]
      
      compsToLoad = self.game.properties["real-boards"][index]

      for (slot, comp) in compsToLoad.items():
      #
        if self.game.activeComponents[slot].name != comp:
        #
          await self.game.activeComponents[slot].TearDown()
          self.game.activeComponents[slot] = await self.game.botHandle.componentfactory.Create(self.game, slot, comp)
        #
      #
    #

    await self.game.UpdateTo("power")
  #