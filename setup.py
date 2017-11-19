#!/usr/bin/env python3

import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

__version__ = '0.2.0'

setup(name='difflame',
      version=__version__,
      description='difflame is a tool to visualise differences using flame graphs',
      author='witchard',
      author_email='witchard@hotmail.co.uk',
      url='https://github.com/witchard/difflame',
      download_url='https://github.com/witchard/difflame/tarball/' + __version__,
      py_modules=['difflame'],
      scripts=['difflame.py'],
      license='MIT',
      platforms='any',
      install_requires=['GitPython', 'grole'],
      keywords=['diff', 'flamegraph'],
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3',
                  ],
     )
