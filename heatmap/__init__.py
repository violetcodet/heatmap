import sys

if sys.hexversion < 0x02060000:
  raise Exception('Heatmap requires python 2.6 or greater.');

from .heatmap import Heatmap
