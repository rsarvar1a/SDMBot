
import os
import math
import random

#

from src.game.game                import Game
from src.game.component.component import Component

#

class SecrethitlerComponentPremiseDefault (Component):


  async def __init__ (self, game : Game):
  #
    await super().__init__(game)
  #


  async def Setup (self):
  #
    # Game size.

    size = len(self.game.playerIDs)
    self.game.properties["sizes.size"]  = size
    self.game.properties["sizes.alive"] = size
        
    # Prepare board.

    await self.PrepareForSize()

    # Create components.

    await self.CreateDefaults()

    # Create player channels and player info.

    await self.PreparePlayers()
    await self.CreatePrivates()
    await self.DealRoles()

    # Launch.

    await self.game.UpdateTo("nomination")
  #


  async def PrepareForSize (self):
  #
    board_overrides = self.game.properties["boards-overrides"][str(self.game.properties["sizes.size"])]

    lib_base = self.game.properties["boards.liberal"].copy()
    lib_plus = board_overrides.get("liberal")

    if lib_plus is not None: 
    #
      for i in range(5):
      #
        lib_base[i].update(lib_plus[i])
      #
    #

    fas_base = self.game.properties["boards.fascist"].copy()
    fas_plus = board_overrides.get("fascist")

    if fas_plus is not None:
    #
      for i in range(6):
      #
        fas_base[i].update(fas_plus[i])
      #
    #

    self.game.properties["real-boards"]        = { "liberal": lib_plus, "fascist": fas_plus }
    self.game.properties["policies-index"]     = { "liberal": 0, "fascist": 0 }
    self.game.properties["last-policy-played"] = None

    # Throw in the deck because it's constant for the premise.

    self.game.properties["deck"] = { "liberal": 6, "fascist": 11 }
  #


  async def CreateDefaults (self):
  #
    for (slot, comp) in self.game.properties["defaults"].items():
    #
      if self.game.activeComponents.get(slot) is not None:
      #
        self.game.activeComponents[slot] = await self.game.botHandle.componentfactory.Create(slot, comp, self.game)
      #
    #
  #


  async def PreparePlayers (self):
  #
    random.shuffle(self.game.playerIDs)
    self.game.properties["seats"] = []

    for i in range(self.game.properties["sizes.size"]):
    #
      p = await self.game.category.guild.fetch_member(self.game.playerIDs[i])
      self.game.properties["seats"].append(
        {
          "player":   p,
          "channel":  None,
          "alive":    True,
          "role":     None,
          "rolecard": None
        }
      )
    #
  #


  async def CreatePrivates (self):
  #
    for i in range(self.game.properties["sizes.size"]):
    #
      playerHere = self.game.properties["seats"][i]["player"]

      self.game.channels[i] = await self.game.category.create_text_channel(
        name = "seat-{n}".format(n = i + 1),
        overwrites = \
        {
          playerHere: Game.read_write,
          self.game.category.guild.default_role: Game.private
        }
      )

      self.game.properties["seats"][i]["channel"] = self.game.channels[i]
    #
  #


  async def DealRoles (self):
  #
    size = self.game.properties["sizes.size"]
    
    roles = \
    [
      "hitler", "fascist", "liberal", "liberal", "liberal", 
      "liberal", "fascist", "liberal", "fascist", "liberal"
    ][slice(0, size, 1)]

    random.shuffle(roles)

    count_f = 1
    count_l = 1

    numLibs = math.floor(size / 2) + 1
    numRegs = size - numLibs - 1

    lib_urls = ["role-liberal-{n}.png".format(n = n) for n in range(1, 7)]
    fas_urls = ["role-fascist-{n}.png".format(n = n) for n in range(1, 4)]

    random.shuffle(lib_urls)
    random.shuffle(fas_urls)

    hit_url  = "role-hitler.png"

    fas_team = []
    hitler = None

    for i in range(size):
    #
      self.game.properties["seats"][i]["role"] = roles[i]

      if roles[i] == "liberal": 
      #
        self.game.properties["seats"][i]["rolecard"] = lib_urls[count_l]
        count_l += 1
      #
      elif roles[i] == "fascist":
      #
        fas_team.append(i)
        self.game.properties["seats"][i]["rolecard"] = fas_urls[count_f]
        count_f += 1
      #
      else:
      #
        fas_team.append(i)
        hitler = i
        self.game.properties["seats"][i]["rolecard"] = hit_url
      #
    #

    for i in range(size):
    #
      seat = self.game.properties["seats"][i]
      roleimg = os.path.join(self.game.paths["assets"], seat["rolecard"])

      if seat["role"] == "liberal":
      #
        await self.game.botHandle.messager.SendEmbed(
          seat["channel"],
          {
            "author": "SDMBot",
            "description": "You receive the liberal role and take seat {n}.".format(n = i + 1),
            "title": self.game.name,
            "colour": self.game.properties["colours.liberal"],
            "image": \
            {
              "name": "rolecard.png",
              "source": roleimg
            }
          },
          delete_after = None
        )
      #
      elif seat["role"] == "fascist":
      #
        fas_teammates = [self.game.properties["seats"][f] for f in fas_team if f != i]

        if size == 5:
        #
          await self.game.botHandle.messager.SendEmbed(
            seat["channel"],
            {
              "author": "SDMBot",
              "description": "You receive the fascist role and take seat {n}.\nYour Hitler is {hitler}." \
                .format(n = i + 1, hitler = self.game.properties["seats"][hitler]["player"].mention),
              "title": self.game.name,
              "colour": self.game.properties["colours.fascist"],
              "image": \
              {
                "name": "rolecard.png",
                "source": roleimg
              }
            },
            delete_after = None
          )
        #
        else:
        #
          await self.game.botHandle.messager.SendEmbed(
            seat["channel"],
            {
              "author": "SDMBot",
              "description": "You receive the fascist role and take seat {n}.\nYour other fascists are {team}, of which Hitler is {hitler}." \
                .format(
                  n = i + 1, hitler = self.game.properties["seats"][hitler]["player"].mention,
                  team = ", ".join(list(map(lambda p: p["player"].mention, fas_teammates))),
                ),
              "title": self.game.name,
              "colour": self.game.properties["colours.fascist"],
              "image": \
              {
                "name": "rolecard.png",
                "source": roleimg
              }
            },
            delete_after = None
          )
        #
      #
      elif seat["role"] == "hitler":
      #
        fas_teammates = [self.game.properties["seats"][f] for f in fas_team if f != i]

        if size == 5:
        #
          await self.game.botHandle.messager.SendEmbed(
            seat["channel"],
            {
              "author": "SDMBot",
              "description": "You receive the Hitler role and take seat {n}.\nYour fascist is {fascist}." \
                .format(n = i + 1, fascist = fas_teammates[0]["player"].mention),
              "title": self.game.name,
              "colour": self.game.properties["colours.hitler"],
              "image": \
              {
                "name": "rolecard.png",
                "source": roleimg
              }
            },
            delete_after = None
          )
        #
        else:
        #
          await self.game.botHandle.messager.SendEmbed(
            seat["channel"],
            {
              "author": "SDMBot",
              "description": "You receive the Hitler role and take seat {n}.".format(n = i + 1),
              "title": self.game.name,
              "colour": self.game.properties["colours.hitler"],
              "image": \
              {
                "name": "rolecard.png",
                "source": roleimg
              }
            },
            delete_after = None
          )
        #
      #
    #
  #
