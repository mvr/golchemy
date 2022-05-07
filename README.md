Golchemy
========

Setup
-----

```
git submodule update --init
curl -sSL https://install.python-poetry.org | python3 -
poetry install
poetry shell
```

Testing Collisions
------------------

```
python3 experiments/colgen.py herschel blinker 160
python3 experiments/timeline.py herschel blinker
```

Filtering Catforce Results
--------------------------

It will try to identify the active pattern, run the filter, put the results in `(inputfile)filtered`

```
python3 experiments/catfilter.py catforceout.rle
```

