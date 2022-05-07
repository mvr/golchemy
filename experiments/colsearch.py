import sys

from golchemy.lab import *

import atexit
import pprint

# nakedse = lt.pattern("2o$obo$b2o!") # actually a boat

nakedse = lt.pattern("bobo2b$o5b$bo2bob$3b3o!")
nakedsefive = nakedse[5] # magic generation with a convenient blurred pattern to search for
magicpattern = lt.pattern("3o$obo$3o!")
magicpatterndead = lt.pattern("o").shift(1,1)

blurses = []
# blurdigests = set()
for orientation in LinearTransform.all:
    live = orientation * nakedsefive
    blur = live ^ live[2]

    halo = lt.pattern("5o$5o$5o$5o$5o!").shift(-2,-2)
    dead = blur.convolve(halo)
    corona = dead - blur
    coronaorigin = corona.top_left
    corona = corona.translate(-coronaorigin)
    blur   = blur.translate(-coronaorigin)
    blurses.append((blur, corona))
    # blurdigests.add(blur.digest())

activename = sys.argv[1]
activeoriginal = book.reagents[activename].pattern

targetname = sys.argv[2]
targetoriginal = None
if len(targetname.split("_")) == 3:
    name, x, y = targetname.split("_")
    name = name[:-1]
    single = book.reagents[name].pattern
    targetoriginal = single + single.shift(int(x),int(y))
else:
    targetoriginal = book.reagents[targetname].pattern

endt = 1150
if len(sys.argv) > 3:
    endt = int(sys.argv[3])

phase = 0
if len(sys.argv) > 4:
    phase = int(sys.argv[4])

if phase < 0:
    for i in range(0,-phase):
        activeoriginal = activeoriginal.advance(1)
if phase > 0:
    for i in range(0,phase):
        targetoriginal = targetoriginal.advance(1)

active = activeoriginal
target = targetoriginal

# activename = sys.argv[1]
# active = patternmap[activename]
# originalname = sys.argv[2]
# original = patternmap[originalname]

startmaxt = 1000000
if len(sys.argv) > 3:
    startmaxt = int(sys.argv[3])

# seenoctos = set()
# try:
#     with open("seenoctos.txt", 'r') as f:
#         seenoctos = eval(f.read())
# except FileNotFoundError:
#     pass
# try:
#     with open("seenash.txt", 'r') as f:
#         seenash = eval(f.read())
# except FileNotFoundError:
#     pass

winners = []

def find_se(collidetime, maxt, vec, pat):
    origpat = pat

    # result, _ , maxt = pat.overadvance_to_stable()
    # octo = result.octodigest()
    # if octo in seenoctos:
    #     print(f"Seen ash for {vec} at {maxt}")
    #     return

    twopre = pat.advance(collidetime)
    pre = twopre.advance(1)
    pat = pre.advance(1)

    # rseq = r.advance(collidetime + 2)
    # rseqdiff = pat ^ rseq
    # rsequence = r.advance(collidetime)
    # print(f"Trying {vec} to {maxt}")
    for t in range(collidetime+2, maxt):

        x = pat ^ twopre
        if x.fast_match(magicpattern, magicpatterndead) and any([x.fast_match(blur, corona) for blur, corona in blurses]):
            halfphases = 0
            while True:
                x = pat ^ twopre
                if not (x.fast_match(magicpattern, magicpatterndead) and any([x.fast_match(blur, corona) for blur, corona in blurses])):
                    break

                twopre = twopre.advance(48)
                pre = pre.advance(48)
                pat = pat.advance(48)

                halfphases += 1
            record = (vec, origpat.rle_string_only, t, halfphases)
            winners.append(record)
            print(f"Success for {vec} at time {t} for {halfphases} half-phases")

        twopre = pre
        pre = pat
        pat = pat.advance(1)
        # rseq = rseq.advance(1)


    # seenoctos.add(octo)
    # seenash.append([octo, vec, maxt])

def printresults():
    if len(winners) == 0: return
    pp = pprint.PrettyPrinter(indent=2)
    # with open("checkpoints.txt", 'w') as f:
    #     f.write(f"{pp.pformat(checkpoints)}")
    # print("wrote checkpoints")
    # with open("seenash.txt", 'w') as f:
    #     f.write(f"{seenash}")
    # with open("seenoctos.txt", 'w') as f:
    #     f.write(f"{seenoctos}")
    with open(f"{activename}-{targetname}-winners.txt", 'w') as f:
        f.write(f"{pp.pformat(winners)}")
    print("wrote winners")

atexit.register(printresults)

filecols = []
with open(f"cols/{activename}-{targetname}.txt", 'r') as f:
    filecols = eval(f.read())
# filecols.reverse()

with open(f"cols/{activename}-{targetname}-rays.txt", 'r') as f:
    rays = eval(f.read())

seenash = set()

for maxt, vec, coltime, rle in filecols:
    startingpat = active + target.translate(vec)

    if maxt == None:
        print(f"Success {vec} col {coltime}, did not stabilise: {rle}")
        record = (vec, rle, None, None)
        winners.append(record)
        continue

    if maxt > startmaxt: continue

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
    find_se(coltime, stopt, vec, lt.pattern(rle))
