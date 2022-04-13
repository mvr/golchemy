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

    def __sub__(self, other):
        return Vec(self.x - other.x, self.y - other.y)

    def __neg__(self):
        return Vec(-self.x, -self.y)

    def __rmul__(self, scale):
        return Vec(scale*self.x, scale*self.y)

    def __eq__(self, other):
        return (self.x == other.x and self.y == other.y)

    def as_tuple(self):
        return (self.x, self.y)

    def __repr__(self):
        return "Vec(%i, %i)" % self.as_tuple()

    def __hash__(self):
        return hash((self.x, self.y))

class BB:
    x : int
    y : int
    w : int
    h : int

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def __eq__(self, other):
        return (self.x == other.x and self.y == other.y and self.w == other.w and self.h == other.h)

    def contains(self,vec):
        return not (vec.x < self.x or
                    vec.x > self.x + self.w or
                    vec.y < self.y or
                    vec.y > self.y + self.h)

    def inflate(self, amount):
        if self.w == 0: return self
        return BB(self.x-amount, self.y-amount, self.w + 2 * amount, self.h + 2*amount)

    def overlaps(self,other):
        return not (self.x > other.x + other.w or
                    self.x + self.w < other.x or
                    self.y > other.y + other.h or
                    self.y + self.h < other.y)

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

    def __eq__(self, other):
        return (self.x == other.x and self.y == other.y)

    def __hash__(self):
        return hash((self.x, self.y))

    @overload
    def __mul__(self, other: Vec) -> Vec: ...
    @overload
    def __mul__(self, other: LinearTransform) -> LinearTransform: ...
    @overload
    def __mul__(self, other: Transform) -> Transform: ...
    @overload
    def __mul__(self, other: Pattern) -> Pattern: ...
    @overload
    def __mul__(self, other: Instance) -> Instance: ...

    def __mul__(self, other):
        if isinstance(other, Vec):
            return (other.x * self.x) + (other.y * self.y)

        if isinstance(other, LinearTransform):
            return LinearTransform(self * other.x, self * other.y)

        if isinstance(other, Transform):
            return Transform(self, Vec(0,0)) * other

        if isinstance(other, Pattern):
            return other.transform(self.name)

        if isinstance(other, Instance):
            return Transform(self, Vec(0,0)) * other

        raise TypeError("Cannot apply LinearTransform to " + str(type(other)))

    def __pow__(self, other):
        if other == 0:
            return Transform.id
        # TODO
        return self * (self ** (other-1))

    def inverse(self):
        if self.x == Vec(0, -1) and self.y == Vec(1, 0): return LinearTransform(Vec(0,1), Vec(-1,0))
        if self.x == Vec(0, 1)  and self.y == Vec(-1, 0): return LinearTransform(Vec(0,-1), Vec(1,0))
        return self

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

    @property
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

    def __repr__(self):
        return "%s(x=%r, y=%r)" % (self.__class__.__name__, self.x, self.y)

    @classmethod
    @property
    def id(cls):
        return LinearTransform(Vec(1, 0), Vec(0, 1))

    @classmethod
    @property
    def flip(cls):
        return LinearTransform(Vec(-1, 0), Vec(0, -1))

    @classmethod
    @property
    def rot90(cls):
        return LinearTransform(Vec(0, -1), Vec(1, 0))

    @classmethod
    @property
    def rot180(cls):
        return LinearTransform(Vec(-1, 0), Vec(0, -1))

    @classmethod
    @property
    def rot270(cls):
        return LinearTransform(Vec(0, 1), Vec(-1, 0))

    @classmethod
    @property
    def flip_x(cls):
        return LinearTransform(Vec(-1, 0), Vec(0, 1))

    @classmethod
    @property
    def flip_y(cls):
        return LinearTransform(Vec(1, 0), Vec(0, -1))

    @classmethod
    @property
    def swap_xy(cls):
        return LinearTransform(Vec(0, 1), Vec(1, 0))

    @classmethod
    @property
    def swap_xy_flip(cls):
        return LinearTransform(Vec(0, -1), Vec(-1, 0))

    @classmethod
    @property
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

    def __eq__(self, other):
        return (self.lin == other.lin and self.offset == other.offset)
    def __hash__(self):
        return hash((self.lin, self.offset))

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
            return Instance(other.reagent, other.time, self * other.trans, self * other.pattern)

        if isinstance(other, Schematic):
            s = Schematic()
            s.pattern = self * other.pattern
            s.reagents = [ self * r for r in other.reagents ]
            s.chaos = [ self * c for c in other.chaos ]
            return s

        raise TypeError("Cannot apply Transform to " + str(type(other)))

    def __pow__(self, other):
        if other == 0:
            return Transform.id
        # TODO
        return self * (self ** (other-1))

    @classmethod
    @property
    def id(cls):
        return Transform(LinearTransform.id, Vec(0, 0))

    def inverse(self):
        return Transform(self.lin.inverse(), -(self.lin.inverse() * self.offset))

    def __str__(self):
        return f"({self.offset} + {self.lin.name})"

    def __repr__(self):
        return "%s(lin=%r, offset=%r)" % (self.__class__.__name__, self.lin, self.offset)

    @classmethod
    def translate(cls, v):
        return Transform(LinearTransform.id, v)

