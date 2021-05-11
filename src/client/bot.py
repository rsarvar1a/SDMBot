
import os
import re
import json
import discord
from dotty_dict import dotty

#

from defs                       import *
from src.utils.logging          import Logger
from src.utils.io               import MessageHandler
from src.game.game              import Game
from src.game.factory           import GameFactory
from src.game.component.factory import ComponentFactory


#
#   Main bot class, controls everything.
#

class TournamentBot (object):


  globals = \
  {
    "new":
    {
      "usage": "new/game/create <variant> [ <size1>,<size2>,... ] [ name ]",
      "description": "Creates a new game of the given variant, sizes (default 7), and name.",
    },
    "global":
    {
      "usage": "config/global <key> <get|set|add|remove> <value>",
      "description": "Sets a global bot configuration key to the specified value and persists.",
      "requires":
      [
        {
          "name": SEP,
          "value": "*You are a bot administrator.*"
        }
      ]
    },
    "help":
    {
      "usage": "help/info/?",
      "description": "Shows bot information and a help menu."
    }
  }


  forbiddenKeys = \
  [
    "token",
    "admins"
  ]


  def __init__ (self):
  #
    f = open(CONFIG_MAIN) if os.stat(CONFIG_FILE).st_size == 0 else open(CONFIG_FILE)
    self.globalConfigs = dotty(dictionary = json.load(f))

    self.discordClient = discord.Client()
    self.logger        = Logger(self)
    self.messager      = MessageHandler(self.globalConfigs, self)

    self.gamefactory      = GameFactory(self)
    self.componentfactory = ComponentFactory(self)
    self.activeGames      = {}
    self.activePlayers    = {}
  #


  async def Usage (self, channel : discord.ChannelType, usage : dict):
  #
    data = \
    {
      "author": "SDMBot",
      "title": "*Usage*  {SEP}  ` ".format(SEP = SEP) + self.globalConfigs["prefix"] + " " + usage.get("usage") + " `",
      "description": usage.get("description") + ("\n\n**Requires at least one of the following conditions:**" if usage.get("requires") is not None else ""),
      "colour": COLOURS["INFO"],
      "fields": usage.get("requires") if usage.get("requires") is not None else None
    }

    await self.messager.SendEmbed(channel, data, delete_after = None)
  #


  def Specialize (self, val : str):
  #
    if   val == "None":   return None
    elif val == "True":   return True
    elif val == "False":  return False
    elif val == "{}":     return {}
    elif val == "[]":     return []
    else:                 return val
  #


  async def NewGame (self, context : discord.Message, args : list):
  #
    player = context.author
    if self.activePlayers.get(player.id) is not None:
    #
      await self.messager.SendEmbed(
        context.channel,
        {
          "author": "SDMBot",
          "description": "{ERR} You are in a different game!" \
            .format(ERR = EMOTES["ERR"]),
          "title": "Game Creator",
          "colour": COLOURS["ERR"]
        },
        delete_after = None
      )
      return
    #

    if args is None or len(args) == 0:     await self.gamefactory.List(context)
    elif len(args) == 1:                   await self.gamefactory.Create(context, args[0])
    elif len(args) == 2:                   await self.gamefactory.Create(context, args[0], args[1])
    elif len(args) >= 3:                   await self.gamefactory.Create(context, args[0], args[1], " ".join(args[2:]))
  #


  async def Help (self, context : discord.Message):
  #
    pass
  #


  async def Configure (self, context : discord.Message, args : list):
  #
    if context.author.id not in self.globalConfigs["admins"]:
    #
      await self.messager.SendEmbed(
        context.channel,
        {
          "author": "SDMBot",
          "description": "{ERROR} {mention}, you need to be a bot admin to do this." \
            .format(ERROR = EMOTES["ERR"], mention = context.author.mention),
          "title": "Global Configuration",
          "colour": COLOURS["ERR"]
        },
        delete_after = None
      )
      return
    #

    # Forbidden keys.
    if args is None or len(args) == 0 or type(args[1]) is int: await self.Usage(context.channel, TournamentBot.globals["global"])
    elif args[0] in TournamentBot.forbiddenKeys:
    #
      await self.messager.SendEmbed(
        context.channel,
        {
          "author": "SDMBot",
          "description": "{ERROR} {mention}, that key is not accessible on Discord for security reasons." \
            .format(ERROR = EMOTES["ERR"], mention = context.author.mention),
          "title": "Global Configuration",
          "colour": COLOURS["ERR"]
        },
        delete_after = None
      )
      return
    #
    elif len(args) == 2 and args[1].lower() == "get":
    #

      data = self.globalConfigs.get(args[0])
      if data is None:
      #
        await self.messager.SendEmbed(
          context.channel,
          {
            "author": "SDMBot",
            "description": "{ERR} Key `{key}` was not found!" \
              .format(ERR = EMOTES["ERR"], key = args[0]),
            "title": "Global Configuration",
            "colour": COLOURS["ERR"]
          },
          delete_after = None
        )
      #
      else:
      #
        await self.messager.SendEmbed(
          context.channel,
          {
            "author": "SDMBot",
            "description": "{SUCCESS} Key `{key}` has value `{val}`." \
              .format(SUCCESS = EMOTES["SUCCESS"], key = args[0], val = data),
            "title": "Global Configuration",
            "colour": COLOURS["SUCCESS"]
          },
          delete_after = None
        )
      #
    #
    elif len(args) != 3: await self.Usage(context.channel, TournamentBot.globals["global"])
    elif args[1].lower() not in ["set", "add", "remove"]: await self.Usage(context.channel, TournamentBot.globals["global"])
    else:
    #
      k = args[0]
      a = args[1].lower()
      v = args[2]

      v = self.Specialize(v)

      if a == "set":
      #
        self.globalConfigs[k] = v

        await self.messager.SendEmbed(
          context.channel,
          {
            "author": "SDMBot",
            "description": "{SUCCESS} Set key `{key}` to value `{val}`." \
              .format(SUCCESS = EMOTES["SUCCESS"], key = k, val = v),
            "title": "Global Configuration",
            "colour": COLOURS["SUCCESS"]
          },
          delete_after = None
        )
      #
      elif a == "add":
      #
        if self.globalConfigs.get(k) is None:
        #
          self.globalConfigs[k] = []
        #

        if type(self.globalConfigs[k]) is not list:
        #
          await self.messager.SendEmbed(
            context.channel,
            {
              "author": "SDMBot",
              "description": "{ERROR} Value at key `{key}` exists and is not a list!\nRun `{prefix} global {key} set []` first." \
                .format(ERR = EMOTES["ERR"], key = k, prefix = self.globalConfigs["prefix"]),
              "title": "Global Configuration",
              "colour": COLOURS["ERR"]
            },
            delete_after = None
          )
        #
        else:
        #
          self.globalConfigs[k].append(v)
          lis = self.globalConfigs[k]

          await self.messager.SendEmbed(
            context.channel,
            {
              "author": "SDMBot",
              "description": "{SUCCESS} Appended value `{value}` to list at key `{key}`\n(The list is `{l}`)." \
                .format(SUCCESS = EMOTES["SUCCESS"], key = k, value = v, l = lis),
              "title": "Global Configuration",
              "colour": COLOURS["SUCCESS"]
            },
            delete_after = None
          )
        #
      #
      elif a == "remove":
      #
        if self.globalConfigs.get(k) is None or type(self.globalConfigs[k]) is not list:
        #
          await self.messager.SendEmbed(
            context.channel,
            {
              "author": "SDMBot",
              "description": "{ERROR} There is no list at key `{key}`!" \
                .format(ERR = EMOTES["ERR"], key = k),
              "title": "Global Configuration",
              "colour": COLOURS["ERR"]
            },
            delete_after = None
          )
        #
        else:
        #
          lis = self.globalConfigs[k]
          
          if v not in lis:
          #
            await self.messager.SendEmbed(
              context.channel,
              {
                "author": "SDMBot",
                "description": "{INFO} Value `{value}` was not in the list at key `{key}`!\n(The list is `{l}`)." \
                  .format(INFO = EMOTES["INFO"], key = k, val = v, l = lis),
                "title": "Global Configuration",
                "colour": COLOURS["INFO"]
              },
              delete_after = None
            )
          #
          else:
          #
            self.globalConfigs[k].remove(v)

            await self.messager.SendEmbed(
              context.channel,
              {
                "author": "SDMBot",
                "description": "{SUCCESS} Removed value `{value}` from the list at key `{key}` (new list is `{l}`)." \
                  .format(SUCCESS = EMOTES["SUCCESS"], key = k, val = v, l = self.globalConfigs[k]),
                "title": "Global Configuration",
                "colour": COLOURS["SUCCESS"]
              },
              delete_after = None
            )
          #
        #
      #

      config = open(CONFIG_FILE, "w")
      config.write(self.globalConfigs.to_json())
      self.logger.info("Wrote to config.json.", __file__)

      if self.globalConfigs is None:
      #
        self.globalConfigs = dotty(json.load(open(CONFIG_MAIN)))
        self.logger.warning("Reloaded from master! Writing to main.", __file__)
        config.write(self.globalConfigs.to_json())
      #
    #
  #


  async def HandleCommand(self, context : discord.Message, command : str, args : list):
  #
    if command in ["new", "game", "create"]:
    #
      await self.NewGame(context, args)
      return True
    #
    elif command in ["global", "config"]:
    #
      await self.Configure(context, args)
      return True
    #
    elif command in ["help", "info", "?", None]:
    #
      await self.Help(context)
      return True
    #
    else: 
    #
      return False
    #
  #
#