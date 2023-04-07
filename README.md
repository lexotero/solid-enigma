# Payment System

If you are here, you must know what this project is about so I'll safe you the details :)

The name of the repository is simply GitHub's suggestion, and I liked the cryptic looking
name.

## Getting started

This is a Python 3.10 project. I use `poetry` to manage dependencies and `poethepoet` for
project scripts.

To setup your dev environment you'll need Python 3.10 and `poetry`.

```shell
poetry install
```

After `poetry` creates the virtualenv and installs the dependencies, you should be able to
run the `poethepoet` tasks/scripts inside the venv. E.g.:

```
poe lint
poe unit
```

## User Interface

Although the modelling of the invoices and payments is implemented in `models.py` and 
tested in `tests/test_models.py`, I thought it would be a bit more fun to create a
really simple (and not too pretty) terminal-based UI. You can start it with:

```shell
python -m payment_system
```

NOTE#1 that the interface is pretty limited and is only meant to allow you to manually play
with the creation of invoices and different payments to cover different amounts of
any existing invoices.

NOTE#2 There is no data persistency layer, so once the process is finished (CTLR + C or
killed otherwise), all created payments and invoices will be lost.