# Monkey patching, sue me
def monkey_patch(cls):
  def update(extension):
    for k,v in extension.__dict__.items():
      if k != '__dict__':
        setattr(cls,k,v)
    return cls
  return update

# Only general purpose things
@monkey_patch(Pattern)
class PatternExt(Pattern):
    def translate(self, vec):
        return Transform.translate(vec) * self

    def coord_vecs(self) -> list[Vec]:
        return [Vec(x, y) for x,y in self.coords()]

    def touches(self, coords, margin=1):
        bb = self.bb
        if not bb.inflate(margin).contains(coords):
            return False

        x, y = coords.as_tuple()
        square = slice(x-margin,x+margin+1), slice(y-margin,y+margin+1) # Slices are not inclusive
        return not self[square].empty()

    @cached_property
    def first_on_coord(self):
        x,y,w,h = self.getrect()

        for i in range(x, x+w):
            if self[i, y] == 1:
                return Vec(i, y)

    @property
    def bb(self):
        if self.empty(): return BB(0,0,0,0)
        x,y,w,h = self.getrect()
        return BB(x,y,w,h)

    @property
    def top_left(self) -> Vec:
        if self.empty(): return Vec(0,0)
        x,y,_,_ = self.getrect()
        return Vec(x,y)

    def normalise_origin(self):
        first = self.first_on_coord
        return (self.shift(-first.x, -first.y), Transform.translate(first))

    def first_cluster(self):
        halo = "5o$5o$5o$5o$5o!"
        return self.component_containing(self.first_on_coord.as_tuple(), halo = halo)
        # return self.component_containing(halo = halo)

    # ripped from apgmera/includes/stabilise.h
    def overadvance_to_stable(self, security = 15) -> tuple[Pattern, int | None, int]:
        p = self

        t = 0
        depth = 0
        prevpop = 0
        currpop = 0
        period = 12

        candidate = self
        candidatetime = 0
        for i in range (0, 1000):
            if (i == 40 and security < 20):  security = 20
            if (i == 60 and security < 25):  security = 25
            if (i == 80 and security < 30):  security = 30

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
                candidate = p
                candidatetime = t
                period ^= 4

            prevpop = currpop;

            if depth == security:
                return (candidate, period, candidatetime)

        return (p, None, t)

    @cached_property
    def over_time_to_stable(self) -> int:
        _, period, t = self.overadvance_to_stable()
        if period == None:
            return None
        return t

    @cached_property
    def approximate_time_to_stable(self) -> int | None:
        _, period, t = self.overadvance_to_stable()

        if period == None:
            return None

        pops = []
        p = self
        for _ in range(0, t+period + period):
            p = p.advance(1)
            pops.append(p.population)

        pops.reverse()
        for i, pop in enumerate(pops):
            if pop != pops[i + period]:
                return t + period - i + 1

        return t + period

    # This is dumb, should expose RleWriter from lifelib
    @cached_property
    def rle_string_only(self) -> str:
        return ''.join(self.rle_string().splitlines()[2:])

    def zoi(self):
        inner = lt.pattern("3o$3o$3o!").shift(-1,-1)
        return self.convolve(inner)

    # Until I have proper gencols
    # Should be done using convolve
    def collisions_with(self, other):
        hits = self.zoi().convolve((LinearTransform.flip * other).zoi())
        overlaps = self.convolve(LinearTransform.flip * other)
        diff = hits - overlaps

        return set(diff.coord_vecs())

    def __repr__(self):
        if self.empty():
            return "Pattern()"

        x,y,_,_ = self.getrect()
        logdiam = self.lifelib('GetDiameterOfPattern', self.ptr)
        if logdiam <= 7:
            return f"Pattern(x={x}, y={y}, rle='{self.rle_string_only}')"
        else:
            return f"Pattern(x={x}, y={y}, logdiam={logdiam})"

    def fast_match_live(self, live):
        newptr = self.lifelib('MatchLive', self.ptr, live.ptr)
        return Pattern(self.session, newptr, self.owner)

    def fast_match(self, live, corona):
        newptr = self.lifelib('MatchLiveAndDead', self.ptr, live.ptr, corona.ptr)
        return Pattern(self.session, newptr, self.owner)

    @cached_property
    def symmetries(self) -> set[LinearTransform]:
        p, _ = self.normalise_origin()
        return { t for t in LinearTransform.all if self.invariant_under(t)}

    def invariant_under(self, trans):
        return self == (trans*self).normalise_origin()[0]

    @cached_property
    def symmetry_classes(self):
        # I am lazy
        seen = []
        result = set()
        for t in LinearTransform.all:
            tp = (t*self).normalise_origin()[0]
            if not tp in seen:
                result.add(t)
            seen.append(tp)
        return result

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
    pattern_rle: str
    pattern: Pattern
    origin_age: int
    phases: list | None
    # TODO track symmetry?

    def __init__(self, name, pattern, origin_age = 0):
        self.name = name
        self.pattern_rle = pattern
        self.pattern = lt.pattern(pattern)
        self.origin_age = origin_age
        self.phases = None
        self.fate = None

    def all_phases(self, endt = None) -> list[tuple[str, int, Transform]]:
        def all_orientations(pat):
            # TODO: handle symmetry
            return [ (n.unnormalised_wechsler, l.inverse() * tr)
                     for l in LinearTransform.all
                     for (n, tr) in [(l*pat).normalise_origin()] ]

        if endt == None: endt = self.time_for_ident

        p = self.pattern
        result = []
        for t in range(0, endt+1):
            result += [(w, t + self.origin_age, tr) for w, tr in all_orientations(p)]
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
            return Fate.OSC

        p = self.pattern
        p = p.advance(1)

        endt = self.pattern.approximate_time_to_stable
        for t in range(1, endt+1):
            if p.population == 0:
                return (Fate.BECOME, t, Schematic())
            if p in book:
                return (Fate.BECOME, t, Schematic().add_instance(book[p]))
            p = p.advance(1)
        return (Fate.OTHER, endt)
        # if self.oscillation:
        #     return (Fate.OSC,) + self.oscillation

        # p = self.pattern
        # p = p.advance(1)

        # endt = self.pattern.approximate_time_to_stable
        # for t in range(1, endt+1):
        #     if p.population == 0:
        #         return (Fate.DIE, t)
        #     if p in book:
        #         return (Fate.BECOME, t, book[p])
        #     p = p.advance(1)
        # return (Fate.OTHER, endt) # Puffers I guess?


    @cached_property
    def is_active(self) -> bool:
        if self.fate == Fate.OSC:
            return False
        if self.fate[0] == Fate.BECOME:
            return True
        if self.fate[0] == Fate.OTHER:
            return True

    @cached_property
    def time_to_fate(self) -> int:
        if self.fate == Fate.OSC:
            return 0
        if self.fate[0] == Fate.BECOME:
            return self.fate[1]
        if self.fate[0] == Fate.OTHER:
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
            if p.population <= 6:
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
        d = {'name': self.name, 'pattern': self.pattern, 'fate': self.fate }
        return "%s(%r)" % (self.__class__.__name__, d)

    def __getstate__(self):
        return {
            'name': self.name,
            'pattern_rle': self.pattern_rle,
            'origin_age': self.origin_age,
            'phases': self.phases,
            'fate': self.fate,
        }

    def __setstate__(self, pickled):
        self.__dict__ = pickled
        self.pattern = lt.pattern(self.pattern_rle)

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
        if not pattern:
            self.pattern = trans * reagent.pattern.advance(time)

        self.time = time
        self.trans = trans

    def step(self) -> tuple[Schematic, list[Event]]:
        new = Instance(self.reagent, self.time + 1, self.trans, self.pattern.advance(1))

        if self.time + 1 == self.reagent.time_to_fate and self.reagent.fate[0] == Fate.BECOME:
            before = Schematic().add_instance(self)
            after = self.trans * self.reagent.fate[2]
            return after, [Event(before, after)]
        else:
            return Schematic().add_instance(new), []

    def naive_advance(self, step):
        return Instance(self.reagent, self.time + step, self.trans, self.pattern.advance(step))

    def reconstruct(self) -> Pattern:
        return self.trans * self.reagent.pattern.advance(self.time)

    def verify(self):
        r = self.reconstruct()
        if self.pattern != r:
            print(f"instance    {self.pattern}")
            print(f"erroneously {r}")
            print(f"difference  {self.pattern ^ r}")

    def touches(self, coords, margin=1):
        self.pattern.touches(coords, margin)

    def collisions_with(self, other):
        return [Transform.translate(v) for v in self.pattern.collisions_with(other.pattern)]

    def all_orientation_collisions_with(self, other):
        return { tr * t for t in other.reagent.pattern.symmetry_classes for tr in self.collisions_with(t * other) }

    def __repr__(self):
        d = {'time': self.time, 'trans': self.trans}
        return "%s(%r, %r)" % (self.__class__.__name__, self.reagent.name, d)

    def __getstate__(self):
        return {
            'reagent': self.reagent,
            'time': self.time,
            'trans': self.trans,
        }

    def __setstate__(self, pickled):
        self.__dict__ = pickled
        self.pattern = self.reconstruct()

