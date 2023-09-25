from __future__ import annotations
from typing import overload
from functools import cached_property

from lifelib.pythlib.pattern import Pattern

from golchemy.basics import *

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
    origin_age: int
    notable: bool
    # TODO track symmetry?

    def __init__(self, name, pattern, origin_age = 0, notable = False):
        self.name = name
        self.pattern_rle = pattern
        # self.pattern = lt.life(pattern)
        self.origin_age = origin_age
        self.notable = notable
        self.fate = None

    @cached_property
    def pattern(self):
        return lt.life(self.pattern_rle)

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def identifiable_phases(self, endt = None) -> Generator[list[tuple[str, int, Transform]]]:
        def all_orientations(pat):
            # TODO: handle symmetry
            return [ (n.digest(), l.inverse() * tr)
                     for l in LinearTransform.all
                     for (n, tr) in [(l*pat).normalise_origin()] ]

        if endt == None: endt = self.time_for_ident

        p = self.pattern
        hasgrown = False
        for t in range(0, endt+1):
            if p.population > 10:
                hasgrown = True
            if hasgrown and p.population <= 6:
                break
            if len(p.components(halo=Pattern.halo2)) == 1:
                for w, tr in all_orientations(p):
                    yield (w, t + self.origin_age, tr)
            p = p.advance(1)

    def sanity_check(self, pat, age, trans):
        assert(trans * self.pattern.advance(age) == pat)

    @cached_property
    def oscillation(self):
        o = self.pattern.oscar(eventual_oscillator=False, verbose=False, allow_guns=False)
        if 'period' in o:
            return (o['period'], Vec(o['displacement'][0], o['displacement'][1]))
        return None

    def determine_fate(self, book: Book):
        if self.oscillation:
            return Fate.OSC

        p = self.pattern
        # s = Schematic.analyse(book, p)

        endt = min(500, self.pattern.approximate_time_to_stable)
        # hasjoined = False
        for t in range(0, endt):
            # if (len(s.chaos) == 1 and len(s.reagents) == 0) or \
            #    (len(s.chaos) == 0 and len(s.reagents) == 1):
            #     hasjoined = True
            if p.population == 0:
                return (Fate.BECOME, t, Schematic())
            if p in book:
                return (Fate.BECOME, t, Schematic().add_instance(book[p]))
            # TODO: come back to this if we add something like "subinstances"
            # if hasjoined and len(s.chaos) == 0:
            #     return (Fate.BECOME, t, s)
            # s, _ = s.step(book)
            p = p.advance(1)

        # if not hasjoined:
        #     # We probably started as multiple identifiable islands:
        #     s = Schematic.analyse(book, p)
        #     if len(s.chaos) == 0:
        #         return (Fate.BECOME, 0, s)

        return (Fate.OTHER, self.pattern.approximate_time_to_stable)

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
        # if self.fate[0] == Fate.BECOME:
        #     return True
        # if self.fate[0] == Fate.OTHER:
        #     return True
        return True

    @cached_property
    def is_still(self) -> bool:
        return self.fate == Fate.OSC and self.oscillation[0] == 1

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
        t = 0
        # while len(p.components(halo)) == 1:
        #     p = p.advance(1)
        #     t += 1
        # return t
        split_duration = 0
        hasconnected = False
        hasgrown     = False
        while split_duration < 2 and t < self.pattern.approximate_time_to_stable:
            p = p.advance(1)
            t += 1
            components = len(p.components(Pattern.halo2))
            if components == 1:
                hasconnected = True
            if p.population > 10:
                hasgrown = True
            if hasgrown and p.population <= 6:
                return t
            if hasconnected and components != 1:
                split_duration += 1
            else:
                split_duration = 0
        return t

    @cached_property
    def time_for_ident(self):
        if self.oscillation:
            return self.oscillation[0] - 1

        # TODO: better idea: interval before stable where there is at
        # least one CHAOS
        return min(self.pattern.approximate_time_to_stable, 500)

    def __repr__(self):
        d = {'name': self.name, 'pattern': self.pattern, 'fate': self.fate }
        return "%s(%r)" % (self.__class__.__name__, d)

    def __getstate__(self):
        return (self.name,
                self.pattern_rle,
                self.origin_age,
                self.fate,
                self.is_active,
                self.oscillation,
                self.time_for_ident,
                self.notable)

    def __setstate__(self, pickled):
        attrs = ['name', 'pattern_rle', 'origin_age', 'fate', 'is_active', 'oscillation', 'time_for_ident', 'notable']
        self.__dict__.update(zip(attrs,pickled))

