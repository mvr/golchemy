import sys

from golchemy.lab import *

rle = sys.argv[1]

p = lt.pattern(rle)
for t in range(1,100):
    if p in book:
        r = book[p]
        print(book[p])
        exit()
    p = p.advance(1)
