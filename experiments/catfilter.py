import sys

from golchemy.lab import *

import pprint

# background = lt.pattern("x = 58, y = 63, rule = B3/S23\n21$22b2o$22b2o9$37bo$36bob2o$37b2o28$55b2o$55bobo!")
# foreground = lt.pattern("x = 40, y = 34, rule = B3/S23\n31$37b2o$36bo2bo$37b3o!")
background = lt.pattern()
foreground = lt.pattern()

maxtime = 150

standard_reagents = [
    book.reagents['r'],
    book.reagents['b'],
    book.reagents['century'],
    book.reagents['dove'],
    book.reagents['e'],
    # book.reagents['glider'],
    book.reagents['herschel'],
    book.reagents['i'],

    book.reagents['blonktie'],
    book.reagents['pi'],
    book.reagents['queenbee'],
    book.reagents['r'],
    book.reagents['wing'],
    book.reagents['lom'],
    book.reagents['uturner'],
    book.reagents['honeyfarmer'],
    book.reagents['lwss'],
    book.reagents['mwss'],
    book.reagents['hwss'],
]

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

# def get_patterns():
#     for l in open(ptbfile).readlines():
#         yield line_to_pat(l)



def get_patterns():
    giant = lt.pattern(open(ptbfile).read())
    cats = giant.getrect()[3] // 100
    columns = giant.getrect()[2] // 100
    print(f"{cats} rows total")
    for i in range(0,cats):
        for j in range(0,columns):
            x = range(0 + j * 100, 100 + j * 100)
            y = range(0 + i * 100, 100 + i * 100)
            p = giant[(x,y)].shift(-j*100,-i*100)
            if (background - p).population > 0:
                print(p)
                print("did not match background")
            if p.population > 0:
                yield (p - background) + foreground

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

def is_interesting(s, catalysts):
    gliders = len([r for r in s.reagents if r.reagent.name == 'glider'])

    if len(s.reagents) - len(catalysts.reagents) - gliders == 0:
        return True
    if len(s.reagents) - len(catalysts.reagents) - gliders <= 2 \
       and all(i.trans.offset.taxicab_length >= 20 for i in s.reagents if not i in catalysts.reagents):
        return True
    if len(s.reagents) - len(catalysts.reagents) - gliders <= 3 \
       and any(i.reagent in standard_reagents for i in s.reagents):
        return True

    return False

lineno = 0
rles = {}
data = {}
seen = []
for p in get_patterns():
    s, catalysts = interpret_pattern(p)
    if not catalysts:
        continue
    orig = s.copy()

    if (lineno % 100) == 0:
        print(f"Doing line {lineno}")

    hasinteracted = False
    isinteresting = False
    for i in range(0, maxtime):
        s, es = s.step(book)
        s.normalise()

        if len(s.chaos) > 0:
            hasinteracted = True
            isinteresting = False

        if hasinteracted \
           and not isinteresting \
           and len(s.chaos) == 0 \
           and is_interesting(s, catalysts) \
           and (catalysts.pattern - s.pattern).population == 0:
            isinteresting = True
            activedigest = (s.pattern - catalysts.pattern).digest()
            if activedigest in seen:
                rles[activedigest].append(orig.pattern.rle_string_only)
                break
            seen.append(activedigest)
            output = [str(i) for i in s.reagents if not i in catalysts.reagents]
            print(orig.pattern.rle_string_only, i, output)
            rles[activedigest] = [orig.pattern.rle_string_only]
            data[activedigest] = (i, output)
    lineno += 1

pp = pprint.PrettyPrinter(indent=2)
with open(ptbfile+'filtered', 'w') as f:
    result = [(rles[s], data[s][0], data[s][1]) for s in seen]
    f.write(f"{pp.pformat(result)}")
