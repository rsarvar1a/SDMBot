
from dotty_dict import dotty

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


  def Create (self, variant : dotty, slot : str, component : str, game : Game):
  #
    pass
  #