"""
Configurability script module: Process which configures apache2.

Python package configuration

 -==========================================================================-
    Written for python 2.7 because it is included with Ubuntu 16.04 and I
      wanted to avoid requiring that python 3 also be installed.
 -==========================================================================-
"""

from distutils.core import setup

setup(
    name='configurability_apache2_process',
    version='0.3',
    url='https://github.com/1and1internet/',
    author='Brian Wojtczak',
    author_email='brian.wojtczak@1and1.co.uk',
    package_dir={
        'configurability_apache2_process': '.'
    },
    packages=[
        'configurability_apache2_process'
    ]
)
