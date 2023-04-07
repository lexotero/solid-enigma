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