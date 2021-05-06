
import sys, os

#

ROOT_PATH   = os.path.dirname(os.path.abspath(__file__))
ASSET_PATH  = os.path.join(ROOT_PATH, "assets/")
SRC_PATH    = os.path.join(ROOT_PATH, "src/")
CONFIG_FILE = os.path.join(ROOT_PATH, "config.json")

EMOTES = \
{
  "ERR": ":no_entry:"
}

COLOURS = \
{
  "ERR": 14438496
}

STD_TIME = 3

class ERRS (object):

  ErrorNoDMS = \
  {
    "author": "SDMBot",
    "title": None,
    "description": "{ERR_EMOTE} You can't use me in a DM channel!" \
      .format(ERR_EMOTE = EMOTES["ERR"]),
    "colour": COLOURS["ERR"]
  }
  #
  ErrorNoGame = \
  {
    "author": "SDMBot",
    "title": None,
    "description": "{ERR_EMOTE} There is no game in this category!" \
      .format(ERR_EMOTE = EMOTES["ERR"]),
    "colour": COLOURS["ERR"]
  }