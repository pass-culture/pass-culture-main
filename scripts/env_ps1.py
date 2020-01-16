import os
import sys


def prompt():
  try:
    if os.environ['ENV'] == 'production':
      return '\x1b[1;49;31mProduction >>>\x1b[0m '
    elif os.environ['ENV'] == 'staging':
      return '\x1b[1;49;33mStaging >>>\x1b[0m '
    else:
      return '\x1b[2;49;37m>>>\x1b[0m '
  except KeyError:
    print("Environment variable 'ENV' is not set")
    return '\x1b[2;49;37m>>>\x1b[0m '

sys.ps1 = prompt()

