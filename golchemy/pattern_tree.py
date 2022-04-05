from __future__ import annotations
from typing import overload
from functools import cached_property

import lifelib
from lifelib.pythlib.pattern import Pattern
import toml

sess = lifelib.load_rules("b3s23")
lt = sess.lifetree(n_layers=1)

class Vec:
    x : int
    y : int

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vec(self.x + other.x, self.y + other.y)

    def __neg__(self):
        return Vec(-self.x, -self.y)

    def __eq__(self, other):
        return (self.x == other.x & self.y == other.y)

    def as_tuple(self):
        return (self.x, self.y)

    def __repr__(self):
        return "Vec(%i, %i)" % self.as_tuple()

class LinearTransform:
    x : Vec
    y : Vec
    # lifelib applies these transformations such that the (0,0) cell
    # is transformed to (0,0)

    # Rotations are counter-clockwise

    # Magic codes from lifelib
    ID         = 228 # 0b11100100
    ROT90      = 141 # 0b10001101
    ROT180     = 27  # 0b00011011
    ROT270     = 114 # 0b01110010
    FLIPX      = 177 # 0b10110001
    FLIPY      = 78  # 0b01001110
    SWAPXY     = 216 # 0b11011000
    SWAPXYFLIP = 39  # 0b00100111

    def __init__(self, x, y):
        self.x = x
        self.y = y

    @overload
    def __mul__(self, other: Vec) -> Vec: ...
    @overload
    def __mul__(self, other: LinearTransform) -> LinearTransform: ...
    @overload
    def __mul__(self, other: Transform) -> Transform: ...
    @overload
    def __mul__(self, other: Pattern) -> Pattern: ...

    def __mul__(self, other):
        if isinstance(other, Vec):
            return Vec(self.x.x * other.x + self.y.x * other.x,
                       self.x.y * other.y + self.y.y * other.y)

        if isinstance(other, LinearTransform):
            return LinearTransform(self * other.x, self * other.y)

        if isinstance(other, Transform):
            return LinearTransform(self, Vec(0,0)) * other

        if isinstance(other, Pattern):
            return other.transform(self.name)

        raise TypeError("Cannot apply LinearTransform to " + str(type(other)))

    def inverse(self):
        return

    @property
    def name(self):
        table: dict[tuple[tuple[int, int], tuple[int, int]], str] = {
            ((1, 0), (0, 1)): "identity",
            ((0, -1), (1, 0)): "rot90",
            ((-1, 0), (0, -1)): "rot180",
            ((0, 1), (-1, 0)): "rot270",
            ((-1, 0), (0, 1)): "flip_x",
            ((1, 0), (0, -1)): "flip_y",
            ((0, 1), (1, 0)): "swap_xy",
            ((0, -1), (-1, 0)): "swap_xy_flip",
        }
        return table[(self.x.as_tuple(), self.y.as_tuple())]

    def lifeviewer_name(self):
        table: dict[tuple[tuple[int, int], tuple[int, int]], str] = {
            ((1, 0), (0, 1)): "IDENTITY",
            ((0, -1), (1, 0)): "RCCW",
            ((-1, 0), (0, -1)): "FLIP",
            ((0, 1), (-1, 0)): "RCW",
            ((-1, 0), (0, 1)): "FLIPX",
            ((1, 0), (0, -1)): "FLIPY",
            ((0, 1), (1, 0)): "SWAPXY",
            ((0, -1), (-1, 0)): "SWAPXYFLIP",
        }
        return table[(self.x.as_tuple(), self.y.as_tuple())]

    @classmethod
    def id(cls):
        return LinearTransform(Vec(1, 0), Vec(0, 1))

    @classmethod
    def all(cls):
        return [LinearTransform(Vec(1, 0), Vec(0, 1)),
                LinearTransform(Vec(0, -1), Vec(1, 0)),
                LinearTransform(Vec(-1, 0), Vec(0, -1)),
                LinearTransform(Vec(0, 1), Vec(-1, 0)),
                LinearTransform(Vec(-1, 0), Vec(0, 1)),
                LinearTransform(Vec(1, 0), Vec(0, -1)),
                LinearTransform(Vec(0, 1), Vec(1, 0)),
                LinearTransform(Vec(0, -1), Vec(-1, 0)),
                ]

