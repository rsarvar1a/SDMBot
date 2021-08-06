#!/usr/bin/env python


import re
import json
import os
import sys
import discord

#

from defs           import *
from src.client.bot import TournamentBot



#
#   Event listeners.
#

bot = TournamentBot()


@bot.discordClient.event
async def on_ready ():
#
  bot.logger.info("Connected as {u}#{d}!".format(
      u = bot.discordClient.user.name, 
      d = bot.discordClient.user.discriminator), 
    __file__)
#


@bot.discordClient.event
async def on_message (message : discord.Message):
#
  if message.author.bot: return

  bot.logger.debug("Message from {u}#{d}: '{content}'".format(
      u = message.author.name, 
      d = message.author.discriminator, 
      content = message.content.replace('\n', ' ')), 
    __file__)

  hasPrefix = str(message.content).startswith(bot.globalConfigs["prefix"])
  content   = str(message.content).removeprefix(bot.globalConfigs["prefix"]).lstrip().rstrip()

  as_array  = content.split()
  as_array  = list(map(lambda s: re.sub(r'<@!?([0-9]+)>', r'\g<1>', s), as_array))
  as_array  = list(map(lambda s: int(s) if s.isnumeric() else s, as_array))

  command   = as_array[0]  if len(as_array) > 0 else None
  command   = command.lower() if type(command) is str else command
  
  args      = as_array[1:] if len(as_array) > 0 else None

  if hasPrefix: # Handle special globals; otherwise pass them off to the active game.
  #
    if (message.guild == None):
    #
      await bot.messager.SendEmbed(message.author.dm_channel, MSGS.ErrorNoDMS, delete_after = STD_TIME)
      return
    #

    bot.logger.debug("Processing command {prefix} `{command}` {args}.".format(prefix = bot.globalConfigs["prefix"], command = command, args = args), __file__)

    if await bot.HandleCommand(message, command, args):
    #
      await message.delete(delay = TRIGGER_TIME)
    #
    else:
    #
      if message.channel.category is not None and message.channel.category.id in bot.activeGames.keys():
      #
        await bot.activeGames[message.channel.category.id].HandleCommand(message, command, args)
      #
      else:
      #
        await bot.messager.SendEmbed(message.channel, MSGS.ErrorNoGame, delete_after = STD_TIME)
        await message.delete(delay = TRIGGER_TIME)
      #
    #
  #
  else: # Handle prefixless bot interactions in active categories.
  #
    bot.logger.debug("Processing message {words}.".format(words = as_array), __file__)

    if message.channel.category is not None and message.channel.category.id in bot.activeGames.keys():
    #
      await bot.activeGames[message.channel.category.id].HandleEvent(message, "message")
    #
  #
#


@bot.discordClient.event
async def on_raw_reaction_add (payload : discord.RawReactionActionEvent):
#
  category = await bot.discordClient.fetch_channel(payload.channel_id)
  if category is not None and category.id in bot.activeGames.keys():
  #
    await bot.activeGames[category.id].HandleEvent(payload, "reaction_add")
  #
#


@bot.discordClient.event
async def on_raw_reaction_remove (payload : discord.RawReactionActionEvent):
#
  category = await bot.discordClient.fetch_channel(payload.channel_id)
  if category is not None and category.id in bot.activeGames.keys():
  #
    await bot.activeGames[category.id].HandleEvent(payload, "reaction_remove")
  #
#



#
#   Let's go!
#

bot.discordClient.run(bot.globalConfigs['token'])
