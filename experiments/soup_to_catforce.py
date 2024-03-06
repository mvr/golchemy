import sys
from golchemy.catalyst import *

def guess_stable(pat):
    result = lt.life()
    for c in pat.components(halo=Pattern.halo2):
        if c[1] == c:
            result += c
    return result

pat = lt.life(sys.argv[1])
cat = guess_stable(pat)

c = Catalyst.from_soup(cat, pat)
c.name = "New catalyst"
c.transparent = False
c.can_smother = False
c.can_rock = False
c.check_reaction = False
c.symmetry = c.pattern.symmetry
c.enforce_symmetry()

c.determine_forbidden()

print(c.to_catforce())
