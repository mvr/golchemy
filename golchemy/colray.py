from basics import *
import pprint

r = lt.pattern("b2o$2ob$bo!")
block = lt.pattern("2o$2o!")
blinker = lt.pattern("3o!").shift(-1, 0)
blonker = lt.pattern("o$o$o!").shift(0, -1)
tub = lt.pattern("bo$obo$bo!").shift(-1, -1)

filecols = []
with open("cols/r-block.txt", 'r') as f:
    filecols = eval(f.read())
filecols = sorted(filecols, key=lambda x: x[2])
# filecols.reverse()

points = {}
dummy = blinker
candidates = []
for maxt, vec, coltime, rle in filecols:
    finalpop = ((dummy.translate(vec) + r)[maxt+100]).population
    points[(vec, coltime)] = finalpop
    prevs = [
        (vec + Vec(1,1), coltime - 4),
        (vec + Vec(-1,1), coltime - 4),
        (vec + Vec(1,-1), coltime - 4),
        (vec + Vec(-1,-1), coltime - 4)
    ]
    for prev in prevs:
        if prev in points and points[prev] == finalpop:
            existing = False
            for candcoltime, origin, direction, pop in candidates:
                if (coltime - candcoltime) % 4 != 0:
                    continue

                if pop == finalpop and origin + ((coltime - candcoltime) / 4) * direction == vec:
                    existing = True
                    break
            if not existing:
                newray = (coltime-4, prev[0], vec - prev[0], finalpop)
                print(f"possible ray {newray}")
                candidates.append(newray)

counted = []
for candcoltime, origin, direction, pop in candidates:
    count = 0
    for t in range(0, 350):
        point = (origin + t * direction, candcoltime + t*4)
        if point in points and points[point] == pop:
            count += 1
    counted.append((candcoltime, origin, direction, pop, count))

counted = sorted(counted, key=lambda x: -x[4])

pp = pprint.PrettyPrinter(indent=2)
pp.pprint(counted)
