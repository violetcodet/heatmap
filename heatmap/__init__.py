import sys

try:
  __version__ = __import__('pkg_resources').get_distribution(__name__).version
except Exception as e:
  __version__ = 'unknown'

if sys.hexversion < 0x02060000:
  raise Exception('Heatmap requires python 2.6 or greater.');

from .heatmap import Heatmap
