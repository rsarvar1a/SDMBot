
import re
import discord
from discord.utils import CachedSlotProperty
from dotty_dict import dotty
from threading  import RLock

#

from defs                  import *
from src.utils.asyncobject import AsyncObject

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

    "resize":
    {
      "usage": "resize/size <size1>,<size2>,...",
      "description": "Changes the size of this game.",
      "requires":
      [
        { "name": SEP, "value": "*You are a bot moderator.*" },
        { "name": SEP, "value": "*You are the owner of the game.*" }
      ]
    },

    "rename":
    {
      "usage": "rename <name>",
      "description": "Changes the name of the game.",
      "requires":
      [
        {"name": SEP, "value": "*You are a bot moderator.*" },
        {"name": SEP, "value": "*You are the owner of this game.*" }
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

    "remake":
    {
      "usage": "remake",
      "description": "Toggles your membership in the remaking queue."
    },

    "go":
    {
      "usage": "go",
      "description": "Initiates a remake of this game.",
      "requires":
      [
        { "name": SEP, "value": "*You are a bot moderator.*" },
        { "name": SEP, "value": "*You are the owner of the game.*" }
      ]
    },

    "freeze":
    {
      "usage": "freeze/pause",
      "description": "Freezes the game, preventing any player from taking actions.",
      "requires":
      [
        { "name": SEP, "value": "*You are a bot moderator.*" }
      ]
    },

    "unfreeze":
    {
      "usage": "unfreeze/resume",
      "description": "Unfreezes the game, allowing players to take actions.",
      "requires":
      [
        { "name": SEP, "value": "*You are a bot moderator.*" }
      ]
    }
  }


  forbiddenKeys = \
  [
    "uuid"
  ]


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


  private = discord.PermissionOverwrite(
    read_messages = False
  )


  base_properties = \
  {
    "private": False
  }


  async def __init__ (self, bot, context : discord.Message, gameName : str, sizes : list, properties : dict):
  #
    self.botHandle = bot
    self.playerIDs = [context.author.id]
    self.owner     = context.author

    self.mutex     = RLock()
    self.didGo     = False

    self.name      = gameName
    self.category  = await context.channel.guild.create_category(name = self.name)

    self.paths     = \
    {
      "root": os.path.join(MODULES_PATH, properties["archetype"]),
      "components": os.path.join(os.path.join(MODULES_PATH, properties["archetype"]), "components"),
      "assets": os.path.join(os.path.join(MODULES_PATH, properties["archetype"]), "assets")
    }

    self.channels  = \
    {
      'lobby': await self.category.create_text_channel(
        name = "lobby",
        overwrites = \
        {
          context.guild.default_role: Game.read_write, 
          context.author: Game.read_write
        }
      ),
      'board': await self.category.create_text_channel(
        name = "board-state",
        overwrites = \
        {
          context.guild.default_role: Game.read_only
        }
      )
    }
    self.messages = {}

    self.botHandle.activeGames.update({ self.category.id: self })
    self.botHandle.activePlayers.update({ context.author.id: self })

    self.isRunning = False
    self.isFrozen  = False

    self.properties = dotty(Game.base_properties)
    self.properties.update(properties)
    self.properties["sizes.sizes"] = sizes
    self.properties["uuid"] = self.category.id

    self.activeComponents = {}
    self.componentPointer = self.properties["entry-point"]

    default_components = self.properties["defaults"]
    for (key, comp) in default_components.items():
    #
      self.activeComponents[key] = await self.botHandle.componentfactory.Create(key, comp, self)
    #

    await self.activeComponents[self.properties["board-manager"]].Setup()
    await self.Preview()
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

      self.playerIDs.append(player.id)
      self.botHandle.activePlayers.update({ player.id: self })
      
      if len(self.playerIDs) in self.properties["sizes.sizes"]:
      #
        await self.Start()
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
      await self.Start()
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
      return
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
      return
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
      return
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
      return
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

      self.botHandle.activePlayers[soughtPlayer.id] = self
      self.playerIDs.append(soughtPlayer.id)

      if len(self.playerIDs) in self.properties["sizes.sizes"]:
      #
        await self.Start()
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
    elif soughtPlayer.id not in self.playerIDs:
    #
      await self.botHandle.messager.SendEmbed(
        context.channel,
        {
          "author": "SDMBot",
          "description": "{INFO} {target} is not in this game!" \
            .format(INFO = EMOTES["INFO"], target = soughtPlayer.mention),
          "title": self.name,
          "colour": COLOURS["INFO"]
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
          "description": "{SUCCESS} {target} was removed from the game!" \
            .format(SUCCESS = EMOTES["SUCCESS"], target = soughtPlayer.mention),
          "title": self.name,
          "colour": COLOURS["SUCCESS"]
        },
        delete_after = None
      )

      self.botHandle.activePlayers.pop(soughtPlayer.id)
      self.playerIDs.remove(soughtPlayer.id)

      if len(self.playerIDs) in self.properties["sizes.sizes"]:
      #
        await self.Start()
      #
    #
  #


  async def Edit (self, context, key, action, value):
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

    if key.startswith("size"):
    #
      await self.botHandle.messager.SendEmbed(
        context.channel,
        {
          "author": "SDMBot",
          "description": "{WARN} You should use `{pref} resize` instead." \
            .format(WARN = EMOTES["WARNING"], pref = self.botHandle.globalConfigs["prefix"]),
          "title": self.name,
          "colour": COLOURS["WARNING"]
        },
        delete_after = None
      )
      return
    #

    if action == 'get':
    #
      data = self.globalConfigs.get(key)
      
      if key in Game.forbiddenKeys:
      #
        await self.messager.SendEmbed(
          context.channel,
          {
            "author": "SDMBot",
            "description": "{WARNING} {mention}, you should not directly modify this key." \
              .format(WARNING = EMOTES["WARNING"], mention = player.mention),
            "title": "Configuration for {game}".format(game = self.name),
            "colour": COLOURS["WARNING"]
          },
          delete_after = None
        )
        return
      #

      if data is None:
      #
        await self.messager.SendEmbed(
          context.channel,
          {
            "author": "SDMBot",
            "description": "{ERR} Key `{key}` was not found!" \
              .format(ERR = EMOTES["ERR"], key = key),
            "title": "Configuration for {game}".format(game = self.name),
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
              .format(SUCCESS = EMOTES["SUCCESS"], key = key, val = data),
            "title": "Configuration for {game}".format(game = self.name),
            "colour": COLOURS["SUCCESS"]
          },
          delete_after = None
        )
      #
    #
    elif action == 'set':
    #
      self.globalConfigs.update({ key: value })

      await self.messager.SendEmbed(
        context.channel,
        {
          "author": "SDMBot",
          "description": "{SUCCESS} Set key `{key}` to value `{val}`." \
            .format(SUCCESS = EMOTES["SUCCESS"], key = key, val = value),
          "title": "Configuration for {game}".format(game = self.name),
          "colour": COLOURS["SUCCESS"]
        },
        delete_after = None
      )
    #
    elif action == "add":
    #
      if self.globalConfigs.get(key) is None:
      #
        self.globalConfigs.update({ key: [] })
      #

      if type(self.globalConfigs[key]) is not list:
      #
        await self.messager.SendEmbed(
          context.channel,
          {
            "author": "SDMBot",
            "description": "{ERROR} Value at key `{key}` exists and is not a list!\nRun `{prefix} global {key} set []` first." \
              .format(ERR = EMOTES["ERR"], key = key, prefix = self.globalConfigs["prefix"]),
            "title": "Configuration for {game}".format(game = self.name),
            "colour": COLOURS["ERR"]
          },
          delete_after = None
        )
      #
      else:
      #
        self.globalConfigs[key].append(value)
        lis = self.globalConfigs[key]

        await self.messager.SendEmbed(
          context.channel,
          {
            "author": "SDMBot",
            "description": "{SUCCESS} Appended value `{value}` to list at key `{key}`\n(The list is `{l}`)." \
              .format(SUCCESS = EMOTES["SUCCESS"], key = key, value = value, l = lis),
            "title": "Configuration for {game}".format(game = self.name),
            "colour": COLOURS["SUCCESS"]
          },
          delete_after = None
        )
      #
    #
    elif action == "remove":
    #
      if self.globalConfigs.get(key) is None or type(self.globalConfigs[key]) is not list:
      #
        await self.messager.SendEmbed(
          context.channel,
          {
            "author": "SDMBot",
            "description": "{ERROR} There is no list at key `{key}`!" \
              .format(ERR = EMOTES["ERR"], key = key),
            "title": "Configuration for {game}".format(game = self.name),
            "colour": COLOURS["ERR"]
          },
          delete_after = None
        )
      #
      else:
      #
        lis = self.globalConfigs[key]

        if value not in lis:
        #
          await self.messager.SendEmbed(
            context.channel,
            {
              "author": "SDMBot",
              "description": "{INFO} Value `{value}` was not in the list at key `{key}`!\n(The list is `{l}`)." \
                .format(INFO = EMOTES["INFO"], key = key, val = value, l = lis),
              "title": "Configuration for {game}".format(game = self.name),
              "colour": COLOURS["INFO"]
            },
            delete_after = None
          )
        #
        else:
        #
          self.globalConfigs[key].remove(value)

          await self.messager.SendEmbed(
            context.channel,
            {
              "author": "SDMBot",
              "description": "{SUCCESS} Removed value `{value}` from the list at key `{key}` (new list is `{l}`)." \
                .format(SUCCESS = EMOTES["SUCCESS"], key = key, val = value, l = self.globalConfigs[key]),
              "title": "Configuration for {game}".format(game = self.name),
              "colour": COLOURS["SUCCESS"]
            },
            delete_after = None
          )  
        #
      #
    #
    else:
    #
      await self.Usage(context.channel, Game.commands["edit"])
      return
    #

    if len(self.playerIDs) in self.properties["sizes.sizes"]:
    #
      await self.Start()
    #
  #


  async def Rename (self, context, name):
  #
    player = context.author

    if player.id != self.owner.id and player.id not in self.botHandle.globalConfigs["moderators"]:
    #
      await self.NoPermission(player, context.channel)
      return
    #
    else:
    #
      self.name = "Game '" + ' '.join(list(map(lambda s: str(s) if type(s) is int else s, name))) + "'"
      await self.category.edit(name = self.name)
      await self.botHandle.messager.SendEmbed(
        context.channel,
        {
          "author": "SDMBot",
          "description": "{SUCCESS} Changed the game's name to `{name}`." \
            .format(SUCCESS = EMOTES["SUCCESS"], name = self.name),
          "title": self.name,
          "colour": COLOURS["SUCCESS"]
        },
        delete_after = None
      )
    #
  #


  async def Resize (self, context, sizes : str):
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

    for size in sizes_list:
    #
      if size not in self.properties["sizes.legal"]:
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

    self.properties["sizes.sizes"] = sizes_list

    await self.botHandle.messager.SendEmbed(
      context.channel,
      {
        "author": "SDMBot",
        "description": "{SUCCESS} Changed the game's sizes to `{sizes}`." \
          .format(SUCCESS = EMOTES["SUCCESS"], sizes = sizes_list),
        "title": self.name,
        "colour": COLOURS["SUCCESS"]
      },
      delete_after = None
    )

    if len(self.playerIDs) in self.properties["sizes.sizes"]:
    #
      await self.Start()
    #
  #


  async def Unfreeze (self, context):
  #
    player = context.author

    if not self.isRunning:
    #
      await self.botHandle.messager.SendEmbed(
        context.channel, 
        {
          "author": "SDMBot",
          "description": "{ERROR} {mention}, this game is not running!" \
            .format(ERROR = EMOTES["ERR"], mention = player.mention),
          "title": self.name,
          "colour": COLOURS["WARNING"]
        }, 
        delete_after = None
      )
    #
    elif player.id not in self.botHandle.globalConfigs["moderators"]:
    #
      await self.NoPermission(player, context.channel)
    #
    else:
    #
      self.isFrozen = False
      await self.botHandle.messager.SendEmbed(
        context.channel,
        {
          "author": "SDMBot",
          "description": "{SUCCESS} The game is unfrozen.",
          "title": self.name,
          "colour": COLOURS["SUCCESS"]
        },
        delete_after = None
      )
    #
  #

  
  async def Freeze (self, context):
  #
    player = context.author

    if not self.isRunning:
    #
      await self.botHandle.messager.SendEmbed(
        context.channel, 
        {
          "author": "SDMBot",
          "description": "{ERROR} {mention}, this game is not running!" \
            .format(ERROR = EMOTES["ERR"], mention = player.mention),
          "title": self.name,
          "colour": COLOURS["WARNING"]
        }, 
        delete_after = None
      )
    #
    elif player.id not in self.botHandle.globalConfigs["moderators"]:
    #
      await self.NoPermission(player, context.channel)
    #
    else:
    #
      self.isFrozen = True
      await self.botHandle.messager.SendEmbed(
        context.channel,
        {
          "author": "SDMBot",
          "description": "{SUCCESS} The game is frozen.",
          "title": self.name,
          "colour": COLOURS["SUCCESS"]
        },
        delete_after = None
      )
    #
  #


  async def Remake (self, context):
  #
    pass
  #


  async def Go (self, context):
  #
    pass
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
    fields = []
    for key in self.properties.keys():
      fields.append({ "name": SEP, "value": "`{key}` : *{type}* {SEP} \n`{value}`" \
        .format(SEP = SEP, key = key, type = type(self.properties[key]), value = self.properties[key]) })

    players = []
    for p in self.playerIDs:
      player = await context.guild.fetch_member(p)
      players.append(player)

    data = \
    {
      "author": "SDMBot",
      "description": "**Players** ({len}):".format(len = len(players)) + \
        ", ".join(list(map(lambda p: p.mention, players))) + \
        "\n**Configuration:**",
      "title": self.name,
      "colour": COLOURS["INFO"],
      "fields": fields
    }

    await self.botHandle.messager.SendEmbed(context.channel, data, delete_after = None)
  #


  async def HandleCommand (self, context, command, args):
  #
    self.mutex.acquire(blocking=True)

    if    command in ["join", "j"]:
    #
      if args not in [None, []]: await self.botHandle.Usage(context.channel, Game.commands["join"])
      else: await self.Join(context)
    #
    elif  command in ["leave", "l"]:
    #
      if args not in [None, []]: await self.botHandle.Usage(context.channel, Game.commands["leave"])
      else: await self.Leave(context)
    #
    elif  command in ["delete", "del"]:
    #
      if args not in [None, []]: await self.botHandle.Usage(context.channel, Game.commands["delete"])
      else: await self.Delete(context)
    #
    elif  command in ["status", "lobby"]:
    #
      if args not in [None, []]: await self.botHandle.Usage(context.channel, Game.commands["status"])
      await self.Status(context)
    #
    elif  command in ["add", "invite"]:    
    #
      if args is None or len(args) != 1: await self.botHandle.Usage(context.channel, Game.commands["invite"])
      else: await self.Add(context, args[0])
    #
    elif  command in ["remove", "kick"]:
    #
      if args is None or len(args) != 1: await self.botHandle.Usage(context.channel, Game.commands["remove"])
      else: await self.Remove(context, args[0])
    #
    elif  command in ["edit"]:
    #
      if args is None or len(args) not in [2, 3] or type(args[1]) is not str: await self.botHandle.Usage(context.channel, Game.commands["edit"])
      else: await self.Edit(context, args[0], args[1].toLower(), self.Specialize(args[2]) if len(args) > 2 else None)
    #
    elif  command in ["resize", "size"]:
    #
      if args is None or len(args) != 1: await self.botHandle.Usage(context.channel, Game.commands["resize"])
      else: await self.Resize(context, args[0])
    #
    elif  command in ["rename"]:
    #
      if args is None: await self.botHandle.Usage(context.channel, Game.commands["rename"])
      else: await self.Rename(context, args)
    #
    elif  command in ["remake"]:
    #
      if args not in [None, []]: await self.botHandle.Usage(context.channel, Game.commands["remake"])
      else: await self.Remake(context)
    #
    elif  command in ["go"]:
    #
      if args not in [None, []]: await self.botHandle.Usage(context.channel, Game.commands["go"])
      else: await self.Go(context)
    #
    elif  command in ["freeze", "pause"]:
    #
      if args not in [None, []]: await self.botHandle.Usage(context.channel, Game.commands["freeze"])
      else: await self.Freeze(context)
    #
    elif  command in ["unfreeze", "resume"]:
    #
      if args not in [None, []]: await self.botHandle.Usage(context.channel, Game.commands["unfreeze"])
      else: await self.Unfreeze(context)
    #

    try:
    #
      await context.delete()
    #
    except discord.NotFound:
    #
      pass
    #

    self.mutex.release()

    if self.didGo:
    #
      await self.Cleanup()
    #
  #


  async def HandleEvent (self, data : any, form : str):
  #
    self.mutex.acquire(blocking = True)

    if self.isRunning and data is not None and not self.isFrozen:
    #
      await self.activeComponents[self.componentPointer].Handle(data, form)
    #

    self.mutex.release()
  #


  async def UpdateTo (self, slot : str, name = None):
  #
    if name is not None and self.activeComponents[slot].name != name:
    #
      self.activeComponents[slot].Teardown()
      self.activeComponents[slot] = await self.botHandle.componentfactory.Create(slot, name, self)
    #

    self.componentPointer = slot
    await self.activeComponents[slot].Setup()
  #


  async def Preview (self):
  #
    imageHandler = self.properties["board-manager"]
    await self.activeComponents[imageHandler].Update()
  #


  async def Start (self):
  #
    playerPerms = \
    {
      self.category.guild.default_role: Game.read_only
    }

    for pid in self.playerIDs:
    #
      player = await self.category.guild.fetch_member(pid)
      playerPerms.update({ player: Game.read_write })
    #

    mainChannel = await self.category.create_text_channel(
      name = 'game-chat',
      overwrites = playerPerms
    )

    self.channels['main'] = mainChannel

    entryPoint = self.properties["entry-point"]
    await self.activeComponents[entryPoint].Setup()
  #


  async def Cleanup (self):
  #
    name    = self.name
    id      = self.category.id
    players = self.playerIDs
    
    self.botHandle.activeGames.pop(id)
    for pid in players:
      self.botHandle.activePlayers.pop(pid)

    for ch in self.channels.values():
      await ch.delete()
    
    await self.category.delete()

    self.botHandle.logger.info("Successfully destroyed game '{name}' (id {uuid})." \
        .format(name = name, uuid = id),
      __file__)
  #