
from datetime import datetime
import os

#

from defs import ROOT_PATH

#

class Logger (object):


  def __init__ (self, config : dict):
  #
    self.prio = self.Numerical(config["logging_level"])
  #


  def Numerical (self, level : str):
  #
    if level == "error":     return 3
    elif level == "warning": return 2
    elif level == "info":    return 1
    elif level == "debug":   return 0
  #


  def Colour (self, level : str):
  #
    if level == "error":      return "\033[38;5;235;48;5;167;1m" 
    elif level == "warning":  return "\033[38;5;235;48;5;178;1m"
    elif level == "info":     return "\033[38;5;235;48;5;159;1m"
    elif level == "debug":    return "\033[38;5;235;48;5;183;1m"
    elif level == "content":  return "\033[38;5;252;48;5;236m"
  #


  def Reset (self):
  #
    return "\033[0m"
  #


  def info (self, content : str, location : str):
  #
    self.Log(content, location, "info")
  #


  def debug (self, content : str, location : str):
  #
    self.Log(content, location, "debug")
  #


  def warning (self, content : str, location : str):
  #
    self.Log(content, location, "warning")
  #


  def error (self, content : str, location : str):
  #
    self.Log(content, location, "error")
  #


  def Log (self, content : str, location : str, priority : str):
  #
    if (self.Numerical(priority) >= self.prio):
      ret = "\n{date} in {file}:\n{tagcolour} {tag}{contentcolour} {content} {reset}".format(
        date = datetime.now().strftime('%I:%M:%S %p').ljust(11),
        tagcolour = self.Colour(priority), 
        tag = priority.upper().ljust(7),
        file = os.path.relpath(location, ROOT_PATH),
        contentcolour = self.Colour("content"), 
        content = content, 
        reset = self.Reset()
      )
      print(ret)
  #