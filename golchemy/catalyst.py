from lifelib.pythlib.pattern import Pattern

from golchemy.basics import *

class Catalyst:
    name: str
    pattern: Pattern
    recovery_time: int
    symmetry: StaticSymmetry
    symmetry_char: str
    period: int

    zoi: Pattern;
    required: Pattern
    locus: Pattern
    contact: Pattern
    forbidden: list[Pattern]

    transparent: bool
    must_include: bool
    check_recovery: bool
    check_reaction: bool
    sacrificial: bool
    can_smother: bool
    can_rock: bool

    def __init__(self, pat, recovery_time, period=None, zoi=None, required=None, locus = None, contact = None, must_include = False, check_recovery = False, check_reaction = False, sacrificial = False):
        self.pattern = pat
        if period is None:
            self.period = pat.period
        else:
            self.period = period
        self.recovery_time = recovery_time
        self.symmetry = StaticSymmetry.C1

        if zoi is None:
            self.zoi = lt.life()
            currentPat = self.pattern
            for _ in range(0, self.period):
                self.zoi |= currentPat.zoi()
                currentPat = currentPat.advance(1)
        else:
            self.zoi = zoi

        if required is None:
            self.required = lt.life()
        else:
            self.required = required

        if locus is None:
            self.locus = pat
        else:
            self.locus = locus

        if contact is None:
            self.contact = pat.zoi()
        else:
            self.contact = contact

        # TODO:
        self.forbidden = []

        self.transparent = (pat & required).empty()
        self.transparent_component = False
        for c in pat.components(Pattern.halostill):
            self.transparent_component |= (c & required).empty()

        self.must_include = must_include
        self.check_recovery = check_recovery
        self.check_reaction = check_reaction
        self.sacrificial = sacrificial

    @property
    def centre(self):
        return self.locus.bb.centre

    def is_suspect(self):
        return len((self.zoi - self.required).components(Pattern.halo2)) > 1 and (self.zoi - self.required).population < 10

    # Needs the patterns to be identical
    def merge(self, other):
        assert self.pattern == other.pattern
        recovery_time = max(self.recovery_time, other.recovery_time)
        required = self.required & other.required
        locus = self.locus | other.locus
        contact = self.contact | other.contact

        same_active_cells = (self.zoi - self.required) == (other.zoi - other.required)
        check_reaction = self.check_reaction and other.check_reaction and same_active_cells

        return Catalyst(self.pattern, recovery_time=recovery_time, required=required, locus=locus, contact=contact, check_reaction = check_reaction)
        # TODO: copy the attributes

    def increasing_interaction(self, other):
        selfactive = self.zoi - self.required
        otheractive = other.zoi - other.required
        for c in selfactive.components():
            if len((c & otheractive).components()) > 1:
                return False
            if (c & otheractive).empty():
                return False
        for c in otheractive.components():
            if (c & selfactive).empty():
                return False
        return True

    def merge_maybe(self, other):
        # if not self.increasing_interaction(other):
        #     return self
        same_active_cells = (self.zoi - self.required) == (other.zoi - other.required)
        if not same_active_cells:
            return self
        return self.merge(other)

    @classmethod
    def from_soup(cls, cat, soup, maxtime=200, stabletime=2):
        # Shift soup to match pattern (both period and location)
        period = cat.period
        for _ in range(0, period):
            tr = cat.transformation_to(soup)
            if tr is not None:
                soup = tr.inverse() * soup
                break
            soup = soup.advance(1)

        zoi = lt.life()
        currentCat = cat
        for _ in range(0, period):
            zoi |= currentCat.zoi()
            currentCat = currentCat.advance(1)

        alwaysPresent = cat
        everPresent = cat
        currentCat = cat
        for _ in range(0, period):
            alwaysPresent = alwaysPresent & currentCat
            everPresent = everPresent + currentCat
            currentCat = currentCat.advance(1)

        catHalo = everPresent.zoi() - everPresent

        required = zoi
        locus = lt.life()
        contact = lt.life()

        hasInteracted = False
        activatedTime = -1
        recoveredTime = -1
        absentFor = 0
        recoveredFor = 0
        recovered = False

        currentCat = cat
        currentSoup = soup
        soupAlone = soup - cat

        for n in range(maxtime):
            catPresent = (currentSoup & catHalo).empty() and alwaysPresent <= currentSoup
            required = required - (currentSoup ^ currentCat)
            if not catPresent and recoveredFor > 0:
                recoveredFor = 0
                absentFor += 1

            if hasInteracted and activatedTime == -1:
                # First activation
                locus += (currentSoup & catHalo).zoi() & currentCat
                contact += currentSoup ^ (soupAlone + currentCat)
                activatedTime = n

            if catPresent and hasInteracted: # present and has been activated.
                if recoveredFor == 0:
                    recoveredTime = n
                recoveredFor += 1

            if recoveredFor >= stabletime:
                recovered = True
                break

            currentCat = currentCat.advance(1)
            currentSoup = currentSoup.advance(1)

            if not hasInteracted:
                soupAlone = soupAlone.advance(1)

                if currentSoup != soupAlone + currentCat:
                    hasInteracted = True

        if not recovered:
            # Reached maxtime without proper recovery
            return None

        absence = recoveredTime - activatedTime + 1
        return Catalyst(cat,
                        period=period,
                        recovery_time=absence,
                        zoi=zoi,
                        required=required,
                        locus=locus,
                        contact=contact,
                        check_reaction=True)

    # mconcat
    @classmethod
    def from_soups(cls, cat, soups, merge_always=True):
        result = None
        while result is None:
            result = cls.from_soup(cat, soups.pop(0))
        for s in soups:
            newcat = cls.from_soup(cat, s)
            if newcat is None:
                continue
            if merge_always:
                result = result.merge(newcat)
            else:
                result = result.merge_maybe(newcat)
        return result

    @classmethod
    def from_history(cls, pat):
        pass # TODO

    def to_history(self):
        return (self.pattern - self.locus).as_state(1) + self.required.as_state(4) + (self.pattern & self.locus).as_state(9) + self.contact.as_state(2)

    def translation_placements_with(self, other):
        hits = self.reactmask.convolve(other)
        # overlaps = self.avoidmask.convolve(other)
        # diff = hits - overlaps
        return { Transform.translate(v) for v in hits.coord_vecs() }

    def all_orientation_placements_with(self, other):
        return { t * tr for t in self.pattern.symmetry_classes for tr in self.translation_placements_with(t.inverse() * other) }

    # TODO: out of date
    @classmethod
    def from_catforce(cls, s):
        chunks = s.split(' ')

        if chunks[0] != "cat":
            return None

        rle = chunks[1]
        recovery_time = int(chunks[2])
        x = int(chunks[3])
        y = int(chunks[4])
        sym = chunks[4]

        pat = lt.pattern(rle).shift(x, y)
        result = Catalyst(pat, recovery_time)
        result.symchar = sym

        pos = 6
        while pos < len(chunks):
            if chunks[pos] == "forbidden":
                rle = chunks[pos+1]
                x = int(chunks[pos+2])
                y = int(chunks[pos+3])
                pat = lt.pattern(rle).shift(x, y)
                result.forbidden.append(pat)
                pos += 4
            elif chunks[pos] == "required":
                rle = chunks[pos+1]
                x = int(chunks[pos+2])
                y = int(chunks[pos+3])
                pat = lt.pattern(rle).shift(x, y)
                result.required |= pat
                pos += 4
            elif chunks[pos] == "antirequired":
                rle = chunks[pos+1]
                x = int(chunks[pos+2])
                y = int(chunks[pos+3])
                pat = lt.pattern(rle).shift(x, y)
                result.required |= pat
                pos += 4
            elif chunks[pos] == "locus":
                rle = chunks[pos+1]
                x = int(chunks[pos+2])
                y = int(chunks[pos+3])
                pat = lt.pattern(rle).shift(x, y)
                result.locus = pat
                pos += 4
            elif chunks[pos] == "contact":
                rle = chunks[pos+1]
                x = int(chunks[pos+2])
                y = int(chunks[pos+3])
                pat = lt.pattern(rle).shift(x, y)
                result.contact = pat
                pos += 4
            elif chunks[pos] == "transparent":
                result.transparent = True
                pos += 1
            elif chunks[pos] == "mustinclude":
                result.mustInclude = True
                pos += 1
            elif chunks[pos] == "check-recovery":
                result.checkRecovery = True
                pos += 1
            elif chunks[pos] == "sacrificial":
                result.sacrificial = True
                pos += 1
            else:
                print("got " + chunks[pos])
                return None
        return result

    def to_catforce(self):
        pattern_position = self.pattern.bb.top_left - self.centre
        result = ""
        if self.name is not None:
            result += f"# {self.name}\n"
        result += f"cat {self.pattern.rle_string_only} {self.recovery_time} {pattern_position.x} {pattern_position.y} {self.symmetry_char}"
        if self.period != 1:
            result += f" period {self.period}"
        if not self.required.empty():
            required_position = self.required.bb.top_left - self.centre
            result += f" required {self.required.rle_string_only} {required_position.x} {required_position.y}"
        if not self.contact.empty():
            contact_position = self.contact.bb.top_left - self.centre
            result += f" contact {self.contact.rle_string_only} {contact_position.x} {contact_position.y}"
        if not self.locus.empty():
            locus_position = self.locus.bb.top_left - self.centre
            result += f" locus {self.locus.rle_string_only} {locus_position.x} {locus_position.y}"
        if self.transparent:
            result += f" transparent"
        if self.transparent_component or self.check_reaction:
            result += f" check-recovery"
        if self.check_reaction:
            result += f" check-reaction"
        if self.can_smother:
            result += f" can-smother"
        if self.can_rock:
            result += f" can-rock"
        return result

    @classmethod
    def from_toml_object(cls, name, toml_dict, merge_always=True):
        pat = lt.life(toml_dict["rle"])
        soups = list(map(lt.life, toml_dict["soups"]))
        c = Catalyst.from_soups(pat, soups, merge_always)
        c.name = name
        c.transparent = toml_dict.get("transparent", False)
        c.can_smother = toml_dict.get("can-smother", False)
        c.can_rock = toml_dict.get("can-rock", False)
        c.check_reaction = toml_dict.get("check-reaction", False)
        c.symmetry_char = toml_dict.get("symmetry-char", "*")
        return c

# required: green
# reactive: teal
# locus: yellow
# transient: blue
# antirequired: red
