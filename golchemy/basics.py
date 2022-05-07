from __future__ import annotations
from typing import overload
from functools import cached_property

import lifelib
from lifelib.pythlib.pattern import Pattern

sess = lifelib.load_rules("b3s23")
lt = sess.lifetree(n_layers=1)

class Vec:
    x : int
    y : int

    __slots__ = ['x', 'y']
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

    @property
    def taxicab_length(self):
        return abs(self.x) + abs(self.y)

class BB:
    x : int
    y : int
    w : int
    h : int

    __slots__ = ['x', 'y', 'w', 'h']
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

    def __hash__(self):
        return hash((self.x, self.y, self.w, self.h))

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

    __slots__ = ['x', 'y']
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

        return NotImplemented

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
    def symbol(self):
        table: dict[tuple[tuple[int, int], tuple[int, int]], str] = {
            ((1, 0), (0, 1)): "╛",
            ((0, -1), (1, 0)): "╖",
            ((-1, 0), (0, -1)): "╒",
            ((0, 1), (-1, 0)): "╙",
            ((-1, 0), (0, 1)): "╘",
            ((1, 0), (0, -1)): "╕",
            ((0, 1), (1, 0)): "╜",
            ((0, -1), (-1, 0)): "╓"
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

LinearTransform.id = LinearTransform(Vec(1, 0), Vec(0, 1))
LinearTransform.flip = LinearTransform(Vec(-1, 0), Vec(0, -1))
LinearTransform.rot90 = LinearTransform(Vec(0, -1), Vec(1, 0))
LinearTransform.rot180 = LinearTransform(Vec(-1, 0), Vec(0, -1))
LinearTransform.rot270 = LinearTransform(Vec(0, 1), Vec(-1, 0))
LinearTransform.flip_x = LinearTransform(Vec(-1, 0), Vec(0, 1))
LinearTransform.flip_y = LinearTransform(Vec(1, 0), Vec(0, -1))
LinearTransform.swap_xy = LinearTransform(Vec(0, 1), Vec(1, 0))
LinearTransform.swap_xy_flip = LinearTransform(Vec(0, -1), Vec(-1, 0))
LinearTransform.all = [LinearTransform(Vec(1, 0), Vec(0, 1)),
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

    __slots__ = ['lin', 'offset']
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

        return NotImplemented

    def __pow__(self, other):
        if other == 0:
            return Transform.id
        # TODO
        return self * (self ** (other-1))

    def inverse(self):
        return Transform(self.lin.inverse(), -(self.lin.inverse() * self.offset))

    def __str__(self):
        return f"({self.lin.name}, {self.offset})"

    def __repr__(self):
        return "%s(lin=%r, offset=%r)" % (self.__class__.__name__, self.lin, self.offset)

    @staticmethod
    def translate(v):
        return Transform(LinearTransform.id, v)

    def __getstate__(self):
        return (self.lin.x.x, self.lin.x.y, self.lin.y.x, self.lin.y.y, self.offset.x, self.offset.y)

    def __setstate__(self, pickled):
        self.lin = LinearTransform(Vec(pickled[0], pickled[1]), Vec(pickled[2], pickled[3]))
        self.offset = Vec(pickled[4], pickled[5])

Transform.id = Transform(LinearTransform.id, Vec(0, 0))

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
    halo1 = lt.pattern("3o$3o$3o!").shift(-1,-1)
    halo2 = lt.pattern("5o$5o$5o$5o$5o!").shift(-2,-2)

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
#        return self.top_left
        x, y = self.firstcell
        return Vec(x, y)

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

    @cached_property
    def centre_vec(self):
        bb = self.bb
        return Vec(bb.x + (bb.w // 2), bb.y + (bb.h // 2))

    def normalise_origin(self):
        first = self.first_on_coord
        return (self.shift(-first.x, -first.y), Transform.translate(first))


    def first_cluster(self, halo = halo2):
        return self.component_containing(self.first_on_coord.as_tuple(), halo)
        return self.component_containing(halo = halo)

    # ripped from apgmera/includes/stabilise.h
    def overadvance_to_stable(self, security = 15) -> tuple[Pattern, int | None, int]:
        p = self

        t = 0
        depth = 0
        prevpop = self.population
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
    def over_time_to_stable(self) -> int | None:
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
            pops.append(p.population)
            p = p.advance(1)

        pops.reverse()
        for i, pop in enumerate(pops[0:-period]):
            if pop != pops[i + period]:
                return t + period + period - i + 1

        return t + period + period + 1

    # This is dumb, should expose RleWriter from lifelib
    @cached_property
    def rle_string_only(self) -> str:
        return ''.join(self.rle_string().splitlines()[2:])

    def zoi(self):
        return self.convolve(PatternExt.halo1)

    # Until I have proper gencols
    def translation_collisions_with(self, other):
        hits = self.zoi().convolve((LinearTransform.flip * other).zoi())
        overlaps = self.convolve(LinearTransform.flip * other)
        diff = hits - overlaps

        return { Transform.translate(v) for v in diff.coord_vecs() }

    def all_orientation_collisions_with(self, other):
        return { tr * t for t in other.symmetry_classes for tr in self.translation_collisions_with(t * other) }

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