class Transform:
    lin: LinearTransform
    offset: Vec

    # The linear transformation is applied first, and then the
    # translation, so (0, 0) is sent to (offset.x, offset.y)

    def __init__(self, lin, offset):
        self.lin = lin
        self.offset = offset

    @overload
    def __mul__(self, other: Vec) -> Vec: ...
    @overload
    def __mul__(self, other: LinearTransform) -> Transform: ...
    @overload
    def __mul__(self, other: Transform) -> Transform: ...
    @overload
    def __mul__(self, other: Pattern) -> Pattern: ...
    @overload
    def __mul__(self, other: Instance) -> Instance: ...

    def __mul__(self, other):
        if isinstance(other, Vec):
            return self.offset + (self.lin * other)

        if isinstance(other, LinearTransform):
            return Transform(self.lin * other, self.offset)

        if isinstance(other, Transform):
            return Transform(self.lin * other.lin,
                             self.offset + (self.lin * other.offset))

        if isinstance(other, PatternExt):
            return (self.lin * other).shift(self.offset.x, self.offset.y)

        if isinstance(other, Instance):
            return Instance(other.reagent, other.time, self * other.trans)

        raise TypeError("Cannot apply Transform to " + str(type(other)))

    def __neg__(self):
        return Transform(self.lin.inverse(), -self.offset)

    @classmethod
    def translate(cls, v):
        return Transform(LinearTransform.id(), v)

# Monkey patching, sue me
def open(cls):
  def update(extension):
    for k,v in extension.__dict__.items():
      if k != '__dict__':
        setattr(cls,k,v)
    return cls
  return update

# Only general purpose things
@open(Pattern)
class PatternExt(Pattern):
    def touches(self, coords):
        x, y = coords.as_tuple()
        square = slice(x-1,x+2), slice(y-1,y+2) # Slices are not inclusive
        return not self[square].empty()

    @cached_property
    def first_on_coord(self):
        cell = self.onecell()
        bb = cell.getrect()
        return Vec(bb[0], bb[1])

    def normalise_origin(self):
        first = self.first_on_coord
        return (self.shift(-first.x, -first.y), Transform.translate(-first))

    def first_cluster(self):
        halo = "5o$5o$5o$5o$5o!"
        return self.component_containing(halo = halo)

    # ripped from apgmera/includes/stabilise.h
    def overadvance_to_stable(self) -> tuple[Pattern, int, int]:
        p = self

        t = 0
        depth = 0
        prevpop = 0
        currpop = 0
        period = 12
        security = 15

        for i in range (0, 1000):
            if (i == 40):  security = 20
            if (i == 60):  security = 25
            if (i == 80):  security = 30

            if (i == 400): period = 18;
            if (i == 500): period = 24;
            if (i == 600): period = 30;

            t += period
            p = p.advance(period)

            currpop = p.population
            if currpop == prevpop:
                depth += 1
            else:
                depth = 0
                period ^= 4

            prevpop = currpop;

            if depth == security:
                return (p, period, t)

        raise RuntimeError("Pattern did not stabilise")

    @cached_property
    def approximate_time_to_stable(self) -> int:
        _, period, t = self.overadvance_to_stable()

        pops = []
        p = self
        for _ in range(0, t+period):
            p = p.advance(1)
            pops.append(p.population)

        pops.reverse()
        for i, pop in enumerate(pops):
            if pop != pops[i + period]:
                return t - i + 1

        return t + period

    # This is dumb, should expose RleWriter from lifelib
    @cached_property
    def rle_string_only(self) -> str:
        return self.rle_string().splitlines()[2]

    def __repr__(self):
        logdiam = self.lifelib('GetDiameterOfPattern', self.ptr)
        if logdiam <= 5:
            return ("Pattern(%r)" % self.rle_string_only)
        else:
            return ("Pattern(logdiam=%d)" % logdiam)

# My kingdom for a sum type
class Fate:
    DIE = 0
    OSC = 1
    BECOME = 2
    OTHER = 3

    def __init__(self):
        pass

    @classmethod
    def die(cls):
        pass

    @classmethod
    def stabilise(cls):
        pass

    @classmethod
    def become(cls):
        pass

