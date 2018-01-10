py_canvas_api
=============

The idea is to have a simple, easy to understand library for the Canvas API.

The Canvas API (https://canvas.instructure.com/doc/api/index.html) has hundreds of endpoints.
It seemed pointless to me to write a unique method for every one of them.
Instead, I created a class, called `ResterAPI` that uses `__getattr__` to
dynamically generate the URLS for an endpoint and `__call__` to make the actual
request. The `Canvas` class is built on top of `ResterAPI`.

The result is a fairly small library that can handle the vast majority of
Canvas API endpoints. There are a few unique cases that are addressed in special
classes. For example, the `SIS Import API`_ takes a file upload and needs
special handling.

Here is how to do an SIS Import.

.. code-block:: py

  from canvas_api import SISImporter
  sis_importer = SISImporter('somedomain.instructure.com', CANVAS_ACCESS_TOKEN=os.getenv('ACCESS_TOKEN'))
  sis_importer.do_sis_import(filepath)


Instantiate the Canvas object like this.

.. code-block:: py

  from canvas_api import Canvas
  c = Canvas('somedomain.instructure.com', CANVAS_ACCESS_TOKEN=os.getenv('ACCESS_TOKEN'))
  # get a list of courses (paginated to 10) in the account
  accounts = c.accounts('self').courses.get()

  # Get a list of all courses in the account. This will keep pulling results as
  # long as there are more pages. It uses generator functions to do this is a
  # smart way.
  accounts = c.accounts('self').course.get_paginated()


.. _`SIS Import API`: https://canvas.instructure.com/doc/api/sis_imports.html
