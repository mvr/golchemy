import sys

from golchemy.lab import *

import pprint

import cProfile

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


done = set()


pops = {}
candidates = []

def overlaps(a, b):
    result = []
    for t in LinearTransform.all:
        translations = a.convolve((LinearTransform.flip * (t * b)).zoi()).coord_vecs()
        result += [Transform.translate(tr) * t for tr in translations]
    return result

result = []
done.update(overlaps(active, target))
for t in range(0, endt):
    print(f"{activename}-{targetname}-{phase} gen {t}")
    newcols = active.all_orientation_collisions_with(target) - done
    print(len(newcols))
    for col in newcols:
        pat = activeoriginal + (col * targetoriginal)
        final, period, maxt = pat[t].overadvance_to_stable()
        maxt += t

        if period == None:
            result.append((None, col, t, pat.rle_string_only))
            continue

        result.append((maxt, col, t, pat.rle_string_only))

        finalpop = pat[16384].population # just in case
        pops[(t, col)] = finalpop

        prevs = [
            # glider+still collision
            (Vec(1,1), 4),
            (Vec(-1,1), 4),
            (Vec(1,-1), 4),
            (Vec(-1,-1), 4),

            # perpendicular glider+glider collision
            # also *wss+still collision
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

            # head on glider+*wss collision
            (Vec(1, 3), 4),
            (Vec(-1, 3), 4),
            (Vec(1, -3), 4),
            (Vec(-1, -3), 4),
            (Vec(3, 1), 4),
            (Vec(-3, 1), 4),
            (Vec(3, -1), 4),
            (Vec(-3, -1), 4),
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
    done.update(overlaps(active, target))
    active = active.advance(1)
    target = target.advance(1)

result = sorted(result, key=lambda x: -(x[0] or 1000000))

outname = ""
rayoutname = ""
# if phase == 0:
#     outname = f"cols/{activename}-{targetname}-over.txt"
#     rayoutname = f"cols/{activename}-{targetname}-over-rays.txt"
# else:
#     outname = f"cols/{activename}-{targetname}-over-phase-{phase}.txt"
#     rayoutname = f"cols/{activename}-{targetname}-over-rays-phase-{phase}.txt"

if phase == 0:
    outname = f"cols/{activename}-{targetname}.txt"
    rayoutname = f"cols/{activename}-{targetname}-rays.txt"
else:
    outname = f"cols/{activename}-{targetname}-phase-{phase}.txt"
    rayoutname = f"cols/{activename}-{targetname}-rays-phase-{phase}.txt"

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

# cProfile.run("go()", "profileout")

# import pstats

# with open("profileout.txt", "w") as f:
#     ps = pstats.Stats("profileout", stream=f)
#     ps.sort_stats('time')
#     ps.print_stats()
