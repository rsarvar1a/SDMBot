
import json
import re
import discord
from dotty_dict import dotty

#

from defs          import *
from src.game.game import Game

#

class GameFactory (object):


  def __init__ (self, bot):
  #
    self.botHandle  = bot

    self.archetypes = {}
    self.variants   = {}

    for module in os.listdir(MODULES_PATH):
    #
      modPath = os.path.join(MODULES_PATH, module)

      archetype = dotty(json.load(open(os.path.join(modPath, "archetype.json"))))
      self.archetypes[module] = archetype

      variantsPath = os.path.join(modPath, "variants")
      for config in os.listdir(variantsPath):
      #
        variant = dotty(json.load(open(os.path.join(variantsPath, config))))
        self.variants[variant["name"]] = variant  
      #
    #
  #


  async def Create (self, context : discord.Message, variant : str, sizes : str = None, name = None):
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

    if sizes == None:
    #
      sizes = self.variants[variant]["sizes.default"]
    #
    elif re.match(r'([0-9]+)(,[0-9]+)*', sizes) is None:
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

    if type(sizes) is not list: sizes_list = list(map(lambda s: int(s), sizes.split(',')))
    else: sizes_list = sizes

    for size in sizes_list:
    #
      if size not in self.variants[variant]["sizes.legal"]:
      #
        await self.botHandle.messager.SendEmbed(
          context.channel,
          {
            "author": "SDMBot",
            "description": "{ERR} This game can't be played with the size '{s}'." \
              .format(ERR = EMOTES["ERR"], s = size),
            "title": self.name,
            "colour": COLOURS["ERR"]
          },
          delete_after = None
        )
        return
      #
    #

    if name is None:
    #
      name = 'New Game'
    #

    self.botHandle.logger.debug("Using:\n{config}".format(config = self.variants[variant]), __file__)
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


  async def ViaRemake (self, context : discord.Message, prev : Game):
  #
    pass
  #