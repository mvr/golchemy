import sys

from basics import *
from common import *

import pprint

activename = sys.argv[1]
active = patternmap[activename]

originalname = sys.argv[2]
original = patternmap[originalname]

endt = 1150
if len(sys.argv) > 3:
    endt = int(sys.argv[3])

## Generating collisions
result = []
activeseq = active
target = original
done = set()

# TODO: put seenash back in

pops = {}
candidates = []

for t in range(0, endt):
    print(f"{activename}-generation {t}")
    newcols = activeseq.collisions_with(target) - done
    for col in newcols:
        pat = original.translate(col) + active
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
            prevind = (t - prev[1], col - prev[0])
            prevprevind = (t - prev[1] - prev[1], col - prev[0] - prev[0])
            if prevind in pops and prevprevind in pops and pops[prevind] == finalpop and pops[prevprevind] == finalpop:
                existing = False
                for candcoltime, origin, direction, period, pop in candidates:
                    if (t - candcoltime) % period != 0:
                        continue

                    if pop == finalpop and origin + ((t - candcoltime) / period) * direction == col:
                        existing = True
                        break
                if not existing:
                    newray = (t-prev[1]-prev[1], col - prev[0] - prev[0], prev[0], prev[1], finalpop)
                    print(f"possible ray {newray}")
                    candidates.append(newray)


    done.update(newcols)
    done.update(activeseq.coord_vecs())
    activeseq = activeseq.advance(1)
    target = target.advance(1)

result = sorted(result, key=lambda x: -(x[0] or 1000000))

with open(f"cols/{activename}-{originalname}.txt", 'w') as f:
    pp = pprint.PrettyPrinter(indent=2)
    f.write(f"{pp.pformat(result)}")

counted = []
for candcoltime, origin, direction, period, pop in candidates:
    count = 0
    for t in range(0, 500):
        point = (candcoltime + t*period, origin + t * direction)
        if point in pops and pops[point] == pop:
            count += 1
        else:
            break
    counted.append((candcoltime, origin, direction, period, pop, count))

counted = list(filter(lambda x: x[5] > 5, sorted(counted, key=lambda x: -x[5])))

with open(f"cols/{activename}-{originalname}-rays.txt", 'w') as f:
    pp = pprint.PrettyPrinter(indent=2)
    f.write(f"{pp.pformat(counted)}")
