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
active = book.reagents[activename].pattern

originalname = sys.argv[2]
original = book.reagents[originalname].pattern

skipt = 0
if len(sys.argv) > 3:
    skipt = int(sys.argv[3])

phase = 0
if len(sys.argv) > 4:
    phase = int(sys.argv[4])
original = original[phase]

result = []


# test = lt.pattern('5b2o$2bobo$o2bobobo$7bo$6b2o$2bo3bo$obo!')
# print(test.first_cluster())
# exit()

def is_reoccur(schematic):
    if any([r.reagent.name == activename and r.time > 50 and r.trans.lin.name in ['id', 'flip_x', 'flip_y', 'swap_xy'] for r in schematic.reagents]): return True
    return False

def is_interesting(schematic):
    gliders = len([r for r in schematic.reagents if r.reagent.name == 'glider'])

    if (len(schematic.chaos) == 0 and
        len(schematic.reagents) - gliders <= 2
        and any([r.reagent.is_active and r.time > 5 for r in schematic.reagents])): return True
    if (len(schematic.chaos) == 0
        and len(schematic.reagents) - gliders <= 4
        and any([r.reagent.is_active and r.time > 25 for r in schematic.reagents])): return True
    # if (len(schematic.reagents) - gliders <= 4
    #     and any([r.reagent.is_active and r.time > 100 for r in schematic.reagents])): return True

    return False


def investigate(coltime, stopt, col, pat):
    s = Schematic.analyse(book, pat.advance(coltime-1))
    interesting = True
    reoccur = False

    for i in range(coltime, stopt):
        s, es = s.step(book)
        gliders = len([r for r in s.reagents if r.reagent.name == 'glider'])
        if len(s.reagents) - gliders > 10: break

        if interesting and len(es) > 0:
            interesting = False
        if not interesting and is_interesting(s):
            interesting = True
            print(f"Success for {col} at time {i}: {s}")
            result.append((pat.rle_string_only, col, coltime, i, s))

        if reoccur and not any([r.reagent.name == activename for r in s.reagents]):
            reoccur = False
        if not reoccur and is_reoccur(s):
            reoccur = True
            print(f"Reoccur for {col} at time {i}: {s}")
            result.append((pat.rle_string_only, col, coltime, i, s))

        if len(s.reagents) == 1 and len(s.chaos) == 0:
            break

        if len(es) > 0 and len(s.chaos) == 0:
            naive = s.naive_advance(1024)
            if naive.pattern == naive.reconstruct():
                if not interesting and is_interesting(naive):
                    print(f"Success for {col} at time {i}: {s}")
                    result.append((pat.rle_string_only, col, coltime, i, s))
                print(f"Bailing at time {i}: {s}")
                break

# investigate(54, 300,Vec(8, 15),lt.pattern('2b2o$3o$bo13$8b2o$8b2o!'))
# exit()

activeseq = active
target = original
done = set()

outname = ""
rayoutname = ""
reactionoutname = ""
if phase == 0:
    outname = f"cols/{activename}-{originalname}.txt"
    rayoutname = f"cols/{activename}-{originalname}-rays.txt"
    reactionoutname = f"{activename}-{originalname}-reactions.txt"
else:
    outname = f"cols/{activename}-{originalname}-phase-{phase}.txt"
    rayoutname = f"cols/{activename}-{originalname}-rays-phase-{phase}.txt"
    reactionoutname = f"{activename}-{originalname}-reactions-phase-{phase}.txt"

filecols = []
with open(outname, 'r') as f:
    filecols = eval(f.read())
filecols = sorted(filecols, key=lambda x: x[2])

with open(rayoutname, 'r') as f:
    rays = eval(f.read())

def printresults():
    global result
    if len(result) == 0: return
    result = sorted(result, key=lambda x: -x[3])
    pp = pprint.PrettyPrinter(indent=2)
    # with open("checkpoints.txt", 'w') as f:
    #     f.write(f"{pp.pformat(checkpoints)}")
    # print("wrote checkpoints")
    # with open("seenash.txt", 'w') as f:
    #     f.write(f"{seenash}")
    # with open("seenoctos.txt", 'w') as f:
    #     f.write(f"{seenoctos}")
    with open(reactionoutname, 'w') as f:
        f.write(f"{pp.pformat(result)}")
    humanresult = [ (rle, interestingtime, str(sch)) for rle, _, _, interestingtime, sch in result]
    with open(reactionoutname+'human', 'w') as f:
        f.write(f"{pp.pformat(humanresult)}")
    print("wrote reactions")

atexit.register(printresults)

seenash = set()

for maxt, col, coltime, rle in filecols:
    if maxt < skipt: continue
    if coltime == 0: continue

    startingpat = active + col * original
    ash = startingpat[16384]

    if ash == (active.advance(16384) + col * original.advance(16384)):
        print(f"No collision for {col} col {coltime}: {startingpat.rle_string_only}")
        continue

    d = ash.digest()
    if (col.lin, d) in seenash:
        print(f"Skipping {col} col {coltime} lifetime {maxt}, seems ash already: {startingpat.rle_string_only}")
        continue
    seenash.add((col.lin, d))

    # if maxt == 1104:
    #     activeash = active[maxt+100]
    #     if ash == (activeash + original.translate(vec)):
    #         print(f"Skipping {vec} col {coltime} lifetime {maxt}, seems to be no collision: {rle}")
    #         continue

    ray = find_ray(rays, coltime, col, ash.population)
    if ray:
        print(f"Skipping {col} col {coltime} lifetime {maxt}, seems to be on ray {ray}: {startingpat.rle_string_only}")
        continue

    #stopt = min(maxt, 1000+coltime)
    stopt = maxt
    print(f"Running {col} col {coltime} lifetime {maxt} to {stopt}: {startingpat.rle_string_only}")
    investigate(coltime, stopt, col, startingpat)
