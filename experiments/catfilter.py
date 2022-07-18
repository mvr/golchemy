import sys
from enum import Enum

from golchemy.lab import *

import pprint

# background = lt.pattern("x = 58, y = 63, rule = B3/S23\n21$22b2o$22b2o9$37bo$36bob2o$37b2o28$55b2o$55bobo!")
# foreground = lt.pattern("x = 40, y = 34, rule = B3/S23\n31$37b2o$36bo2bo$37b3o!")
background = lt.pattern()
foreground = lt.pattern()
correctiontransform = "identity"

maxtime = 150

standard_reagents = [
    'r',
    'b',
    'century',
    'dove',
    'e',
    # 'glider',
    'herschel',
    # 'herschelprime',
    'i',

    'blonktie',
    'pi',
    'queenbee',
    'r',
    'wing',
    'lom',
    'uturner',
    'honeyfarmer',
    'lwss',
    'mwss',
    'hwss',

    'octomino',
]
book.reagents['lwss'].notable = True


ptbfile = sys.argv[1]

def line_to_pat(line):
    line, _ = line.split(" ")
    line = line.replace("*", "o")
    line = line.replace("z", "o")
    line = line.replace("a", "o")
    line = line.replace("b", "o")
    line = line.replace(".", "b")
    line = line.replace("!", "$")
    return lt.pattern(line)

def get_patterns(filename):
    giant = lt.pattern(open(filename).read())
    if not giant:
        return

    cats = 1 + giant.getrect()[3] // 100
    print(f"{cats} rows total")

    donedigests = set()
    for i in range(0,cats):
        if (i % 50) == 0:
            pass
        print(f"Doing cat {i}")
        y = range(0 + i * 100, 100 + i * 100)
        row = giant[(range(0,100*1000),y)]
        columns = 1 + row.getrect()[2] // 100
        for j in range(0,columns):
            if j > 0 and (j % 200) == 0:
                pass
            x = range(0 + j * 100, 100 + j * 100)
            p = giant[(x,y)].shift(-j*100,-i*100)
            digest = p.digest()
            if digest in donedigests:
                print(f"Skipping entry {j}, already done")
                continue
            donedigests.add(digest)
            print(f"Doing entry {j}: {p.rle_string_only}")
            if (background - p).population > 0:
                print(p)
                print("did not match background")
            if p.population > 0:
                p2 = (p - background) + foreground
                yield p2.transform(correctiontransform)

def interpret_pattern(p):
    s = Schematic.analyse(book, p, generous=True)
    actives = list(filter(lambda i: i.reagent.is_active , s.reagents))
    if len(s.chaos) > 0:
        print(f"could not comprehend {p}")
        return s, None
    tr = actives[0].trans
    catalysts = s.copy()
    for a in actives:
        catalysts.reagents.remove(a)
        catalysts.pattern -= a.pattern
    return tr.inverse() * s, tr.inverse()*catalysts


class Reason(Enum):
    SINGLETON = 0
    SHOOTING = 1
    STANDARD = 2
    SURVIVING = 3
    SPECIAL = 4
    TRANSPARENT = 5
    GLIDER = 6

def is_interesting(s, catalysts):
    gliders = [r for r in s.reagents if r.reagent.name == 'glider']

    # for g in gliders:
    #     if g.trans.lin == LinearTransform.flip_x or g.trans.lin == LinearTransform.rot270:
    #         return Reason.GLIDER

    if len(s.chaos) == 0 and len(s.reagents) - len(catalysts.reagents) - len(gliders) <= 1:
        return Reason.SINGLETON

    if len(s.chaos) == 0 and len(s.reagents) - len(catalysts.reagents) - len(gliders) <= 3 \
       and any(i.reagent.name in standard_reagents for i in s.reagents):
        return Reason.STANDARD
    if any(i.reagent.name in standard_reagents and i.time > 30 for i in s.reagents):
        return Reason.SURVIVING
    if any(i.reagent.notable and not i in catalysts.reagents for i in s.reagents):
        return Reason.SPECIAL

    # if any(i.reagent.name in standard_reagents
    #        and i.trans.offset.taxicab_length > 25
    #        and i.time > 20
    #        for i in s.reagents):
    #     return Reason.SHOOTING

    # nonactives = [r for r in s.reagents if not r.reagent.is_active]
    activepart = s.copy()
    for g in gliders:
        activepart.reagents.remove(g)
        activepart.pattern -= g.pattern

    activebb = activepart.pattern.bb
    limit = 30

    if abs(activebb.x) > limit or \
       abs(activebb.x + activebb.w) > limit or \
       abs(activebb.y) > limit or \
       abs(activebb.y + activebb.h) > limit:
        return Reason.SHOOTING

    return None


