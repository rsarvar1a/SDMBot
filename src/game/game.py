
from dotty_dict import dotty
from threading import RLock
import discord

#

from src.utils.asyncobject import AsyncObject
from defs import *

#

class Game (AsyncObject):

  commands = \
  {
    "join":
    {
      "usage": "join",
      "description": "Joins the game.",
      "requires":
      [
        { "name": SEP, "value": "*The game is public.*" },
        { "name": SEP, "value": "*You are a bot moderator.*" }
      ]
    },

    "leave":
    {
      "usage": "leave",
      "description": "Leaves the game."
    },

    "invite":
    {
      "usage": "invite/add <@player>",
      "description": "Adds the specified user to the game.",
      "requires":
      [
        { "name": SEP, "value": "*You are a bot moderator.*" },
        { "name": SEP, "value": "*You are the owner of the game.*" }
      ]
    },

    "remove":
    {
      "usage": "remove/kick <@player>",
      "description": "Removes the specified user from the game.",
      "requires":
      [
        { "name": SEP, "value": "*You are a bot moderator.*" },
        { "name": SEP, "value": "*You are the owner of the game.*" }
      ]
    },
    
    "edit":
    {
      "usage": "edit <key> <value>",
      "description": "Changes a game setting to the specified value. Contact a developer for in-depth information.",
      "requires":
      [
        { "name": SEP, "value": "*You are a bot moderator.*" },
        { "name": SEP, "value": "*You are the owner of the game.*" }
      ]
    },  

    "delete":
    {
      "usage": "delete/del",
      "description": "Deletes the game.",
      "requires":
      [
        { "name": SEP, "value": "*You are a bot moderator.*" },
        { "name": SEP, "value": "*You are the owner of the game.*" }
      ]
    },

    "status":
    {
      "usage": "status/lobby",
      "description": "Views info about this game."
    }, 
  }


  read_only = discord.PermissionOverwrite(
    read_messages = True, 
    send_messages = False,
    add_reactions = False
  )


  read_write = discord.PermissionOverwrite(
    read_messages = True,
    send_messages = True,
    add_reactions = False
  ) 


  async def __init__ (self, bot, context : discord.Message, gameName : str, sizes : list):
  #
    self.botHandle = bot
    self.playerIDs = [context.author.id]
    self.owner     = context.author

    self.mutex     = RLock()

    self.name      = "Game '" + gameName + "'" if gameName is not None else "New Game"
    self.category  = await context.channel.guild.create_category(name = self.name)

    self.channels  = \
    {
      'lobby': await context.channel.category.create_text_channel(
        name = "lobby",
        overwrites = \
        {
          context.guild.default_role: Game.read_write, 
          context.author: Game.read_write
        }
      ),
      'board': await context.channel.category.create_text_channel(
        name = "board-state",
        overwrites = \
        {
          context.guild.default_role: Game.read_only
        }
      )
    }

    self.botHandle.activeGames.update({ self.category.id: self })
    self.botHandle.activePlayers.update({ context.author.id: self })

    self.isRunning = False

    self.properties = dotty(
      {
        "private": False,
        "uuid": self.category.id,
        "sizes":
        {
          "sizes": sizes,
          "absolute-max": 10
        }
      }
    )

    self.Prepare()
  #


  async def GameRunning (self, player, channel):
  #
    await self.botHandle.messager.SendEmbed(
      channel, 
      {
        "author": "SDMBot",
        "description": "{ERROR} {mention}, this game is already running!" \
          .format(ERROR = EMOTES["ERR"], mention = player.mention),
        "title": self.name,
        "colour": COLOURS["WARNING"]
      }, 
      delete_after = None
    )
  #


  async def NoPermission (self, player, channel):
  #
    await self.botHandle.messager.SendEmbed(
      channel,
      {
        "author": "SDMBot",
        "description": "{ERROR} {mention}, you need to be the game owner or a bot admin." \
          .format(ERROR = EMOTES["ERR"], mention = player.mention),
        "title": self.name,
        "colour": COLOURS["WARNING"]
      },
      delete_after = None
    )
  #


  async def Usage (self, channel : discord.ChannelType, usage : dict):
  #
    data = \
    {
      "author": "SDMBot",
      "title": "*Usage* {SEP} `".format(SEP = SEP) + self.botHandle.globalConfigs["prefix"] + " " + usage.get("usage") + "`",
      "description": usage.get("description") + ("\n\n**Requires at least one of the following:**" if usage.get("requires") is not None else ""),
      "colour": COLOURS["INFO"],
      "fields": ";\n".join(usage.get("requires")).rstrip(';') + "." if usage.get("requires") is not None else None
    }

    await self.botHandle.messager.SendEmbed(channel, data, delete_after = None)
  #


  async def Join (self, context):
  #
    player = context.author 

    if self.isRunning:
    #
      await self.GameRunning(player, context.channel)
      return
    #

    if self.properties["private"]:
    #
      await self.botHandle.messager.SendEmbed(
        context.channel,
        {
          "author": "SDMBot",
          "description": "{WARNING} {mention}, this game is invite-only.\nAsk {owner}, the game owner, to be added." \
            .format(WARNING = EMOTES["WARNING"], mention = player.mention, owner = self.owner.mention),
          "title": self.name,
          "colour": COLOURS["WARNING"]
        },
        delete_after = None
      )
      return
    #

    if player.id in self.botHandle.activePlayers.keys():
    #
      if self.botHandle.activePlayers[player.id].gameCategory.id == self.category.id:
      #
        await self.botHandle.messager.SendEmbed(
          context.channel, 
          {
            "author": "SDMBot",
            "description": "{INFO} {mention}, you are already in this game." \
              .format(INFO = EMOTES["INFO"], mention = player.mention),
            "title": self.name,
            "colour": COLOURS["INFO"]
          },
          delete_after = None
        )
        return
      #
      else:
      #
        await self.botHandle.messager.SendEmbed(
          context.channel, 
          {
            "author": "SDMBot",
            "description": "{ERR} {mention}, you are already in another game!" \
              .format(ERR = EMOTES["ERR"], mention = player.mention),
            "title": self.name,
            "colour": COLOURS["ERR"]
          },
          delete_after = None
        )
        return
      #
    #
    else:
    #
      await self.botHandle.messager.SendEmbed(
        context.channel,
        {
          "author": "SDMBot",
          "description": "{SUCCESS} {mention}, you joined '{gameName}'." \
            .format(SUCCESS = EMOTES['SUCCESS'], mention = player.mention, gameName = self.name),
          "title": self.name,
          "colour": COLOURS['SUCCESS']
        },
        delete_after = None
      )

      self.playerIDs.append[player.id]
      self.botHandle.activePlayers.update({ player.id: self })
      
      if len(self.playerIDs) in self.properties["sizes.sizes"]:
      #
        self.Start()
      #
    #
  #


  async def Leave (self, context):
  #
    player = context.author

    if self.isRunning:
    #
      await self.GameRunning(player, context.channel)
      return
    #

    if player.id not in self.playerIDs:
    #
      await self.botHandle.messager.SendEmbed(
        context.channel,
        {
          "author": "SDMBot",
          "description": "{ERROR} {mention}, you are not in this game!" \
            .format(ERROR = EMOTES["ERR"], mention = player.mention),
          "title": self.name,
          "colour": COLOURS["ERR"]
        },
        delete_after = None
      )
      return
    #

    if self.properties["private"]:
    #
      await self.botHandle.messager.SendEmbed(
        context.channel,
        {
          "author": "SDMBot",
          "description": "{WARNING} {mention}, you will need to be re-invited if you wish to rejoin." \
            .format(WARNING = EMOTES["WARNING"], mention = player.mention, owner = self.owner.mention),
          "title": self.name,
          "colour": COLOURS["WARNING"]
        },
        delete_after = None
      )
    #
    await self.botHandle.messager.SendEmbed(
      context.channel,
      {
        "author": "SDMBot",
        "description": "{SUCCESS} {mention}, you left '{gameName}'." \
          .format(SUCCESS = EMOTES["SUCCESS"], mention = player.mention, gameName = self.name),
        "title": self.name,
        "colour": COLOURS["SUCCESS"]
      },
      delete_after = None
    )

    self.playerIDs.remove(player.id)
    self.botHandle.activePlayers.pop(player.id)

    if len(self.playerIDs) in self.properties["sizes.sizes"]:
    #
      self.Start()
    #
  #


  async def Add (self, context, member):
  #
    player = context.author

    if self.isRunning:
    #
      await self.GameRunning(player, context.channel)
      return
    #

    if player.id != self.owner.id and player.id not in self.botHandle.globalConfigs["moderators"]:
    #
      await self.NoPermission(player, context.channel)
      return
    #

    soughtPlayer = None
    try:
    #
      soughtPlayer = await context.guild.fetch_member(member)
    #
    except (discord.Forbidden, discord.HTTPException) as e:
    #
      soughtPlayer = None
    #

    if soughtPlayer is None:
    #
      await self.botHandle.messager.SendEmbed(
        context.channel,
        {
          "author": "SDMBot",
          "description": "{ERROR} <@{pid}> is not a valid server member!" \
            .format(ERROR = EMOTES["ERR"], pid = member),
          "title": self.name,
          "colour": COLOURS["ERR"]
        },
        delete_after = None
      )
    #
    elif soughtPlayer.id in self.playerIDs:
    #
      await self.botHandle.messager.SendEmbed(
        context.channel,
        {
          "author": "SDMBot",
          "description": "{INFO} {target} is already in this game!" \
            .format(INFO = EMOTES["INFO"], target = soughtPlayer.mention),
          "title": self.name,
          "colour": COLOURS["INFO"]
        },
        delete_after = None
      )
    #
    elif soughtPlayer.id in self.botHandle.activePlayers.keys():
    #
      await self.botHandle.messager.SendEmbed(
        context.channel,
        {
          "author": "SDMBot",
          "description": "{ERROR} {target} is already in another game!" \
            .format(ERROR = EMOTES["ERR"], target = soughtPlayer.mention),
          "title": self.name,
          "colour": COLOURS["ERROR"]
        },
        delete_after = None
      )
    #
    elif len(self.playerIDs) > self.properties["sizes.absolute-max"]:
    #
      await self.botHandle.messager.SendEmbed(
        context.channel,
        {
          "author": "SDMBot",
          "description": "{ERROR} This game is full!\nThe absolute maximum number of players is {n}." \
            .format(ERROR = EMOTES["ERR"], n = self.properties["sizes.absolute-max"]),
          "title": self.name,
          "colour": COLOURS["ERROR"]
        },
        delete_after = None
      )
    #
    else:
    #
      await self.botHandle.messager.SendEmbed(
        context.channel,
        {
          "author": "SDMBot",
          "description": "{SUCCESS} {target} joined the game!" \
            .format(SUCCESS = EMOTES["SUCCESS"], target = soughtPlayer.mention),
          "title": self.name,
          "colour": COLOURS["SUCCESS"]
        },
        delete_after = None
      )

      self.botHandle.activePlayers.update({ soughtPlayer.id, self })
      self.playerIDs.append(soughtPlayer.id)

      if len(self.playerIDs) in self.properties["sizes.sizes"]:
      #
        self.Start()
      #
    #
  #


  async def Remove (self, context, member):
  #
    player = context.author

    if self.isRunning:
    #
      await self.GameRunning(player, context.channel)
      return
    #

    if player.id != self.owner.id and player.id not in self.botHandle.globalConfigs["moderators"]:
    #
      await self.NoPermission(player, context.channel)
      return
    #

    # TODO
  #


  async def Edit (self, context, key, value):
  #
    player = context.author

    if self.isRunning:
    #
      await self.GameRunning(player, context.channel)
      return
    #

    if player.id != self.owner.id and player.id not in self.botHandle.globalConfigs["moderators"]:
    #
      await self.NoPermission(player, context.channel)
      return
    #

    if len(self.playerIDs) in self.properties["sizes.sizes"]:
    #
      self.Start()
    #
  #


  async def Delete (self, context):
  #
    player = context.author

    if self.isRunning and player.id not in self.botHandle.globalConfigs["moderators"]:
    #
      await self.GameRunning(player, context.channel)
      return
    #
    elif not self.isRunning and player.id != self.owner.id and player.id not in self.botHandle.globalConfigs["moderators"]:
    #
      await self.NoPermission(player, context.channel)
      return
    #

    await self.botHandle.messager.SendEmbed(
      context.channel,
      {
        "author": "SDMBot",
        "description": "{WARNING} Deleting game!" \
          .format(WARNING = EMOTES["WARNING"]),
        "title": self.name,
        "colour": COLOURS["WARNING"]
      },
      delete_after = None
    )

    await self.Cleanup()
  #


  async def Status (self, context):
  #
    pass
  #


  async def HandleCommand (self, context, command, args):
  #
    self.mutex.acquire(blocking=True)
    #
    if    command in ["join", "j"]:
    #
      if len(args) != 0: await self.botHandle.Usage(context.channel, Game.commands["join"])
      else: await self.Join(context)
    #
    elif  command in ["leave", "l"]:
    #
      if len(args) != 0: await self.botHandle.Usage(context.channel, Game.commands["leave"])
      else: await self.Leave(context)
    #
    elif  command in ["delete", "del"]:
    #
      if len(args) != 0: await self.botHandle.Usage(context.channel, Game.commands["delete"])
      else: await self.Delete(context)
    #
    elif  command in ["status", "lobby"]:
    #
      if len(args) != 0: await self.botHandle.Usage(context.channel, Game.commands["status"])
      await self.Status(context)
    #
    elif  command in ["add", "invite"]:    
    #
      if len(args) != 1: await self.botHandle.Usage(context.channel, Game.commands["invite"])
      else: await self.Add(context, args[0])
    #
    elif  command in ["remove", "kick"]:
    #
      if len(args) != 1: await self.botHandle.Usage(context.channel, Game.commands["remove"])
      else: await self.Remove(context, args[0])
    #
    elif  command in ["edit"]:
    #
      if len(args) != 2: await self.botHandle.Usage(context.channel, Game.commands["edit"])
      else: await self.Edit(context, args[0], args[1])
    #
    context.delete()
    #
    self.mutex.release()
  #


  async def HandleEvent (self, data, type):
  #
    pass
  #


  async def Start (self):
  #
    pass
  #


  async def Cleanup (self):
  #
    id      = self.category.id
    players = self.playerIDs
    
    self.botHandle.activeGames.pop(id)
    for pid in players:
      self.botHandle.activePlayers.pop(pid)

    for ch in self.channels:
      await ch.delete()
    
    await self.category.delete()
  #