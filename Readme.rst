Laozi
-----

.. image:: ./docs/laozi_pic.jpg

Serialization library outputting a human-readable (and machine parseable)
log format. Mainly intended to be use in conjunction with SPLUNK and python
logging.


|pypi| |release| |downloads| |python_versions| |coverage| |pypi_versions| |actions|

.. |pypi| image:: https://img.shields.io/pypi/l/laozi
.. |release| image:: https://img.shields.io/librariesio/release/pypi/laozi
.. |downloads| image:: https://img.shields.io/pypi/dm/laozi
.. |python_versions| image:: https://img.shields.io/pypi/pyversions/laozi
.. |pypi_versions| image:: https://img.shields.io/pypi/v/laozi
.. |coverage| image:: https://codecov.io/gh/XayOn/laozi/branch/develop/graph/badge.svg
    :target: https://codecov.io/gh/XayOn/laozi
.. |actions| image:: https://github.com/XayOn/laozi/workflows/CI%20commit/badge.svg
    :target: https://github.com/XayOn/laozi/actions


Table of contents
=================

.. contents::
  :local:
  :depth: 3

.. _features:

Features
--------

Represent in a "key=value;" format the following supported types:

- String types
- Numeric types
- Classes with __dict__
- Dataclasses
- Sets
- Dicts
- Lists
- Objects with __repr__ (as a last resort, wont follow formatting)

Installation
------------

This is a python library available on pypi, just run

.. code:: bash

    pip install laozi

Make sure your python version is at least python3.8 and you're using that
version's pip.

Notes
------

I like :star:, star this project to show your appreciation! 


.. raw:: html

        <a href="https://github.com/XayOn/laozi/graphs/contributors">
          <img src="https://contributors-img.web.app/image?repo=XayOn/laozi" />
        </a>

Made with `contributors-img <https://contributors-img.web.app>`_
