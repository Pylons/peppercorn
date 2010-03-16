Peppercorn
==========

A library for converting a token stream into a data structure
comprised of sequences, mappings, and scalars, developed primarily for
converting HTTP form post data into a richer data structure.

Example "bare" usage:

.. code-block:: python

  >>> fields = [
  ... ('name', 'project1'),
  ... ('title', 'Cool project'),
  ... ('__start__', 'series:mapping'),
  ... ('name', 'date series 1'),
  ... ('__start__', 'dates:sequence'),
  ... ('__start__', 'date:sequence'),
  ... ('day', '10'),
  ... ('month', '12'),
  ... ('year', '2008'),
  ... ('__end__', 'date:sequence'),
  ... ('__start__', 'date:sequence'),
  ... ('day', '10'),
  ... ('month', '12'),
  ... ('year', '2009'),
  ... ('__end__', 'date:sequence'),
  ... ('__end__', 'dates:sequence'),
  ... ('__end__', 'series:mapping'),
  ... ]
   >>> from peppercorn import parse
   >>> return pprint.pprint(parse(fields))
   {'series':
     {'name':'date series 1',
      'dates': [['10', '12', '2008'], ['10', '12', '2009']]},
    'name': 'project1',
    'title': 'Cool project'}

A ``__start__`` token pushes a data structure onto the stack.  Its
value is composed of a name and a type, separated by a colon
(e.g. ``date:sequence``).  Two ``__start__`` token types exist:

- ``sequence``: begins a sequence.  Subsequent data elements will be
  added as positional elements in the sequence.

- ``mapping``: begins a mapping.  Subsequent data elements will be
  added as key/value pairs in the mapping.

A sequence or mapping is closed when the corresponding ``__end__``
token for its ``__start__`` token is processed.  Mappings and
sequences can be nested arbitrarily.  The value of an ``__end__``
tokens is optional; it is useful as documentation, but they are
not required by Peppercorn.

The data structure returned from :func:`peppercorn.fields` will always
be a mapping.

To use Peppercorn in a web application, create a form that has the
tokens in order.  For instance, the below form will generate the above
token stream:

.. code-block:: html

   <form>
     <input name="name"/>
     <input name="title/>
     <input type="hidden" name="__start__" value="series:mapping"/>
     <input name="name"/>
     <input type="hidden" name="__start__" value="dates:sequence"/>
     <input type="hidden" name="__start__" value="date:sequence"/>
     <input name="day"/>
     <input name="month"/>
     <input name="year"/>
     <input type="hidden" name="__end__"/>
     <input type="hidden" name="__start__" value="date:sequence"/>
     <input name="day"/>
     <input name="month"/>
     <input name="year"/>
     <input type="hidden" name="__end__"/>
     <input type="hidden" name="__end__"/>
     <input type="hidden" name="__end__"/>
   </form>

Then when the web post reaches the application, call the
:func:`peppercorn.parse` function with the ordered field pairs.  For a
:term:`WebOb` request, this means using the request's ``items``
method:

.. code-block:: python
   :linenos:

   fields = request.items()
   peppercorn.parse(fields)

The ``list`` attribute of a Python ``cgi.FieldStorage`` object can
also be used as a source of information:

.. code-block:: python
   :linenos:

   fields = []
   if fs.list:
       for field in fs.list:
           if field.filename:
               fields.append((field.name, field))
           else:
               fields.append((field.name, field.value))

   peppercorn.parse(fields)

.. toctree::
   :maxdepth: 2

   api.rst
   glossary.rst

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
