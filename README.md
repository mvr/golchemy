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

Running
-------

```
python3 experiments/colgen.py herschel blinker 160
python3 experiments/timeline.py herschel blinker
```

