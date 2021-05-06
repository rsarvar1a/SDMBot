
import discord

#

from defs import *

#

class MessageHandler (object):


  def __init__ (self, config):
  #
    pass
  #


  async def SendMessage (self, channel : discord.ChannelType, data : str, delete_after : int = None):
  #
    return await channel.send(content = data, delete_after = delete_after)
  #


  async def SendEmbed (self, channel : discord.ChannelType, data : dict, delete_after : int = None):
  #
    constructed = discord.Embed(
      title       = data.get("title"),
      author      = data.get("author"),
      color       = data.get("colour"),
      description = data.get("description"),
      image       = data.get("image")
    )
    
    if data.get("fields") is not None:
      for field in data.get("fields"):
        constructed.add_field(field)

    return await channel.send(embed = constructed, delete_after = delete_after)
  #