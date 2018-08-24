Changes
=======

0.6 (2018-08-24)
----------------

- Add support for Python 3.4, 3.5, 3.6 and 3.7.

- Drop support for Python 2.6, 3.2 and 3.3.

- Add contributing.md and update docs. See
  https://github.com/Pylons/peppercorn/issues/13


0.5 (2014-09-29)
----------------

- Switch to an iterative parser rather than a recursive parser to avoid
  DoS attacks.

- Add the ``ignore`` operation. The subsequent data elements in the stream
  will be ignored until the corresponding ``__end__`` marker.  This feature
  is useful for form elements designed for client-side scripting, such as a
  "select all" checkbox in the middle of a list of other kinds of fields.

- Add support for Python 3.3.

- Drop support for Python 2.5 and Jython.


0.4 (2012-02-14)
----------------

- Drop support for Python 2.4.

- Add support for Python 3.2.

- Move project to GitHub.

- Switch to Pylons Project Sphinx theme.

- Add tox configuration.


0.3 (2010-09-02)
----------------

- 0.2 was a brownbag release. Handle the case where ``rename`` operation types
  may not have children.


0.2 (2010-09-02)
----------------

- Add new operation type: ``rename``.  ``rename`` begins a special mode.
  The value of the first subsequent data element in the stream will be
  used within its parent sequence or mapping. Any remaining data
  elements until the corresponding ``__end__`` marker are ignored.
  This is mostly in support of radio buttons.  See the ``rename`` docs
  within `https://docs.pylonsproject.org/projects/peppercorn/en/latest/
  <https://docs.pylonsproject.org/projects/peppercorn/en/latest/>`_ for more
  information.


0.1 (2010-03-23)
----------------

- Initial release.
