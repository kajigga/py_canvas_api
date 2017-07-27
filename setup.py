from setuptools import setup

setup(
    name='py_canvas_api',
    version='0.1.4',
    description = 'A very small library for accessing the API for the Canvas LMS.',
    py_modules=['canvas_api'], #find_packages(),
    download_url = 'https://github.com/kajigga/py_canvas_api/tree/0.1',
    keywords = ['canvaslms', 'api'],
    #packages=['icutils'],
    include_package_data=True,
    install_requires=[
				'requests'
    ],
    test_suite='nose.collector',
    tests_require=['nose', 'mock']
)
