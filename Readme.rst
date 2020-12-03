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
.. |coverage| image:: https://codecov.io/gh/XayOn/laozi/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/XayOn/laozi
.. |actions| image:: https://github.com/XayOn/laozi/workflows/CI%20commit/badge.svg
    :target: https://github.com/XayOn/laozi/actions


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

Examples
--------

.. code:: python

   @dataclass
   class Test:
       a: str = None
       b: str = None


   class Foo:
       def __init__(self):
           self.a = 1
           self.b = 2


   input_dict = {
       "foo": [1, 2],
       "bar": "3",
       "baz": [{
           "4": 5
       }],
       "stuff": {
           6: 7
       },
       "qu": {8, 9},
       "qux": Test(10, 11),
       'quu': 1.2,
       'qua': Decimal(1.2),
       'stux': Foo(),
       'foobar': b'123'
   }

   print(Laozi.parse(input_dict))

Results in a string like this:

.. code::

        foo.0=1; foo.1=2; bar="3"; baz.0.4=5; stuff.6=7; qu.0=8; qu.1=9; qux.a=10; qux.b=11; quu=1.2; qua=1.1999999999999999555910790149937383830547332763671875; stux.a=1; stux.b=2; foobar="b'123'"


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
