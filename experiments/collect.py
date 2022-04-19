import sys
import glob

from basics import *
from common import *

import pprint

wins = []
for n in glob.glob("winners/nine/*.txt"):
    with open(n, 'r') as f:
        wins += eval(f.read())

wins = list(sorted(wins, key=lambda x: -x[3]))
pp = pprint.PrettyPrinter(indent=2)
print(pp.pformat(wins))
