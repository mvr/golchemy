import sys

from basics import *
from common import *

# original = block
# originalname = 'block'
activename = sys.argv[1]
active = patternmap[activename]

originalname = sys.argv[2]
original = patternmap[originalname]

filecols = []
with open(f"cols/{activename}-{originalname}.txt", 'r') as f:
    filecols = eval(f.read())
# filecols.reverse()

with open(f"cols/{activename}-{originalname}-rays.txt", 'r') as f:
    rays = eval(f.read())

# seenash = set()
result = lt.pattern()
for maxt, vec, coltime, rle in filecols:
    if maxt == None:
        result[vec.x, vec.y] = 1
        continue

    ash = (original.translate(vec) + active)[maxt+100]

    testtime = maxt+100
    rash = active[maxt+100]
    if ash == (rash + original.translate(vec)[testtime]):
        print(f"Skipping {vec} col {coltime} lifetime {maxt}, seems to be no collision: {rle}")
        continue

    ray = find_ray(rays, coltime, vec, ash.population)
    if ray:
        print(f"Skipping {vec} col {coltime} lifetime {maxt}, seems to be on ray {ray}: {rle}")
        continue

    result[vec.x, vec.y] = 1

stamp = lt.pattern('5o$2o2bo$o2b2o$2ob2o$5o!').shift(-1,-1)
result = (result - stamp) + stamp

print(result)
print(result.rle_string())
