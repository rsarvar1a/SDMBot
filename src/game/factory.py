
import re
import discord

#

from defs          import *
from src.game.game import Game

#

class GameFactory (object):


  def __init__ (self, bot):
  #
    self.botHandle = bot
    self.variants  = {}
  #


  async def Create (self, context : discord.Message, variant : str, sizes : str = "7", name = None):
  #
    if variant not in self.variants.keys():
    #
      await self.botHandle.messager.SendEmbed(
        context.channel,
        {
          "author": "SDMBot",
          "description": "{ERR} Unknown variant `{variant}`!" \
            .format(ERR = EMOTES["ERR"], variant = variant),
          "title": "Game Creator",
          "colour": COLOURS["ERR"],
        },
        delete_after = None
      )
      return
    #

    if re.match(r'([0-9]+)(,[0-9]+)*', sizes) is None:
    #
      await self.botHandle.messager.SendEmbed(
        context.channel,
        {
          "author": "SDMBot",
          "description": "{ERR} Invalid size list '{sizes}'!" \
            .format(ERR = EMOTES["ERR"], sizes = sizes),
          "title": "Game Creator",
          "colour": COLOURS["ERR"],
        },
        delete_after = None
      )
      return
    #

    sizes_list = list(map(lambda s: int(s), sizes.split(',')))

    ref = await Game(self.botHandle, context, name, sizes_list, self.variants[variant])

    await self.botHandle.messager.SendEmbed(
      ref.channels['lobby'],
      {
        "author": "SDMBot",
        "description": "{SUCCESS} Welcome to the game!\nType `{prefix} help` for more info." \
          .format(SUCCESS = EMOTES["SUCCESS"], prefix = self.botHandle.globalConfigs["prefix"]),
        "title": "Game Creator",
        "colour": COLOURS["SUCCESS"],
      },
      delete_after = None
    )

    self.botHandle.logger.info("Successfully created game '{name}' (id {uuid})." \
        .format(name = ref.name, uuid = ref.properties["uuid"]), 
      __file__)
  #


  async def List (self, context : discord.Message):
  #
    fields = []
    for key in self.variants.keys():
      variant = self.variants[key]
      fields.append({ "name": "**" + key + "**", "value" : "*" + variant["description"] + "*" })
    
    await self.botHandle.messager.SendEmbed(
      context.channel,
      {
        "author": "SDMBot",
        "description": "Available variants:\n",
        "title": "Game Creator",
        "colour": COLOURS["INFO"],
        "fields": fields
      },
      delete_after = None
    )
  #