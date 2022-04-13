import sys
import os.path
from os import path
import pickle

from basics import *
from common import *

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
active = Instance(book.reagents[activename], 0, Transform.id)

originalname = sys.argv[2]
original = Instance(book.reagents[originalname], 0, Transform.id)

endt = 1150
if len(sys.argv) > 3:
    endt = int(sys.argv[3])

phase = 0
if len(sys.argv) > 4:
    phase = int(sys.argv[4])

## Generating collisions
result = []
activeseq = active
for i in range(0,phase):
    original = original.step()[0].reagents[0]
target = original

done = set()

# TODO: put seenash back in

pops = {}
candidates = []

done.update(activeseq.pattern.convolve((LinearTransform.flip * target).pattern.zoi()).coord_vecs())
for t in range(0, endt):
    print(f"{activename}-{originalname}-{phase} gen {t}")
    newcols = activeseq.all_orientation_collisions_with(target) - done
    print(len(newcols))
    for col in newcols:
        pat = active.pattern + (col * original).pattern
        final, period, maxt = pat[t].overadvance_to_stable(security=50)
        maxt += t

        if period == None:
            result.append((None, col, t, pat.rle_string_only))
            continue

        finalpop = final[1024].population # just in case
        pops[(t, col)] = finalpop
        result.append((maxt, col, t, pat.rle_string_only))

        prevs = [
            # glider+still collision
            (Vec(1,1), 4),
            (Vec(-1,1), 4),
            (Vec(1,-1), 4),
            (Vec(-1,-1), 4),

            # perpendicular glider+glider collision
            (Vec(2, 0), 4),
            (Vec(-2, 0), 4),
            (Vec(0, 2), 4),
            (Vec(0, -2), 4),

            # lucky head on glider+glider collision
            (Vec(1, 1), 2),
            (Vec(-1, 1), 2),
            (Vec(1, -1), 2),
            (Vec(-1, -1), 2),

            # unlucky head on glider+glider collision
            (Vec(2, 2), 4),
            (Vec(-2, 2), 4),
            (Vec(2, -2), 4),
            (Vec(-2, -2), 4),
        ]
        for prev in prevs:
            tr = Transform.translate(-prev[0])
            prevind = (t - prev[1], tr * col)
            prevprevind = (t - prev[1] - prev[1], tr * tr * col)
            if prevind in pops and prevprevind in pops and pops[prevind] == finalpop and pops[prevprevind] == finalpop:
                existing = False
                for candcoltime, origin, direction, period, pop in candidates:
                    if (t - candcoltime) % period != 0:
                        continue

                    if pop == finalpop and (direction ** ((t - candcoltime) // period)).inverse() * origin == col:
                        existing = True
                        break
                if not existing:
                    newray = (t-prev[1]-prev[1], tr * tr * col, tr, prev[1], finalpop)
                    print(f"possible ray {newray}")
                    candidates.append(newray)


    done.update(newcols)
    done.update(activeseq.pattern.convolve((LinearTransform.flip * target).pattern.zoi()).coord_vecs())
    # done.update(activeseq.pattern.coord_vecs())
    activeseq = activeseq.step()[0].reagents[0]
    target = target.step()[0].reagents[0]

result = sorted(result, key=lambda x: -(x[0] or 1000000))

outname = ""
rayoutname = ""
if phase == 0:
    outname = f"cols/{activename}-{originalname}.txt"
    rayoutname = f"cols/{activename}-{originalname}-rays.txt"
else:
    outname = f"cols/{activename}-{originalname}-phase-{phase}.txt"
    rayoutname = f"cols/{activename}-{originalname}-rays-phase-{phase}.txt"

with open(outname, 'w') as f:
    pp = pprint.PrettyPrinter(indent=2)
    f.write(f"{pp.pformat(result)}")

counted = []
for candcoltime, origin, direction, period, pop in candidates:
    count = 0
    for t in range(0, 500):
        point = (candcoltime + t*period, (direction ** t).inverse() * origin)
        if point in pops and pops[point] == pop:
            count += 1
        else:
            break
    counted.append((candcoltime, origin, direction, period, pop, count))

counted = list(filter(lambda x: x[5] > 5, sorted(counted, key=lambda x: -x[5])))

with open(rayoutname, 'w') as f:
    pp = pprint.PrettyPrinter(indent=2)
    f.write(f"{pp.pformat(counted)}")
