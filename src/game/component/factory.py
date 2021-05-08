
import importlib
from os import O_SHORT_LIVED
from dotty_dict import dotty
from os.path import join

#

from defs                         import *
from src.game.game                import Game
from src.game.component.component import Component

#

class ComponentFactory (object):


  def __init__ (self, parent):
  #
    self.botHandle = parent
  #


  async def Create (self, slot : str, component : str, game : Game):
  #
    variant = game.properties

    componentPath = join(join(game.paths["components"], slot), component + ".py")
    self.botHandle.logger.debug("Loading component from {rel}.".format(os.path.relpath(componentPath), start = ROOT_PATH), __file__)
  
    if os.path.isfile(componentPath) == False:
    #
      old       = component
      component = self.botHandle.gamefactory.archetypes.get(variant["archetype"])[slot]

      await self.botHandle.messager.SendEmbed(
        game.channels['lobby'],
        {
          "author": "SDMBot",
          "description": "{WARNING} Component {s}.{c} does not exist!\nUsing {s}.{c2} instead; if you encounter issues please remake and inform an admin." \
            .format(WARNING = EMOTES["WARNING"], s = slot, c = old, c2 = component),
          "title": game.name,
          "colour": COLOURS["WARNING"]
        },
        delete_after = None
      )
    #

    compsModName = str(os.path.relpath(game.paths["components"], start = ROOT_PATH)) \
      .translate({ '/' : '.' })
    modName      = "{comps}.{s}.{c}".format(comps = compsModName, s = slot, c = component)
    self.botHandle.logger.debug("Loading module {m}.".format(m = modName), __file__)

    module    = importlib.import_module(modName)
    archetype = variant["archetype"]
    clazz     = getattr(module, "{archetype}Component{s}{c}" \
      .format(archetype = archetype, s = slot.capitalize(), c = component.capitalize()))
    
    instance  = await clazz(parent = game)
    return instance
  #