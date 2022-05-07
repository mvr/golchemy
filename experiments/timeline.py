import sys
import atexit

from golchemy.lab import *

import pprint

# import cProfile

activename = sys.argv[1]
activeoriginal = book.reagents[activename].pattern

targetname = sys.argv[2]
if len(targetname.split("_")) == 3:
    name, x, y = targetname.split("_")
    name = name[:-1]
    single = book.reagents[name].pattern
    targetoriginal = single + single.shift(int(x),int(y))
else:
    targetoriginal = book.reagents[targetname].pattern

skipt = 0
if len(sys.argv) > 3:
    skipt = int(sys.argv[3])

phase = 0
if len(sys.argv) > 4:
    phase = int(sys.argv[4])

if phase > 0:
    targetoriginal = targetoriginal[phase]
if phase < 0:
    activeoriginal = activeoriginal[-phase]

active = activeoriginal
target = targetoriginal

# test = lt.pattern('5b2o$2bobo$o2bobobo$7bo$6b2o$2bo3bo$obo!')
# print(test.first_cluster())
# exit()

def is_reoccur(schematic):
    if any([r.reagent.name == activename and r.time > 50 and r.trans.lin.name not in ['rot90', 'rot180', 'rot270'] for r in schematic.reagents]): return True
    return False

interestingthing = True
def is_interesting(schematic):
    global interestingthing
    if any([r.reagent.notable for r in schematic.reagents]):
        if not interestingthing:
            interestingthing = True
            return True
    else:
        interestingthing = False

    gliders      = len([r for r in schematic.reagents if r.reagent.name == 'glider'])
    shortactives = len([r for r in schematic.reagents if r.reagent.is_active and r.time > 5])
    longactives  = len([r for r in schematic.reagents if r.reagent.is_active and r.time > 50])

    if (len(schematic.chaos) == 0 and
        len(schematic.reagents) - gliders <= 1): return True

    if (gliders >= 3 and
        len(schematic.chaos) == 0 and
        len(schematic.reagents) - gliders - longactives <= 1): return True

    if (len(schematic.chaos) == 0 and
        len(schematic.reagents) - gliders <= 3 and
        shortactives >= 1): return True
    if (len(schematic.chaos) == 0 and
        len(schematic.reagents) - gliders <= 5 and
        longactives >= 1): return True
    # if (len(schematic.reagents) - gliders <= 4
    #     and any([r.reagent.is_active and r.time > 100 for r in schematic.reagents])): return True

    return False

# print(book.reagents['r'])
# print(book.reagents['r'].time_for_ident)
# exit()
def check_chaos(s):
    for c in s.chaos:
        o = c.oscar(eventual_oscillator=False, verbose=False, allow_guns=False)
        if 'period' in o:
            print(f"Oops: thought {c.rle_string_only} was chaos" )

result = []

def investigate(coltime, stopt, col, pat):
    if coltime > 0:
        s = Schematic.analyse(book, pat.advance(coltime-1))
    else:
        s = Schematic.analyse(book, pat)
    interesting = True
    #reoccur = False
    startings = s

    for i in range(coltime, stopt+1):
        s, es = s.step(book)
        if s == startings.naive_advance(i):
            continue

        gliders = len([r for r in s.reagents if r.reagent.name == 'glider'])
        if len(s.reagents) - gliders > 10:
#            check_chaos(s)

            return interesting

        if interesting and len(es) > 0: # len(es) > 0:
            interesting = False
        if not interesting and is_interesting(s):
            interesting = True
            print(f"Success for {col} at time {i}: {s}")
            result.append((pat.rle_string_only, col, coltime, i, s))

        # if reoccur and not any([r.reagent.name == activename for r in s.reagents]):
        #     reoccur = False
        # if not reoccur and is_reoccur(s):
        #     reoccur = True
        #     print(f"Reoccur for {col} at time {i}: {s}")
        #     result.append((pat.rle_string_only, col, coltime, i, s))

        if len(s.reagents) <= 1 and len(s.chaos) == 0:
            return interesting

        # if len(s.chaos) == 0 and es > 0: # len(es) > 0:
        #     naive = s.naive_advance(1024)
        #     if naive.pattern == naive.reconstruct():
        #         if not interesting and is_interesting(naive):
        #             print(f"Success for {col} at time {i}: {s}")
        #             result.append((pat.rle_string_only, col, coltime, i, s))
        #         print(f"Bailing at time {i}: {s}")
                # break
#    check_chaos(s)
    return interesting


# investigate(54, 300,Vec(8, 15),lt.pattern('2b2o$3o$bo13$8b2o$8b2o!'))
# exit()


# print(book.reagents['iwona'].time_for_ident)
# exit()


done = set()

outname = ""
rayoutname = ""
reactionoutname = ""
if phase == 0:
    outname = f"cols/{activename}-{targetname}.txt"
    rayoutname = f"cols/{activename}-{targetname}-rays.txt"
    reactionoutname = f"results/{activename}-{targetname}-reactions.txt"
else:
    outname = f"cols/{activename}-{targetname}-phase-{phase}.txt"
    rayoutname = f"cols/{activename}-{targetname}-rays-phase-{phase}.txt"
    reactionoutname = f"results/{activename}-{targetname}-reactions-phase-{phase}.txt"

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
    humanresult = [ (rle, interestingtime, sch.to_list()) for rle, _, _, interestingtime, sch in result]
    with open(reactionoutname+'human', 'w') as f:
        f.write(f"{pp.pformat(humanresult)}")
    print("wrote reactions")

atexit.register(printresults)


seenash = set()


activeash = activeoriginal.advance(16384)
targetash = targetoriginal.advance(16384)
for maxt, col, coltime, rle in filecols:
    if maxt == None: continue
    if maxt < skipt: continue
    # if coltime == 0: continue

    startingpat = activeoriginal + col * targetoriginal
    ash = startingpat.advance(16384)


    # if col.offset.x < 0:
    #     print(f"Skipping {col} col {coltime} by symmetry: {startingpat.rle_string_only}")
    #     continue

    if ash == (activeash + col * targetash):
        print(f"No collision for {col} col {coltime}: {startingpat.rle_string_only}")
        continue

    d = ash.digest()
    if (col.lin, d) in seenash:
        print(f"Skipping {col} col {coltime} lifetime {maxt}, seems ash already: {startingpat.rle_string_only}")
        continue


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
    wasinteresting = investigate(coltime, stopt, col, startingpat)

    if not wasinteresting:
        seenash.add((col.lin, d))

# cProfile.run("go()", "profileout")

# import pstats

# with open("profileout.txt", "w") as f:
#     ps = pstats.Stats("profileout", stream=f)
#     ps.sort_stats('time')
#     ps.print_stats()
