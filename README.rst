Django Amiqus
==============

Django app for integration with the Amiqus API.

The current version supports Django 3.2+/4.0+ and Python 3.8+.


Background
----------

Amiqus is an online identity verification service. 
.. Amiqus is an online identity verification service. It provides API access to a
.. range of tests (identity, right to work, criminal history, credit check). It
.. is assumed that you are only interested in this project because you are
.. already aware of what Amiqus does, and so I won't repeat it here. If you want
.. to find out more, head over to their website.

.. If you *are* using Amiqus, and you are using Django, then this project can be
.. used to manage Amiqus checks against your existing Django users. It handles
.. the API interactions, as well as providing the callback webhooks required to
.. support live status updates.

.. Installation
.. ------------

.. The project is available through PyPI as ``django-amiqus``:

.. .. code::

..     $ pip install django-amiqus

.. Tests
.. -----

.. If you want to run the tests manually, install ``poetry``.

.. .. code::

..     $ poetry install
..     $ poetry run pytest

.. If you are hacking on the project, please keep coverage up.

.. Contributing
.. ------------

.. Standard GH rules apply: clone the repo to your own account, make sure you
.. update the tests, and submit a pull request.
