from setuptools import setup

setup(
    name='canvas_api',
    version='0.1',
    py_modules=['canvas_api'], #find_packages(),
    #packages=['icutils'],
    include_package_data=True,
    install_requires=[
				'requests'
    ],
    test_suite='nose.collector',
    tests_require=['nose', 'mock'],
)

