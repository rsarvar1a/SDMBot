 
import discord
from datetime import datetime

#

from defs import *

#

class MessageHandler (object):


  def __init__ (self, config, bot):
  #
    self.botHandle = bot
  #


  async def SendMessage (self, channel : discord.ChannelType, data : str, delete_after : int = None):
  #
    self.botHandle.logger.Reflect("bot.response: '" + data + "'", "debug")
    
    return await channel.send(content = data, delete_after = delete_after)
  #


  async def SendEmbed (self, channel : discord.ChannelType, data : dict, delete_after : int = None):
  #
    constructed = discord.Embed(
      title       = data.get("title"),
      author      = data.get("author"),
      color       = data.get("colour"),
      description = data.get("description")
    )
    
    f = None
    if data.get("file") is not None:
    #

      f = discord.File(fp = data.get("file")["source"], filename = data.get("file")["name"])
      constructed.set_image(
        url = "attachment://{ref}" \
          .format(ref = data.get("file")["name"])
      )
    #

    constructed.set_footer(
      text = "SDMBot {sep} {date}" \
        .format(sep = SEP, date = datetime.now().strftime('%I:%M:%S %p')),
      icon_url = ICON_URL
    )

    if data.get("fields") is not None:
      for field in data.get("fields"):
        constructed.add_field(name = field["name"], value = field["value"])

    self.botHandle.logger.Reflect("bot.response: '" + data.get("description") + "'\n" + ('\n'.join(list(map(lambda d: d["name"] + ": " + d["value"], data.get("fields")))) if data.get("fields") else ""), data.get("colour"))

    return await channel.send(embed = constructed, file = f, delete_after = delete_after)
  #