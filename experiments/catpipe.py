import os
import sys
import glob

import lifelib

sess = lifelib.load_rules("b3s23")
lt = sess.lifetree(n_layers=1)

def get_patterns(filename):
    donedigests = set()
    giant = lt.pattern(open(filename).read())
    if not giant:
        return
    cats = 1 + giant.getrect()[3] // 100
    for i in range(0,cats):
        y = range(0 + i * 100, 100 + i * 100)
        row = giant[(range(0,100*1000),y)].shift(0,-i*100)
        columns = 1 + row.getrect()[2] // 100
#         columns = min(columns, 10)
        for j in range(0,columns):
            x = range(0 + j * 100, 100 + j * 100)
            p = row[x, range(0,100)]
            digest = p.digest()
            if digest in donedigests:
                continue
            donedigests.add(digest)
            if p.population > 0:
                yield p.shift(-j*100,0)

bigZOI = lt.pattern()
bigZOI[-3:4, -3:4] = 1

def fix_wraparound(catalysts):
    pasted = \
        catalysts.shift(-64, -64) + catalysts.shift(0, -64) + catalysts.shift(64, -64) + \
        catalysts.shift(-64,   0) + catalysts               + catalysts.shift(64,   0) + \
        catalysts.shift(-64,  64) + catalysts.shift(0,  64) + catalysts.shift(64,  64)
    return pasted.component_containing(catalysts, bigZOI)

g = sys.argv[1]
files = glob.glob(g)
# files = list(filter(lambda fn: "full" not in fn, files))
total = len(files)
for i, fn in enumerate(files):
    print(f"Piping file {i}/{total}: {fn}", file=sys.stderr)
    for p in get_patterns(fn):
        p2 = fix_wraparound(p)
        print(p2.rle_string())
