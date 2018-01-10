py_canvas_api
#############

The idea is to have a simple, easy to understand library for the Canvas API.

The Canvas API (https://canvas.instructure.com/doc/api/index.html) has hundreds of endpoints.

It seemed pointless to me to write a unique method for every one of them.
Instead, I created a class, called `ResterAPI` that uses `__getattr__` to
dynamically generate the path for an endpoint and `__call__` to add a path
element with a parameter. The `Canvas` class is built on top of `ResterAPI`.

The result is a fairly small library that can handle the vast majority of
Canvas API endpoints. 


Instantiate the Canvas object like this.

.. code-block:: py

  from canvas_api import Canvas
  c = Canvas('somedomain.instructure.com', CANVAS_ACCESS_TOKEN=os.getenv('ACCESS_TOKEN'))


Building paths
==============
You build the path appending "methods" after the instanted canvas_api object.

You will typically see a line like `GET /api/v1/accounts/:account_id/courses`
in the Canvas API documentation. This tells you what the path is and the inline
parameters it needs. You would build this path with the `py_canvas_api` library
like this: `c.accounts(8423).courses`. Don't worry about the `/api/v1` part.

The `py_canvas_api` library takes care of the path parameters like :user by taking
them as method arguments. For example, here is how you would get courses in the
account with the id of 10 using the path above.

.. code-block:: py

  # get a list of courses (paginated to 10) in the account
  accounts = c.accounts('self').courses.get().json()

Common Requests
================

GET
-----

To make a `GET` request, simply end with `get()`. This tells the library to
make a GET request. This library uses the awesome `Requests`_ library so the
return object in this case is simple a Response object. You will most often
want the response as a json object. You get this by calling .json() with the
Response.

.. code-block:: py

  # get a list of courses (paginated to 10) in the account
  accounts_json = c.accounts('self').courses.get().json()

If you need to send query parameters (key-value pairs added after a question
mark), add these as keyword parameters in the `get()` call. Let's say you want
a list of your own courses where you are a teacher and the enrollment is active. You would normally need to
add `?enrollment_type=teacher&enrollment_state=active` to the URL to do this. With the `py_canvas_api`
library, however, you would do it like this.

.. code-block:: py

  # get a list of courses (paginated to 10) in the account
  accounts_json = c.courses.get(enrollment_type='teacher', enrollment_state='active').json()

Here are several more `GET` examples.

.. code-block:: py

  # list of users
  users = c.accounts('self').users.get().json()

  # assignments in course with canvas id 23423
  assignments = c.courses(23423).assignments.get().json()

  # assignments in course with sis id ENG101
  assignments = c.courses('sis_course_id:ENG101').assignments.get().json()

  # list communication channels for user with id 82
  channels = c.users(82).communication_channels.get().json()

  # list own communication channels
  channels = c.users('self').communication_channels.get().json()

  # Get a list of all courses in the account. This will keep pulling results as
  # long as there are more pages. It uses generator functions to do this is a
  # smart way.
  accounts = c.accounts('self').course.get_paginated()

Special Cases
==============
There are a few unique cases that are addressed in special
classes. For example, the `SIS Import API`_ takes a file upload and needs
special handling.

Here is how to do an SIS Import.

.. code-block:: py

  from canvas_api import SISImporter
  sis_importer = SISImporter('somedomain.instructure.com', CANVAS_ACCESS_TOKEN=os.getenv('ACCESS_TOKEN'))
  sis_importer.do_sis_import(filepath)


.. _`SIS Import API`: https://canvas.instructure.com/doc/api/sis_imports.html

.. _`Requests`: http://docs.python-requests.org/en/master/
