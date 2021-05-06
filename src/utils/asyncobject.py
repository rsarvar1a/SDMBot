
class AsyncObject (object):


  async def __new__ (clazz, *args, **kwargs):
  # 
    instance = super().__new__(clazz)
    await instance.__init__(*args, **kwargs)
    return instance
  #


  async def __init__ (self):
  #
    pass
  #