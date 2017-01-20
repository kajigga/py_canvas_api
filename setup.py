from setuptools import setup, find_packages

setup(
    name='canvas_api',
    version='0.1',
    packages=find_packages(),
    #packages=['icutils'],
    include_package_data=True,
    install_requires=[
				'requests'
    ],
)

