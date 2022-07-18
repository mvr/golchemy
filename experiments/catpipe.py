import sys
import glob
import intset

import lifelib

sess = lifelib.load_rules("b3s23")
lt = sess.lifetree(n_layers=1)

def get_patterns(filename):
    giant = lt.pattern(open(filename).read())
    if not giant:
        return
    cats = 1 + giant.getrect()[3] // 100
    for i in range(0,cats):
        y = range(0 + i * 100, 100 + i * 100)
        row = giant[(range(0,100*1000),y)].shift(0,-i*100)
        columns = 1 + row.getrect()[2] // 100
        for j in range(0,columns):
            x = range(0 + j * 100, 100 + j * 100)
            p = row[x, range(0,100)]
            if p.population > 0:
                yield p.shift(-j*100,0)

g = sys.argv[1]

donedigests = intset.IntSet()
for fn in glob.glob(g):
    print(f"Piping file {fn}", file=sys.stderr)
    for p in get_patterns(fn):
        digest = p.digest()
        if digest in donedigests:
            continue
        donedigests = donedigests.insert(digest)
        print(p.rle_string())
