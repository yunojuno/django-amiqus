# django-amiqus


Django app for integration with the Amiqus API.

The current version supports Django 3.2+/4.0+ and Python 3.8+.


## Background

Amiqus is an online identity verification service. We use this library to integrate with it.


## Installation

The project is available through PyPI as ``django-amiqus``:

```bash
$ pip install django-amiqus
```

## Tests

If you want to run the tests manually, install ``poetry``.

```bash
$ poetry install
$ poetry run pytest
```

If you are hacking on the project, please keep coverage up.

## Contributing

Standard GH rules apply: clone the repo to your own account, make sure you
update the tests, and submit a pull request.
