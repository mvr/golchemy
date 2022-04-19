import sys
import os.path
from os import path

import toml
import pickle

from basics import *

if path.isfile("book.txt"):
    with open(f"book.txt", 'rb') as f:
        book = Book()
        book.reagents, book.table = pickle.load(f)

else:
    reagentfiles = ["reagents/ash.toml", "reagents/constellations.toml", "reagents/commonsmall.toml", "reagents/commonactive.toml", "reagents/notabledebris.toml", "reagents/pseudostill.toml"]
    book = Book.from_toml_object(toml.load(reagentfiles))
    with open(f"book.txt", 'wb') as f:
         pickle.dump((book.reagents,book.table), f)

rle = sys.argv[1]
p = lt.pattern(rle)
for t in range(1,100):
    if p in book:
        r = book[p]
        print(book[p])
        r.time = 0
        print(r.reconstruct())
        exit()
    p = p.advance(1)
