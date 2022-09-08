import os
import sys
import intset
import subprocess

import lifelib

sess = lifelib.load_rules("b3s23")
lt = sess.lifetree(n_layers=1)

def rle_string_only(pat) -> str:
    return ''.join(pat.rle_string().splitlines()[2:])

def generate_soup(symmetry):
    base = lt.pattern()
    base[0:8,0:8] = 0.5

    result = base
    # if symmetry == "C2":
    #     result += base.transform("rot180").shift(16, -16)

    return result

def get_patterns(filename):
    donedigests = intset.IntSet()
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
            donedigests = donedigests.insert(digest)
            if p.population > 0:
                yield p.shift(-j*100,0)

sym = "C2"
while True:
    soup = generate_soup("C2")
    soup = soup.advance(10)
    print(f"Forcing soup: {rle_string_only(soup)}", file=sys.stderr)
    catfile = f"""
max-gen 100
last-gen 30
stable-interval 8
num-catalyst 2
# max-category-size 10
symmetry {sym}
pat {rle_string_only(soup)} 0 0
output catsoup.rle

cat 10b2o$5b2obo2bo$4bobob3o$4bobo$2b3ob5o$bo3bo4bo$b4o2bo$4bob2o$b2obo$2bobo$obob2o$2o! 20 -5 -5 + forbidden 2bo$3bo$b3o6b2o$5b2obo2bo$4bobob3o$4bobo$2b3ob5o$bo3bo4bo$b4o2bo$4bob2o$b2obo$2bobo$obob2o$2o! -5 -7 forbidden 3bo$bobo$2b2o6b2o$5b2obo2bo$4bobob3o$4bobo$2b3ob5o$bo3bo4bo$b4o2bo$4bob2o$b2obo$2bobo$obob2o$2o! -5 -7 forbidden 12b2o$2bo4b2obo2bo$obo3bobob3o$b2o3bobo$4b3ob5o$3bo3bo4bo$3b4o2bo$6bob2o$3b2obo$4bobo$2bobob2o$2b2o! -7 -5 forbidden 12b2o$bo5b2obo2bo$2bo3bobob3o$3o3bobo$4b3ob5o$3bo3bo4bo$3b4o2bo$6bob2o$3b2obo$4bobo$2bobob2o$2b2o! -7 -5 required 10b2o$11bo$8b3o$4bo$3b2ob5o$5bo4bo$3b2o2bo$4bob2o$2bobo$2bobo$obob2o$2o! -5 -5 antirequired 9bo$9b2o$10b2o$3b2o$3b2obob4o$6bo$4b2ob4o$6b2o$4bobo$2o2bobo$b2obobo$2bobo! -6 -6 locus 4b2o$3bobo$3bobo$b3obo$o3bo$4o! -4 -4

cat bo$obo$bo$2b3o$4bo! 10 -3 -3 * forbidden bo$obo$bo$2b3ob2o$4bobobo$7bo! -3 -3 required o$b3o$3bo! -2 -1 antirequired b4o$o3bo$3obo$2b3o! -2 -1 locus bo$o! -3 -3

# cat 3bo$2bobo$o2bo2bo$2obob2o$3bo3b2o$2obob2o2bo$2obo2bobo$4b2o2b2o$5bobo$5bobo$6bo! 20 -5 -6 * required 3bo$2bobo$o2bo2bo$2obob2o$3bo3b2o$5b2o2bo$6bobo$5bo2b2o$5bobo$5bobo$6bo! -5 -6 antirequired 3b2obo$4bobo$3obob3o$o3bo4b2o$6b2obo$3b2o3b2o$b6obo$8bo! -7 -4 locus 2o$2o! -5 -1

cat 2obo$2ob3o$6bo$2ob2obo$bob2ob2o$bo$2b3ob2o$4bob2o! 10 -3 -3 | forbidden 2bo$obo$b2o2$3b2obo$3b2ob3o$9bo$3b2ob2obo$4bob2ob2o$4bo$5b3ob2o$7bob2o! -6 -7 forbidden bo$2bo$3o2$3b2obo$3b2ob3o$9bo$3b2ob2obo$4bob2ob2o$4bo$5b3ob2o$7bob2o! -6 -7 forbidden 2bo$obo$b2o$4b2obo$4b2ob3o$10bo$4b2ob2obo$5bob2ob2o$5bo$6b3ob2o$8bob2o! -7 -6 forbidden bo$2bo$3o$4b2obo$4b2ob3o$10bo$4b2ob2obo$5bob2ob2o$5bo$6b3ob2o$8bob2o! -7 -6 forbidden 2obo$2ob3o$6bo$2ob2obo$bob2ob2o$bo$2b3ob2o$4bob2o$9b3o$9bo$10bo! -3 -3 forbidden 2obo$2ob3o$6bo$2ob2obo$bob2ob2o$bo$2b3ob2o$4bob2o$9b2o$9bobo$9bo! -3 -3 forbidden 2obo$2ob3o$6bo$2ob2obo$bob2ob2o$bo$2b3ob2o$4bob2o2$8b3o$8bo$9bo! -3 -3 forbidden 2obo$2ob3o$6bo$2ob2obo$bob2ob2o$bo$2b3ob2o$4bob2o2$8b2o$8bobo$8bo! -3 -3 required 3bo$3b3o$6bo$2ob2obo$bob2ob2o$bo$2b3o$4bo! -3 -3 antirequired 4b3o$6b2o$2b4obo$2bo2bobo$obo2bo$ob4o$2o$b3o! -3 -3 locus 2o$2o5$6b2o$6b2o! -3 -3

cat 2b2obo$3bob3o$bobo4bo$ob2ob2obo$o4bobo$b3obo$3bob2o! 10 -4 -3 x required 3bob3o$bobo4bo$ob2ob2obo$o4bobo$b3obo! -4 -2 antirequired 8bo$8b3o$6bob4o$b4obo3b3o$3obob4ob2o$2obo2bo2bob2o$2ob4obob3o$3o3bob4o$b4obo$2b3o$4bo! -6 -5 locus 2obo6$bob2o! -2 -3

cat 6b2ob2o$7bobo$2b2obo5bob2o$bobob2o3b2obobo$o6bobo6bo$7o3b7o2$2b3o7b3o$bo2bo3bo3bo2bo$b2o4bobo4b2o$7bobo$8bo! 20 -8 -6 + required 6b2ob2o$7bobo$2b2obo5bob2o$bobob2o3b2obobo$o15bo$3o11b3o2$2bo11bo$bo13bo$2bo11bo! -8 -6 antirequired 6b7o$6bo2bo2bo$2b6obob6o$b2o2bob5obo2b2o$2obobo2b3o2bobob2o$ob2ob2o2bo2b2ob2obo$o8bo8bo$5o3bobo3b5o$b2o4bo3bo4b2o$bobo11bobo$bo2b3o5b3o2bo$b6o5b6o$4b3o5b3o$9bo! -9 -7 locus bo$obo$obo$bo! -1 2 check-recovery

cat o2bobo2bo$4ob4o$4bo$2bo3b3o$2b4o2bo$6bo$2b4ob4o$2bo2bobo2bo! 12 -5 -3 / forbidden bo$obobo2bobo2bo$b2ob4ob4o$8bo$6bo3b3o$6b4o2bo$10bo$6b4ob4o$6bo2bobo2bo! -9 -4 forbidden o2bobo2bo$4ob4o$4bo$2bo3b3o$2b4o2bo$6bo$2b4ob4ob2o$2bo2bobo2bobobo$13bo! -5 -3 required 4ob4o$4bo$2bo3b3o$2b4o2bo$6bo$2b4ob4o! -5 -2
    """
    open("catsoup.in", "w").write(catfile)
    r = subprocess.run(["./CatForce", 'catsoup.in'], stdout=subprocess.DEVNULL)
    print(f"Piping soup: {rle_string_only(soup)}", file=sys.stderr)
    for p in get_patterns("catsoup.rle"):
        print(p.rle_string())