class FloodFill:
    def __init__(self):
        self.neighbours = {}

    def add_node(self, n):
        if n not in self.neighbours: self.neighbours[n] = set()

    def add_neighbourhood(self, o):
        for i in o:
            if i not in self.neighbours: self.neighbours[i] = set()
            self.neighbours[i].update(o)

    def groups(self):
        done = set()
        groups = []
        for n in self.neighbours:
            if n in done: continue
            # explore:
            group = set()
            stack = [n]
            while stack: # python why
                m = stack.pop()
                if m in done: continue
                group.add(m)
                done.add(m)
                stack += self.neighbours[m]
            groups.append(group)
        return groups

class Book:
    reagents : dict[str, Reagent]
    table : dict[str, Instance]

    def __init__(self):
        self.reagents = {}
        self.table = {}

    def add_reagent(self, reagent: Reagent):
        reagent.fate = reagent.determine_fate(self)
        self.reagents[reagent.name] = reagent
        for s, t, tr in reagent.all_phases():
            if s not in self.table:
                self.table[s] = Instance(reagent, t, tr.inverse())

    def __getitem__(self, pat: Pattern) -> Instance:
        v = pat.first_on_coord
        return Transform.translate(v) * self.table[pat.unnormalised_wechsler]

    def __contains__(self, pat):
        return pat.unnormalised_wechsler in self.table

    @classmethod
    def from_toml_object(cls, toml_dict):
        b = Book()
        for name, values in toml_dict.items():
            print(f"Adding {name}")
            b.add_reagent(Reagent(name, values['rle']))
        return b

