import os
from setuptools import setup

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def readme():
  with open(os.path.join(BASE_DIR, 'README.rst')) as f:
    return f.read()

setup(
    name='py_canvas_api',
    version='0.2.0',
    description = 'A very small library for accessing the API for the Canvas LMS.',
    long_description = readme(),
    py_modules=['py_canvas_api', 'canvas_api'], 
    #download_url = 'https://github.com/kajigga/py_canvas_api',
    url = 'https://github.com/kajigga/py_canvas_api',
    keywords = ['canvaslms', 'api'],
    #packages=['icutils'],
    include_package_data=True,
    install_requires=[
				'requests'
    ],
    test_suite='nose.collector',
    tests_require=['nose', 'mock']
)
