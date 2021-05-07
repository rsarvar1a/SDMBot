
import sys, os

#

ROOT_PATH   = os.path.dirname(os.path.abspath(__file__))
ASSET_PATH  = os.path.join(ROOT_PATH, "assets/")
SRC_PATH    = os.path.join(ROOT_PATH, "src/")
CONFIG_FILE = os.path.join(ROOT_PATH, "config.json")
CONFIG_MAIN = os.path.join(ROOT_PATH, "config.json.master")

EMOTES = \
{
  "ERR": ":no_entry:",
  "WARNING": ":warning:",
  "SUCCESS": ":white_check_mark:",
  "INFO": "information_source:"
}

COLOURS = \
{
  "ERR": 14438496,
  "WARNING": 16769101,
  "SUCCESS": 10805325,
  "INFO": 11258335
}

STD_TIME = 3
TRIGGER_TIME = 0


class MSGS (object):

  ErrorNoDMS = \
  {
    "author": "SDMBot",
    "title": "Invalid Location",
    "description": "{ERR_EMOTE} You can't use me in a DM channel!" \
      .format(ERR_EMOTE = EMOTES["ERR"]),
    "colour": COLOURS["ERR"]
  }
  #
  ErrorNoGame = \
  {
    "author": "SDMBot",
    "title": "Invalid Location",
    "description": "{ERR_EMOTE} There is no game in this category!" \
      .format(ERR_EMOTE = EMOTES["ERR"]),
    "colour": COLOURS["ERR"]
  }


SEP = "—"
ICON_URL = "https://cdn.discordapp.com/avatars/840322898693586944/6add5bf8522d00653c7c43556738d6ea.png?size=256"