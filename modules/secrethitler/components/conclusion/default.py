
from defs                         import *
from src.game.game                import Game
from src.game.component.component import Component

#

class SecrethitlerComponentConclusionDefault (Component):


  async def __init__ (self, game):
  #
    await super().__init__(game)
  #


  async def Setup (self):
  #
    self.game.isRunning = False

    winCon = self.game.properties["wincon"]

    embed = {}
    if winCon == "win-liberal":
    #
      embed = \
      {
        "author": "SDMBot",
        "description": "The 5th liberal policy was played.\n**Liberals win the game.**",
        "title": self.game.name,
        "colour": self.game.properties["colours.liberal"],
        "fields":
        [
          { "name": "Liberals {SEP}".format(SEP = SEP), "value": ", ".join([seat["player"].mention for seat in self.game.properties["seats"] if seat["role"] == "liberal"])},
          { "name": "Fascists {SEP}".format(SEP = SEP), "value": ", ".join([seat["player"].mention for seat in self.game.properties["seats"] if seat["role"] == "fascist"])},
          { "name": "Hitler {SEP}".format(SEP = SEP),   "value": ", ".join([seat["player"].mention for seat in self.game.properties["seats"] if seat["role"] == "hitler"])}
        ],
        "image":
        {
          "name": "liberal-win.png",
          "source": "win-liberal.png"
        }
      }
    #
    elif winCon == "shot-hitler":
    #
      embed = \
      {
        "author": "SDMBot",
        "description": "Hitler was executed.\n**Liberals win the game.**",
        "title": self.game.name,
        "colour": self.game.properties["colours.liberal"],
        "fields":
        [
          { "name": "Liberals {SEP}".format(SEP = SEP), "value": ", ".join([seat["player"].mention for seat in self.game.properties["seats"] if seat["role"] == "liberal"])},
          { "name": "Fascists {SEP}".format(SEP = SEP), "value": ", ".join([seat["player"].mention for seat in self.game.properties["seats"] if seat["role"] == "fascist"])},
          { "name": "Hitler {SEP}".format(SEP = SEP),   "value": ", ".join([seat["player"].mention for seat in self.game.properties["seats"] if seat["role"] == "hitler"])}
        ],
        "image":
        {
          "name": "liberal-win.png",
          "source": "win-liberal.png"
        }
      }
    #
    elif winCon == "win-fascist":
    #
      embed = \
      {
        "author": "SDMBot",
        "description": "The 6th fascist policy was played.\n**Fascists win the game.**",
        "title": self.game.name,
        "colour": self.game.properties["colours.fascist"],
        "fields":
        [
          { "name": "Liberals {SEP}".format(SEP = SEP), "value": ", ".join([seat["player"].mention for seat in self.game.properties["seats"] if seat["role"] == "liberal"])},
          { "name": "Fascists {SEP}".format(SEP = SEP), "value": ", ".join([seat["player"].mention for seat in self.game.properties["seats"] if seat["role"] == "fascist"])},
          { "name": "Hitler {SEP}".format(SEP = SEP),   "value": ", ".join([seat["player"].mention for seat in self.game.properties["seats"] if seat["role"] == "hitler"])}
        ],
        "image":
        {
          "name": "fascist-win.png",
          "source": "win-fascist.png"
        }
      }
    #
    elif winCon == "elected-hitler":
    #
      embed = \
      {
        "author": "SDMBot",
        "description": "Hitler was elected as chancellor.\n**Fascists win the game.**",
        "title": self.game.name,
        "colour": self.game.properties["colours.fascist"],
        "fields":
        [
          { "name": "Liberals {SEP}".format(SEP = SEP), "value": ", ".join([seat["player"].mention for seat in self.game.properties["seats"] if seat["role"] == "liberal"])},
          { "name": "Fascists {SEP}".format(SEP = SEP), "value": ", ".join([seat["player"].mention for seat in self.game.properties["seats"] if seat["role"] == "fascist"])},
          { "name": "Hitler {SEP}".format(SEP = SEP),   "value": ", ".join([seat["player"].mention for seat in self.game.properties["seats"] if seat["role"] == "hitler"])}
        ],
        "image":
        {
          "name": "fascist-win.png",
          "source": "win-fascist.png"
        }
      }
    #

    await self.game.botHandle.messager.SendEmbed(
      self.game.channels['main'],
      embed,
      delete_after = None
    )
  #