class Cluster:
    REAGENT = 0
    CHAOS = 1

class Instance:
    reagent : Reagent
    time : int
    trans : Transform

    def __init__(self, reagent, time, trans, pattern = None):
        self.reagent = reagent

        self.time = time
        self.trans = trans

        if not pattern is None:
            self.pattern = pattern

    def reconstruct(self) -> Pattern:
        return self.trans * self.reagent.pattern.advance(self.time)

    @cached_property
    def pattern(self):
        return self.reconstruct()

    def __eq__(self, other):
        return self.reagent == other.reagent and self.time == other.time and self.trans == other.trans

    def __hash__(self):
        return hash((self.reagent, self.time, self.trans))

    def __rmul__(self, other):
        return Instance(self.reagent, self.time, other * self.trans, other * self.pattern)

    def __copy__(self):
        return Instance(self.reagent, self.time, self.trans, self.pattern.__copy__());

    def step(self) -> tuple[Schematic, list[Event]]:
        new = Instance(self.reagent, self.time + 1, self.trans, self.pattern.advance(1))

        if self.time + 1 == self.reagent.time_to_fate and self.reagent.fate[0] == Fate.BECOME:
            before = Schematic().add_instance(self)
            after = self.trans * self.reagent.fate[2]
            return after, [Event(before, after)]
            # return after, 1
        else:
            # return Schematic().add_instance(new), 0
            return Schematic().add_instance(new), []

    def naive_advance(self, step):
        return Instance(self.reagent, self.time + step, self.trans, self.pattern.advance(step))

    def verify(self):
        r = self.reconstruct()
        if self.pattern != r:
            print(f"instance    {self.pattern}")
            print(f"erroneously {r}")
            print(f"difference  {self.pattern ^ r}")

    def touches(self, coords, margin=1):
        self.pattern.touches(coords, margin)

    def translation_collisions_with(self, other):
        return self.pattern.translation_collisions_with(other.pattern)


    def all_orientation_collisions_with(self, other):
        return self.pattern.all_orientation_collisions_with(other.pattern)

    def normalise(self):
        # TODO: do oscillators
        if self.reagent.is_still:
            self.time = 0

        # TODO: do orientation!!

    def __str__(self):
        return f"{self.reagent.name}[{self.time}].transform{str(self.trans)}"

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
    table : dict[str, tuple[str, int, Transform]]

    def __init__(self):
        self.reagents = {}
        self.table = {}

    def add_reagent(self, reagent: Reagent):
        reagent.fate = reagent.determine_fate(self)
        self.reagents[reagent.name] = reagent
        for s, t, tr in reagent.identifiable_phases():
            if s not in self.table:
                self.table[s] = (reagent.name, t, tr.inverse())

    def __getitem__(self, pat: Pattern) -> Instance:
        v = pat.first_on_coord
        name, time, tr = self.table[pat.digest()]
        return Transform.translate(v) * Instance(self.reagents[name], time, tr)

    def __contains__(self, pat):
        return pat.digest() in self.table

    def invent_still(self, pat):
        pat2, tr = pat.normalise_origin()
        o = pat2.oscar(eventual_oscillator=False, verbose=False, allow_guns=False)
        if not 'period' in o or o['period'] != 1:
            return None
        digest = pat2.digest()
        code = str(digest)
        r = Reagent(code, pat2.rle_string())
        self.add_reagent(r)
        return self[pat]

    @classmethod
    def from_toml_object(cls, toml_dict):
        b = Book()
        for name, values in toml_dict.items():
            print(f"Adding {name}")
            notable = 'notable' in values and values['notable']
            r = Reagent(name, values['rle'], notable = notable)
            b.add_reagent(r)
        return b

    def __getstate__(self):
        return {
            'reagents': self.reagents,
            'table': self.table
        }

    def __setstate__(self, pickled):
        self.__dict__ = pickled

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
        self.pattern = lt.life()
        self.reagents = []
        self.chaos = []

    # @cached_property
    # def pattern(self):
    #     return self.reconstruct()

    @classmethod
    def analyse(cls, book: Book, pattern: Pattern, generous = False) -> Schematic:
        schematic = Schematic()
        schematic.pattern = pattern
        remaining = pattern

        while remaining.nonempty():
            c = remaining.first_cluster()
            if c in book:
                schematic.reagents.append(book[c])
                remaining = remaining - c
                continue
            if generous:
                c2 = remaining.first_cluster(halo=Pattern.halostill)
                if c2 in book:
                    schematic.reagents.append(book[c2])
                    remaining = remaining - c2
                    continue
                cstill = book.invent_still(c2)
                if not cstill is None:
                    schematic.reagents.append(book[c2])
                    remaining = remaining - c2
                    continue

            schematic += Schematic.analyse_chaos(book, c)
            remaining = remaining - c
        return schematic

    # Need to separate blinkers/still lifes that are close
    # orthogonally/diagonally. a proper version of fullsep would be
    # better.
    @classmethod
    def analyse_chaos(cls, book: Book, pattern: Pattern) -> Schematic:
        justchaos = Schematic()
        justchaos.pattern = pattern
        justchaos.chaos = [pattern]

        nonactive_islands = []

        remaining = pattern
        while remaining.nonempty():
            c = remaining.first_cluster(halo = Pattern.halo1)
            if c in book:
                i = book[c]
                if not i.reagent.is_active:
                    nonactive_islands.append(i)
                else:
                    return justchaos
            else:
                return justchaos

            remaining = remaining - c

        if not 'period' in pattern.oscar(eventual_oscillator=False, verbose=False, allow_guns=False):
            return justchaos

        nonactive = Schematic()
        nonactive.pattern = pattern
        nonactive.reagents = nonactive_islands
        return nonactive

    def reconstruct(self) -> Pattern:
        return sum([i.reconstruct() for i in self.reagents], lt.life()) + sum(self.chaos, lt.life())

    def normalise(self):
        for i in self.reagents:
            i.normalise()

    def verify(self):
        for r in self.reagents:
            r.verify()

        r = self.reconstruct()
        if self.pattern != r:
            print(f"pattern     {self.pattern}")
            print(f"erroneously {r}")
            print(f"difference  {self.pattern ^ r}")

    def __eq__(self, other):
        return self.pattern == other.pattern and self.reagents == other.reagents and self.chaos == other.chaos

    def __add__(self, other):
        s = Schematic()
        s.pattern = self.pattern + other.pattern
        s.reagents = self.reagents + other.reagents
        s.chaos = self.chaos + other.chaos
        return s

    def __rmul__(self, other):
        s = Schematic()
        s.pattern = other * self.pattern
        s.reagents = [ other * r for r in self.reagents ]
        s.chaos = [ other * c for c in self.chaos ]
        return s

    def contains(self, other):
        return all(i in self.reagents for i in other.reagents)

    def add_instance(self, reagent):
        self.reagents.append(reagent)
        self.pattern += reagent.pattern
        return self

    def add_chaos(self, chaos):
        self.chaos.append(chaos)
        self.pattern += chaos
        return self

    def without_instance(self, reagent):
        s = self.copy()
        s.reagents.remove(reagent)
        s.pattern -= reagent.pattern
        return s

    def copy(self):
        s = Schematic()
        s.reagents = [r.__copy__() for r in self.reagents]
        s.chaos = [c.__copy__() for c in self.chaos]
        s.pattern = self.pattern.__copy__()
        return s

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

        diff = sum(map(lambda v : v[2][0].pattern if v[0] == Cluster.REAGENT else v[2], coordmap.values()), lt.life()) ^ newpattern

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
        # events = 0
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
                        # events += 1
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
                # events += 1

        result.pattern = newpattern
        return (result, events)

    def naive_advance(self, step):
        s = Schematic()
        s.pattern = self.pattern.advance(step)
        s.reagents = [ r.naive_advance(step) for r in self.reagents ]
        s.chaos    = [ c.advance(step) for c in self.chaos ]
        return s

    def noninteracting(self):
        if len(self.chaos) > 0 or len(self.reagents) == 1:
            return False
        return self.pattern.advance(1024) == self.naive_advance(1024).reconstruct()

    def to_list(self):
        return [f"{r.reagent.name}[{r.time}].transform{str(r.trans)}" for r in self.reagents] \
             + [f"CHAOS({c.first_on_coord.x}, {c.first_on_coord.y})" for c in self.chaos]

    def __str__(self):
        return 'Schematic(' + (', '.join(self.to_list())) + ')'

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
        self.chaos = [ lt.life(c) for c in self.chaos]
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
