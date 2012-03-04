def weirdimport(fullpath):
  global project

  import os
  import sys
  sys.path.append(os.path.dirname(fullpath))
  try:
      project = __import__(os.path.basename(fullpath))
      sys.modules['project'] = project
  finally:
      del sys.path[-1]

weirdimport("./conf")

print dir()
from conf.dev import settings
print dir()