class Reagent:
    name: str
    pattern: Pattern
    origin_age: int
    phases: list | None
    # TODO track symmetry?

    def __init__(self, name, pattern, origin_age = 0):
        self.name = name
        self.pattern = lt.pattern(pattern)
        self.origin_age = origin_age
        self.phases = None
        self.fate = None

    def all_orientations(self, pat):
        return [ (n.unnormalised_wechsler, tr * l)
                 for l in LinearTransform.all()
                 for (n, tr) in [(l*pat).normalise_origin()] ]

    def all_phases(self, endt = None) -> list[tuple[str, int, Transform]]:
        if endt == None: endt = self.time_for_ident

        p = self.pattern
        result = []
        for t in range(0, endt+1):
            result += [(w, t + self.origin_age, tr) for w, tr in self.all_orientations(p)]
            p = p.advance(1)
        return result

    def sanity_check(self, pat, age, trans):
        assert(trans * self.pattern[age] == pat)

    @cached_property
    def oscillation(self):
        o = self.pattern.oscar(eventual_oscillator=False, verbose=False)
        if 'period' in o:
            return (o['period'], Vec(o['displacement'][0], o['displacement'][1]))

    def determine_fate(self, book: Book):
        if self.oscillation:
            return (Fate.OSC,) + self.oscillation

        p = self.pattern
        p = p.advance(1)

        endt = self.pattern.approximate_time_to_stable
        for t in range(1, endt+1):
            if p.population == 0:
                return (Fate.DIE, t)
            if p in book:
                return (Fate.BECOME, t, book[p])
            p = p.advance(1)
        return (Fate.OTHER, endt) # Puffers I guess?


    @cached_property
    def time_to_fate(self) -> int:
        if self.fate[0] == Fate.OSC:
            return 0
        else:
            return self.fate[1]

    # Or pattern dies
    @cached_property
    def time_to_split(self) -> int:
        p = self.pattern
        # halo = "7o$7o$7o$7o$7o$7o$7o!"
        halo = "5o$5o$5o$5o$5o!"
        t = 0
        # while len(p.components(halo)) == 1:
        #     p = p.advance(1)
        #     t += 1
        # return t
        split_duration = 0
        while split_duration < 2 and t < self.pattern.approximate_time_to_stable:
            p = p.advance(1)
            t += 1
            if p.empty():
                return t
            if len(p.components(halo)) != 1:
                split_duration += 1
            else:
                split_duration = 0
        return t

    @cached_property
    def time_for_ident(self):
        if self.oscillation:
            return self.oscillation[0] - 1

        return min(self.pattern.approximate_time_to_stable, self.time_to_split-1)

    def __repr__(self):
        d = {'name': self.name }
        return "%s(%r)" % (self.__class__.__name__, d)

class Cluster:
    REAGENT = 0
    CHAOS = 1

class Instance:
    reagent : Reagent
    pattern : Pattern
    time : int
    trans : Transform

    def __init__(self, reagent, time, trans, pattern = None):
        self.reagent = reagent

        self.pattern = pattern
        if pattern == None:
            self.pattern = trans * reagent.pattern.advance(time)

        self.time = time
        self.trans = trans

    def step(self) -> tuple[Instance, list[Event]]:
        new = Instance(self.reagent, self.time + 1, self.trans, self.pattern.advance(1))

        if self.time + 1 == self.reagent.time_to_fate:
            return new, [Event(self.time + 1, [(Cluster.REAGENT, self)], [self.reagent.fate])]
        else:
            return new, []

    def reconstruct(self) -> Pattern:
        return self.trans * self.reagent.pattern.advance(self.time)

    def touches(self, coords):
        self.pattern.touches(coords)

    def __repr__(self):
        d = {'time': self.time, 'trans': self.trans}
        return "%s(%r, %r)" % (self.__class__.__name__, self.reagent.name, d)

class FloodFill:
    def __init__(self):
        self.neighbours = {}

    def add_neighbourhood(self, o):
        for i in o:
            if i not in self.neighbours: self.neighbours[i] = []
            self.neighbours[i] += o

    def groups(self):
        done = []
        groups = []
        for n in self.neighbours:
            if n in done: continue
            # explore:
            group = []
            stack = [n]
            while stack: # python why
                m = stack.pop()
                if m in done: continue
                group.append(m)
                done.append(m)
                stack += self.neighbours[m]
            groups.append(group)
        return groups

class Book:
    table : dict[str, Instance]

    def __init__(self):
        self.table = {}

    def add_reagent(self, reagent: Reagent):
        reagent.fate = reagent.determine_fate(self)
        for s, t, tr in reagent.all_phases():
            if s not in self.table:
                self.table[s] = Instance(reagent, t, tr)

    def __getitem__(self, pat) -> Instance:
        v = pat.first_on_coord
        return Transform.translate(v) * self.table[pat.unnormalised_wechsler]

    def __contains__(self, pat):
        return pat.unnormalised_wechsler in self.table

    @classmethod
    def from_toml_object(cls, toml_dict):
        b = Book()
        for name, values in toml_dict.items():
            b.add_reagent(Reagent(name, values['rle']))
        return b

