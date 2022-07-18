import sys

from os import path
import pickle

from golchemy.basics import *
from golchemy.schematic import *

if path.isfile("bookgiant.pickle"):
    with open(f"bookgiant.pickle", 'rb') as f:
        book = pickle.load(f)

else:
    reagentfiles = ["reagents/ash.toml", "reagents/constellations.toml", "reagents/commonsmall.toml", "reagents/commonactive.toml", "reagents/notabledebris.toml", "reagents/sevencell.toml",  "reagents/catalysts.toml", "reagents/smallcensusall.toml",]
    book = Book.from_toml_object(toml.load(reagentfiles))
    with open(f"bookgiant.pickle", 'wb') as f:
         pickle.dump(book, f)


rle = sys.argv[1]

p = lt.pattern(rle)
last = "xxx"
print(rle)
for t in range(1,100):
    if p in book:
        r = book[p]
        if not r.reagent.name == last:
            print(f"Becomes {book[p]} at time {t}")
            last = r.reagent.name
    p = p.advance(1)

if last == "xxx":
    print("Unknown")