goodpats = {}
data = {}
seen = []
def go():
    lastreason = None
    for p in get_patterns(ptbfile):
        s, catalysts = interpret_pattern(p)

        if not catalysts:
            continue
        orig = s.copy()
        catalystsborder = catalysts.pattern.zoi() - catalysts.pattern

        # if any(not i.reagent.name in boring_catalysts for i in catalysts.reagents):
        #     activedigest = catalysts.pattern.digest()
        #     output = [str(i) for i in catalysts.reagents]
        #     print(orig.pattern.rle_string_only, 0, Reason.SPECIAL.name, output)
        #     rles[activedigest] = [orig.pattern.rle_string_only]
        #     data[activedigest] = (0, Reason.SPECIAL.name, output)

        hasinteracted = False
        lastinteresting = None
        hasdestroyed = False
        destroyedrs = []
        hasreportedtrans = False
        reasons = set()
        for i in range(0, maxtime):
            if len(s.chaos) > 0:
                hasinteracted = True
            if not lastinteresting is None and lastinteresting != [i.reagent.name for i in s.reagents]:
                lastinteresting = None

            for c in catalysts.reagents:
                if c in destroyedrs:
                    continue
                if c.pattern.population < 10 and (c.pattern - s.pattern).population >= 4:
                    destroyedrs.append(c)
                    hasdestroyed = True

            reportable = hasinteracted \
               and (catalysts.pattern - s.pattern).empty() \
               and (catalystsborder & s.pattern).empty()

            shouldreport = reportable \
               and not (isinteresting := is_interesting(s, catalysts)) is None \
               and (lastinteresting is None or isinteresting != lastreason) \
               and not isinteresting in reasons

            if reportable and hasdestroyed and not hasreportedtrans:
                shouldreport = True
                isinteresting = Reason.TRANSPARENT
                hasreportedtrans = True

            if shouldreport:
                lastinteresting = [i.reagent.name for i in s.reagents]
                lastreason = isinteresting
                if isinteresting != Reason.STANDARD:
                    reasons.add(isinteresting)

                activedigest = (s.pattern - catalysts.pattern).digest()
                if isinteresting == Reason.TRANSPARENT:
                    destroyedpat = lt.pattern()
                    destroyedpat[-200,-200] = 1 # stupid hack to stop lifelib from shifting everything to the origin
                    for c in destroyedrs:
                        destroyedpat += c.pattern
                    activedigest = destroyedpat.digest()

                if activedigest in seen:
                    goodpats[activedigest].append(orig.pattern)
                    continue

                seen.append(activedigest)
                output = [str(i) for i in s.reagents if not i in catalysts.reagents]
                if len(s.chaos) > 0:
                    output += ["CHAOS"]
                if isinteresting == Reason.TRANSPARENT:
                    output = [str(i) for i in destroyedrs]
                print(orig.pattern.rle_string_only, i, isinteresting.name, output)
                goodpats[activedigest] = [orig.pattern]
                data[activedigest] = (i, isinteresting.name, output)

            s, es = s.step(book)
            s.normalise()

# import cProfile
# cProfile.run("go()", "profileout")

go()

print("writing summary")
pp = pprint.PrettyPrinter(indent=2)
with open(ptbfile+'filtered', 'w') as f:
    result = [([p.rle_string_only for p in goodpats[s]], data[s][0], data[s][1], data[s][2]) for s in seen]
    f.write(f"{pp.pformat(result)}")

print("writing groups")
total = lt.pattern()
j = 0
for s in seen:
    i = 0
    for p in goodpats[s]:
        total += p.shift(i*100 + 50, j*100 + 50)
        i += 1
    j += 1

with open(ptbfile+'groups', 'w') as f:
    f.write(total.rle_string())

# import pstats
# from pstats import SortKey

# with open("profileout.txt", "w") as f:
#     ps = pstats.Stats("profileout", stream=f)
#     ps.sort_stats(SortKey.CUMULATIVE)
#     ps.print_stats()
