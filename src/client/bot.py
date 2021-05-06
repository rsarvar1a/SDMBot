
import json
import discord

#

from defs import *
from src.utils.logging import Logger
from src.utils.io import MessageHandler



#
#   Main bot class, controls everything.
#

class TournamentBot (object):

  globals = \
  [
    "new" # <prefix> [ new <variant> [size] ] name
  ]

  def __init__ (self):
  #
    self.globalConfigs = json.load(open(CONFIG_FILE))

    self.discordClient = discord.Client()
    self.logger        = Logger(self.globalConfigs)
    self.messager      = MessageHandler(self.globalConfigs)

    self.activeGames   = {}
    self.activePlayers = {}
  #

  async def HandleCommand(self, context : discord.Message, command : str, args : list):
  #
    pass
  #
#