
import discord
from discord import permissions

#

from src.utils.asyncobject import AsyncObject

#

class Game (AsyncObject):

  commands = \
  [
    "join",   # ()
    "leave",  # ()
    "add",    # mention 
    "remove", # mention
    "resize", # int
    "edit",   # key value
    "delete", # ()
    "status", # ()
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


  async def __init__ (self, bot, context : discord.Message, gameName : str):
  #
    self.botHandle = bot
    self.playerIDs = [context.author.id]

    self.gameCategory = await context.channel.guild.create_category(name = gameName)

    self.gameChannels = \
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

    self.botHandle.activeGames.update({ self.gameCategory.id: self })
    self.botHandle.activePlayers.update({ context.author.id: self })
  #


  async def Join (self, context):
  #
    pass
  #


  async def Leave (self, context):
  #
    pass
  #


  async def Add (self, context):
  #
    pass
  #


  async def Remove (self, context):
  #
    pass
  #


  async def Resize (self, context):
  #
    pass
  #