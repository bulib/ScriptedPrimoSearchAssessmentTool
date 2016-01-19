import spst
version = '0.8.0'
from distutils.core import setup

import sys
if sys.version_info < (3 , 0):
    print('Requires Python version 3.x')
del sys

try:
    import pymarc
except ImportError:
    install_requires.append('pymarc 3')
try:
    import marcx
except ImportError:
    install_requires.append('marcx')
try:
    import pandas
except ImportError:
    install_requires.append('pandas')
try:
    import codecs
except ImportError:
    install_requires.append('codecs')
try:
    import json
except ImportError:
    install_requires.append('json')
try:
    import time
except ImportError:
    install_requires.append('time')
try:
    import urllib
except ImportError:
    install_requires.append('urllib')
try:
    import itertools
except ImportError:
    install_requires.append('itertools')
try:
    import io
except ImportError:
    install_requires.append('io')

classifiers = """
Intended Audience :: Education
Intended Audience :: Developers
Intended Audience :: Information Technology
Intended Audience :: Librarians
License :: OSI Approved :: BSD License
Programming Language :: Python
Programming Language :: Python :: 3
Topic :: Text Processing :: General
Topic :: Discovery Services ::Assessment
"""

import spst

setup(
    name = 'spst',
    version = '1.0.0',
    author='Jack Ammerman',
    author_email='jwacooks@gmail.com',
    url='https://github.com/jwacooks/ScriptedPrimoSearchAssessmentTool',
    description='Automates Primo searches from a list of searches, storing the results in a Pandas dataframe.',
    classifiers = filter(None, classifiers.split('\n'))
    )

