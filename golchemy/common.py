from basics import *

nakedse = lt.pattern("bobo2b$o5b$bo2bob$3b3o!")

r = lt.pattern("b2o$2ob$bo!")
pi = lt.pattern("3o$obo$obo!")
century = lt.pattern("2b2o$3ob$bo!")
herschel = lt.pattern("2bo$2o$2bobo$4bo!")
bag = lt.pattern("2o2b$obob$2b2o!")
thunderbird = lt.pattern("3o2$bob$bob$bo!")
z = lt.pattern("2o$bo$bo$b2o!")
lom = lt.pattern("2o$b2o$2b2o!")
hook = lt.pattern("2o$b2o$2bo$3o!")
eheptomino = lt.pattern("2o$bo$3b2o$4bo!")
uturner = lt.pattern("o$o$o2$2o$2bo!")
octomino = lt.pattern("o$b5o!")
blip = lt.pattern("o$5o!")

iwona = lt.pattern("ob3o$2o!")
moth = lt.pattern("4bo$2b2o$bo$o$bo!")
lifelinek = lt.pattern("2bo$2bo$2bo$2o$o!")
hheptomino = lt.pattern("2o$2bo$3b2o$5bo!")
dove = lt.pattern("2b2o$bo2bo$o2bo$3o!")
b = lt.pattern("3bo$o2bo$b3o!")
fheptomino = lt.pattern("2o$bo$bo$b3o!")
blonktie = lt.pattern("$b2o$2bo2$2bobo$3bo!")
lifelinestable = lt.pattern("2o$o$2b3o!")

block = lt.pattern("2o$2o!")
blinker = lt.pattern("3o!").shift(-1, 0)
blonker = lt.pattern("o$o$o!").shift(0, -1)
tub = lt.pattern("bo$obo$bo!").shift(-1, -1)
pond = lt.pattern("b2o$o2bo$o2bo$b2o!")
hive = lt.pattern("b2o$o2bo$b2o!")
hove = lt.pattern("bo$obo$obo$bo!")
loafa = lt.pattern("bo$o$bobo$2bo!")
loafb = lt.pattern("2bo$bobo$o$bo!")
loafc = lt.pattern("bo$obo$3bo$2bo!")
loafd = lt.pattern("2bo$3bo$obo$bo!")
shipa = lt.pattern("bo$obo$b2o!")
shipb = lt.pattern("bo$obo$2o!")
shipc = lt.pattern("2o$obo$bo!")
shipd = lt.pattern("b2o$obo$bo!")

tee = lt.pattern("3o$bo!")
yee = lt.pattern("bo$bo$obo!")

glidersea = lt.pattern("bo$2bo$3o!")
gliderseb = lt.pattern("obo$b2o$bo!").shift(-1,-1)
glidersec = lt.pattern("2bo$obo$b2o!")
glidersed = lt.pattern("o$b2o$2o!").shift(-1,-1)

gliderswa = lt.pattern("bo$o$3o!").shift(0,-2)
gliderswb = lt.pattern("obo$2o$bo!").shift(-1,-1)
gliderswc = lt.pattern("o$obo$2o!").shift(0,-2)
gliderswd = lt.pattern("2bo$2o$b2o!").shift(-1, -1)

glidernwa = lt.pattern("3o$o$bo!")
glidernwb = lt.pattern("bo$2o$obo!").shift(-1,-1)
glidernwc = lt.pattern("2o$obo$o!")
glidernwd = lt.pattern("b2o$2o$2bo!").shift(-1, -1)

glidernea = lt.pattern("3o$2bo$bo!").shift(-2,0)
gliderneb = lt.pattern("bo$b2o$obo!").shift(-1,-1)
glidernec = lt.pattern("b2o$obo$2bo!").shift(-2,0)
gliderned = lt.pattern("2o$b2o$o!").shift(-1, -1)

halo = lt.pattern("5o$5o$5o$5o$5o!").shift(-2,-2)

patternmap = {
    'r': r,
    'pi': pi,
    'century': century,
    'herschel': herschel,
    'bag': bag,
    'thunderbird': thunderbird,
    'lom': lom,
    'z': z,
    'hook': hook,
    'eheptomino': eheptomino,
    'uturner': uturner,
    'octomino': octomino,
    'blip': blip,

    'iwona': iwona,
    'moth': moth,
    'lifelinek': lifelinek,
    'hheptomino': hheptomino,
    'dove': dove,
    'b': b,
    'fheptomino': fheptomino,
    'blonktie': blonktie,
    'lifelinestable': lifelinestable,

    'block': block,
    'blinker': blinker,
    'blonker': blonker,
    'tub': tub,
    'pond': pond,
    'hive': hive,
    'hove': hove,
    'tee': tee,
    'yee': yee,

    'glidersea': glidersea,
    'gliderseb': gliderseb,
    'glidersec': glidersec,
    'glidersed': glidersed,

    'gliderswa': gliderswa,
    'gliderswb': gliderswb,
    'gliderswc': gliderswc,
    'gliderswd': gliderswd,

    'glidernwa': glidernwa,
    'glidernwb': glidernwb,
    'glidernwc': glidernwc,
    'glidernwd': glidernwd,

    'glidernea': glidernea,
    'gliderneb': gliderneb,
    'glidernec': glidernec,
    'gliderned': gliderned,
}

def find_ray(rays, coltime, vec, pop):
    for candcoltime, origin, direction, period, raypop, _ in rays:
        if (coltime - candcoltime) % period != 0:
            continue
        raydist = (coltime - candcoltime) / period
        if raydist > 0 and pop == raypop and origin + raydist * direction == vec:
            return (candcoltime, origin, direction, raypop)
    return None
