from __future__ import annotations

from os import path
import pickle

from golchemy.basics import *
from golchemy.schematic import *

if path.isfile("book.pickle"):
    with open(f"book.pickle", 'rb') as f:
        book = Book()
        book.reagents, book.table = pickle.load(f)

else:
    reagentfiles = ["reagents/ash.toml", "reagents/constellations.toml", "reagents/commonsmall.toml", "reagents/commonactive.toml", "reagents/notabledebris.toml",]
    book = Book.from_toml_object(toml.load(reagentfiles))
    with open(f"book.pickle", 'wb') as f:
         pickle.dump((book.reagents,book.table), f)

class Collision:
    left: Reagent
    right: Reagent
    trans: Transform
    coltime: int
    phase: int # positive means advance right, negative means advance left

class Outcome:
    search_stop: int
    ash: Schematic | None
    time_to_ash: int | None
    finalpop: int | None
    notable: list[tuple[int, Schematic]]

class Ray:
    coltime: int
    origin: Vec
    direction: Vec
    period : int
    pop: int

    ray_directions = [
            # glider+still collision
            (Vec(1,1), 4),
            (Vec(-1,1), 4),
            (Vec(1,-1), 4),
            (Vec(-1,-1), 4),

            # perpendicular glider+glider collision
            # also *wss+still collision
            (Vec(2, 0), 4),
            (Vec(-2, 0), 4),
            (Vec(0, 2), 4),
            (Vec(0, -2), 4),

            # lucky head on glider+glider collision
            (Vec(1, 1), 2),
            (Vec(-1, 1), 2),
            (Vec(1, -1), 2),
            (Vec(-1, -1), 2),

            # unlucky head on glider+glider collision
            (Vec(2, 2), 4),
            (Vec(-2, 2), 4),
            (Vec(2, -2), 4),
            (Vec(-2, -2), 4),

            # head on glider+*wss collision
            (Vec(1, 3), 4),
            (Vec(-1, 3), 4),
            (Vec(1, -3), 4),
            (Vec(-1, -3), 4),
            (Vec(3, 1), 4),
            (Vec(-3, 1), 4),
            (Vec(3, -1), 4),
            (Vec(-3, -1), 4),
        ]

    def contains_collision(self, col):
        if (col.time - self.coltime) % self.period != 0:
            return False
        raydist = (col.time - self.coltime) // self.period
        if raydist > 0 and col.finalpop == self.pop and (self.direction ** raydist).inverse() * self.origin == col.trans:
            return True
        return False

def find_ray(rays, coltime, col, pop):
    for candcoltime, origin, direction, period, raypop, _ in rays:
        if (coltime - candcoltime) % period != 0:
            continue
        raydist = (coltime - candcoltime) // period
        if raydist > 0 and pop == raypop and (direction ** raydist).inverse() * origin == col:
            return (candcoltime, origin, direction, raypop)

    return None
