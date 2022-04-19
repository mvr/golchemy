from os import path
import pickle

from golchemy.basics import *
from golchemy.schematic import *

class Collision:
    left: Reagent
    right: Reagent
    trans: Transform

if path.isfile("book.pickle"):
    with open(f"book.pickle", 'rb') as f:
        book = Book()
        book.reagents, book.table = pickle.load(f)

else:
    reagentfiles = ["reagents/ash.toml", "reagents/constellations.toml", "reagents/commonsmall.toml", "reagents/commonactive.toml", "reagents/notabledebris.toml",]
    book = Book.from_toml_object(toml.load(reagentfiles))
    with open(f"book.pickle", 'wb') as f:
         pickle.dump((book.reagents,book.table), f)

def find_ray(rays, coltime, col, pop):
    for candcoltime, origin, direction, period, raypop, _ in rays:
        if (coltime - candcoltime) % period != 0:
            continue
        raydist = (coltime - candcoltime) // period
        if raydist > 0 and pop == raypop and (direction ** raydist).inverse() * origin == col:
            return (candcoltime, origin, direction, raypop)

    return None
