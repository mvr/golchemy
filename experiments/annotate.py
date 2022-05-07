import sys

from golchemy.lab import *

creations = {}
deaths = {}

def collect_events(pat, stopt):
    s = Schematic.analyse(book, pat)

    for t in range(0, stopt):
        if t % 500 == 0:
            print(f"gen {t}", file=sys.stderr)
        s, es = s.step(book)

        for e in es:
            for r in e.outs.reagents:
                if r.reagent.is_active:
                    creations[(r.reagent.name, r.trans)] = (t, r)
            for r in e.ins.reagents:
                if r.reagent.is_active:
                    deaths[(r.reagent.name, r.trans)] = t

        # Need to deliberately not recognise the starting pattern
        if len(s.chaos) == 0 and len(s.reagents) == 1:
            s.chaos = [s.reagents[0].pattern]
            s.reagents = []
            continue

# orig = book.reagents['r'].pattern
# endt = 1104
orig = lt.pattern('o3b3o$3o2bo$bo!')
endt = 17331
collect_events(orig, endt)

print(orig.rle_string())
print(f"[[ LABELSIZE 32 ]]")
for (name, trans), (t, r) in creations.items():
    if (name, trans) in deaths:
        death = deaths[(name, trans)]
    else:
        death = endt
    # print(r, t, death)
    if death - t < 5: continue
    print(f"[[ LABELT {t-2} {death+2} 2 ]]")
    centre = r.pattern.centre_vec
    print(f"[[ LABEL {centre.x} {centre.y} 7 \"{name}\" ]]")
    bb = r.pattern.bb
    print(f"[[ POLYT {t+1} {t+2} 0 ]]")
    print(f"[[ POLYLINE {bb.x-0.5} {bb.y-0.5} {bb.x+bb.w-0.5} {bb.y-0.5} {bb.x+bb.w-0.5} {bb.y+bb.h-0.5} {bb.x-0.5} {bb.y+bb.h-0.5} {bb.x-0.5} {bb.y-0.5} 7 ]]")