class Event:
    ins: Schematic
    outs: Schematic

    def __init__(self, ins, outs):
        self.ins = ins
        self.outs = outs

    def __str__(self):
        return "%s(%s --> %s)" % (self.__class__.__name__, self.ins, self.outs)

    def __repr__(self):
        return "%s(ins=%r, outs=%r)" % (self.__class__.__name__, self.ins, self.outs)

class Schematic:
    pattern: Pattern
    reagents: list[Instance]
    chaos: list[Pattern]

    def __init__(self):
        self.pattern = lt.pattern()
        self.reagents = []
        self.chaos = []

    @classmethod
    def analyse(cls, book: Book, pattern: Pattern) -> Schematic:
        schematic = Schematic()
        schematic.pattern = pattern
        remaining = pattern
        while remaining.nonempty():
            c = remaining.first_cluster()
            if c in book:
                schematic.reagents.append(book[c])
            else:
                schematic.chaos.append(c)
            remaining = remaining - c
        return schematic

    def reconstruct(self) -> Pattern:
        return sum([i.reconstruct() for i in self.reagents], lt.pattern()) + sum(self.chaos, lt.pattern())

    def verify(self):
        for r in self.reagents:
            r.verify()

        r = self.reconstruct()
        if self.pattern != r:
            print(f"pattern     {self.pattern}")
            print(f"erroneously {r}")
            print(f"difference  {self.pattern ^ r}")

    def __add__(self, other):
        s = Schematic()
        s.pattern = self.pattern + other.pattern
        s.reagents = self.reagents + other.reagents
        s.chaos = self.chaos + other.chaos
        return s

    def add_instance(self, reagent):
        self.reagents.append(reagent)
        self.pattern += reagent.pattern
        return self

    def add_chaos(self, chaos):
        self.chaos.append(chaos)
        self.pattern += chaos
        return self

    def step(self, book: Book) -> tuple[Schematic, list]:
        # Let's refer to each instance/chaos by its first coord in the
        # original schematic. (theoretically, the stepped ones might
        # have identical first coord but I am struggling to think of
        # a situation where this is possible. seems rule specific)

        coordmap = {}
        for r in self.reagents:
            rstep = r.step()
            coordmap[r.pattern.first_on_coord] = (Cluster.REAGENT, r, rstep)
        for c in self.chaos:
            cstep = c.advance(1)
            coordmap[c.first_on_coord] = (Cluster.CHAOS, c, cstep)

        newpattern = self.pattern.advance(1)

        diff = sum(map(lambda v : v[2][0].pattern if v[0] == Cluster.REAGENT else v[2], coordmap.values()), lt.pattern()) ^ newpattern

        # if diff.empty():
        #     result = Schematic()
        #     result.pattern = newpattern
        #     events = []
        #     for tag, _, stepped in coordmap.values():
        #         if tag == Cluster.REAGENT:
        #             result += stepped[0]
        #             events += stepped[1]
        #         if tag == Cluster.CHAOS:
        #             s = Schematic.analyse(book, stepped)
        #             if len(s.chaos) > 0 and len(s.reagents) == 0:
        #                 result.chaos.append(stepped)
        #             else:
        #                 events.append(Event(Schematic().add_chaos(stepped), s))
        #                 result += s
        #     result.pattern = newpattern
        #     return result, events

        f = FloodFill()
        for k in coordmap.keys():
            f.add_node(k)
        for xy in diff.coord_vecs():
            neighbours = [ k for k, v in coordmap.items()
                           if (v[0] == Cluster.REAGENT and v[1].pattern.touches(xy))
                           or (v[0] == Cluster.CHAOS and v[1].touches(xy)) ] + \
                         [ xy ]

            f.add_neighbourhood(neighbours)
        # pairs = [(a, b) for a in coordmap.items() for b in coordmap.items()]
        # for (coord1, c1), (coord2, c2) in pairs:
        #     if coord1 == coord2: continue
        #     if c1[0] == Cluster.REAGENT or c2[0] == Cluster.REAGENT: continue
        #     if not c1[1].bb.inflate(1).overlaps(c2[1].bb.inflate(1)): continue

        #     if (c1[2].zoi() ^ c2[2].zoi()).nonempty():
        #         f.add_neighbourhood([coord1, coord2])

        result = Schematic()

        events = []
        groups = f.groups()

        for g in groups:
            if len(g) == 1:
                elem = list(g)[0]
                if not elem in coordmap: # a connecting pixel
                    continue
                o = coordmap[elem]
                if o[0] == Cluster.REAGENT:
                    r, es = o[2]
                    result.reagents += r.reagents
                    result.chaos += r.chaos
                    events += es
                if o[0] == Cluster.CHAOS:
                    chaos = o[2]
                    s = Schematic.analyse(book, chaos)
                    if len(s.chaos) > 0 and len(s.reagents) == 0:
                        result.chaos.append(o[2])
                    else:
                        events.append(Event(Schematic().add_chaos(chaos), s))
                        result += s

            else:
                ins = Schematic()
                for coord in g:
                    if not coord in coordmap: # a connecting pixel
                        continue
                    o = coordmap[coord]
                    if o[0] == Cluster.REAGENT:
                        ins.add_instance(o[1])
                    if o[0] == Cluster.CHAOS:
                        ins.add_chaos(o[1])

                outs = Schematic.analyse(book, ins.pattern.advance(1))
                result += outs
                events.append(Event(ins, outs))

        result.pattern = newpattern
        return (result, events)

    def naive_advance(self, step):
        s = Schematic()
        s.pattern = self.pattern.advance(step)
        s.reagents = [ r.naive_advance(step) for r in self.reagents ]
        s.chaos    = [ c.advance(step) for c in self.chaos ]
        return s

    def __str__(self):
        return ', '.join(
            [f"{r.reagent.name}[{r.time}]({str(r.trans)})" for r in self.reagents] + \
            [f"CHAOS({c.first_on_coord.x}, {c.first_on_coord.y})" for c in self.chaos]
            )

    def __repr__(self):
        d = {'reagents': self.reagents, 'chaos': self.chaos}
        return "%s(%r)" % (self.__class__.__name__, d)

    def __getstate__(self):
        return {
            'reagents': self.reagents,
            'chaos': [c.rle_string for c in self.chaos],
        }

    def __setstate__(self, pickled):
        self.__dict__ = pickled
        self.chaos = [ lt.pattern(c) for c in self.chaos]
        self.pattern = self.reconstruct()

class Timeline:
    reagents: list[tuple[Instance, int, int]]
    chaos: list[tuple[Pattern, int, int]]
    events: list

    def __init__(self, pattern):
        self.pattern = pattern

    @classmethod
    def analyse(cls, book: Book, pattern: Pattern):
        pass
