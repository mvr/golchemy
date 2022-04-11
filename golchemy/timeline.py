import sys
import os.path
from os import path
import atexit

from basics import *
from common import *

import pickle
import pprint

if path.isfile("book.txt"):
    with open(f"book.txt", 'rb') as f:
        book = Book()
        book.reagents, book.table = pickle.load(f)

else:
    reagentfiles = ["reagents/ash.toml", "reagents/constellations.toml", "reagents/commonsmall.toml", "reagents/commonactive.toml", ]
    book = Book.from_toml_object(toml.load(reagentfiles))
    with open(f"book.txt", 'wb') as f:
         pickle.dump((book.reagents,book.table), f)

activename = sys.argv[1]
active = patternmap[activename]

originalname = sys.argv[2]
original = patternmap[originalname]

endt = 300
if len(sys.argv) > 3:
    endt = int(sys.argv[3])

skipt = 0
if len(sys.argv) > 4:
    skipt = int(sys.argv[4])

result = []


# test = lt.pattern('5b2o$2bobo$o2bobobo$7bo$6b2o$2bo3bo$obo!')
# print(test.first_cluster())
# exit()

def is_interesting(schematic):
    if any([r.reagent.name == activename and r.time > 30 for r in schematic.reagents]): return True
    return len(schematic.chaos) == 0 and len(schematic.reagents) <= 4 and any([r.reagent.is_active and r.time > 15 for r in schematic.reagents])


def investigate(coltime, stopt, vec, pat):
    s = Schematic.analyse(book, pat.advance(coltime-1))
    for i in range(coltime, stopt):
        s, _ = s.step(book)
        s.verify()
        if s.pattern == (active.advance(i) + original.advance(i).translate(vec)): continue
        if len(s.reagents) > 10: break
        if is_interesting(s):
            print(f"Success for {vec} at time {i}: {s}")
            result.append((pat.rle_string_only, i, s))
            break

# investigate(54, 300,Vec(8, 15),lt.pattern('2b2o$3o$bo13$8b2o$8b2o!'))
# exit()

activeseq = active
target = original
done = set()

filecols = []
with open(f"cols/{activename}-{originalname}.txt", 'r') as f:
    filecols = eval(f.read())
filecols.reverse()

with open(f"cols/{activename}-{originalname}-rays.txt", 'r') as f:
    rays = eval(f.read())

def printresults():
    global result
    if len(result) == 0: return
    result = sorted(result, key=lambda x: -x[1])
    pp = pprint.PrettyPrinter(indent=2)
    # with open("checkpoints.txt", 'w') as f:
    #     f.write(f"{pp.pformat(checkpoints)}")
    # print("wrote checkpoints")
    # with open("seenash.txt", 'w') as f:
    #     f.write(f"{seenash}")
    # with open("seenoctos.txt", 'w') as f:
    #     f.write(f"{seenoctos}")
    with open(f"{activename}-{originalname}-reactions.txt", 'w') as f:
        f.write(f"{pp.pformat(result)}")
    print("wrote reactions")

atexit.register(printresults)

seenash = set()

for maxt, vec, coltime, rle in filecols:
    if maxt < skipt: continue
    if coltime == 0: continue
    startingpat = original.translate(vec) + active

    ash = startingpat[16384]
    d = ash.digest()
    if d in seenash:
        print(f"Skipping {vec} col {coltime} lifetime {maxt}, seems ash already: {rle}")
        continue
    seenash.add(d)

    # if maxt == 1104:
    #     activeash = active[maxt+100]
    #     if ash == (activeash + original.translate(vec)):
    #         print(f"Skipping {vec} col {coltime} lifetime {maxt}, seems to be no collision: {rle}")
    #         continue

    ray = find_ray(rays, coltime, vec, ash.population)
    if ray:
        print(f"Skipping {vec} col {coltime} lifetime {maxt}, seems to be on ray {ray}: {rle}")
        continue

    #stopt = min(maxt, 1000+coltime)
    stopt = maxt
    print(f"Running {vec} col {coltime} lifetime {maxt} to {stopt}: {rle}")
    investigate(coltime, stopt, vec, startingpat)