class Event:
    time: int
    ins: list[tuple[int, Instance | Pattern]]
    outs: list[tuple[int, Instance | Pattern]]

    def __init__(self, time, ins, outs):
        self.time = time
        self.ins = ins
        self.outs = outs

class Schematic:
    pattern: Pattern
    reagents: list[Instance]
    chaos: list[Pattern]

    def __init__(self):
        self.pattern = lt.pattern()
        self.reagents = []
        self.chaos = []

    @classmethod
    def analyse(cls, book: Book, pattern: Pattern):
        schematic = Schematic()
        schematic.pattern = pattern
        remaining = pattern
        while remaining.nonempty():
            c = remaining.first_cluster()
            if c in book:
                schematic.reagents.append(book[c])
            else:
                schematic.chaos.append(c)
            remaining -= c
        return schematic

    def reconstruct(self) -> Pattern:
        return sum([i.reconstruct() for i in self.reagents], lt.pattern()) + sum(self.chaos, lt.pattern())

    def __add__(self, other):
        s = Schematic()
        s.pattern = self.pattern + other.pattern
        s.reagents = self.reagents + other.reagents
        s.chaos = self.chaos + other.chaos
        return s

    def step_chaos(self, pattern) -> tuple[Schematic, list]:
        pass

    def step(self, book: Book) -> tuple[Schematic, list]:
        # Let's refer to each instance/chaos by its first coord in the
        # original schematic. (theoretically, the stepped ones might
        # have identical first coord but I am struggling to think of
        # a situation where this is possible. seems rule specific)

        coordmap = {}
        for r in self.reagents:
            coordmap[r.pattern.first_on_coord] = (Cluster.REAGENT, r)
        for c in self.chaos:
            coordmap[c.first_on_coord] = (Cluster.CHAOS, c)

        newpattern = self.pattern.advance(1)

        diff = sum([r.pattern.advance(1) for r in self.reagents], lt.pattern()) + \
               sum([c.advance(1) for c in self.chaos], lt.pattern()) ^ newpattern

        f = FloodFill()
        for xy in diff.coords():
            neighbours = [ i[1].pattern.first_on_coord for i in newinstances if i[2].pattern.touches(xy) ] + \
                         [ c[1].first_on_coord for c in newchaos if newchaos[2].touches(xy) ]

            f.add_neighbourhood(neighbours)


        # newinstances = [ (REAGENT, r, r.step()) for r in self.reagents ]
        # newchaos = [ (CHAOS, c, c.advance(1)) for c in self.chaos ]

        result = Schematic()
        result.pattern = newpattern
        events = []
        for g in f.groups():
            if g.length == 1:
                o = coordmap[g[0]]
                if o[0] == Cluster.REAGENT:
                    r, es = o[1].step()
                    # At the moment assuming every reagent resolves to
                    # one thing. Could instead have it resolve a
                    # constellation.
                    result.reagents.append(r)
                    events += es
                if o[0] == Cluster.CHAOS:
                    r, es = self.step_chaos(o[1])
                    result += r
                    events += es
            else:
                # Multiple components have merged:
                pass

        return (result, events)

    def __repr__(self):
        d = {'reagents': self.reagents, 'chaos': self.chaos}
        return "%s(%r)" % (self.__class__.__name__, d)

class Timeline:
    reagents: list[tuple[Instance, int, int]]
    chaos: list[tuple[Pattern, int, int]]
    events: list

    def __init__(self, pattern):
        self.pattern = pattern

    @classmethod
    def analyse(cls, book: Book, pattern: Pattern):
        pass

# block = Reagent("block", "2o$2o!")
r = Reagent("r", "b2o$2ob$bo!")
# b = Reagent("b", "ob2o$3ob$bo!")
# century = Reagent("century", "2b2o$3ob$bo!")
# pi = Reagent("pi", "3o$obo$obo!")
# lwss = Reagent("lwss", "b2o$3o$2obo$b3o$2bo!")
# diehard = Reagent("diehard", "6bob$2o6b$bo3b3o!")
# flare = Reagent("flare", "b3o$o2bo$o2bo$2bo!")

# book = Book()
# book.add_reagent(flare)
# book.add_reagent(b)
# s = Schematic.analyse(book, lt.pattern("b2o$2ob$bo!").advance(30))
# print(s)

# block = lt.pattern("2o$2o!")
# r = lt.pattern("b2o$2ob$bo!")

# print(diehard.determine_fate(book))

# print(Book.from_toml_object(toml.load("reagents/commonsmall.toml")))
