#! /usr/bin/env python
"""
The Landlab

:Package name: TheLandlab
:Version: 0.1.0
:Release date: 2013-03-24
:Authors:
  Greg Tucker,
  Nicole Gasparini,
  Erkan Istanbulluoglu,
  Daniel Hobley,
  Sai Nudurupati,
  Jordan Adams,
  Eric Hutton

:URL: http://csdms.colorado.edu/trac/landlab

:License: MIT
"""

from __future__ import absolute_import

__version__ = '0.1.0'

import os
if 'DISPLAY' not in os.environ:
    try:
        import matplotlib
    except ImportError:
        warnings.warn('matplotlib not found', ImportWarning)
    else:
        matplotlib.use('Agg')

from .model_parameter_dictionary import ModelParameterDictionary
from .framework.collections import Palette, Arena, NoProvidersError
from .framework.decorators import Implements, ImplementsOrRaise
from .framework.framework import Framework
from .grid import *
from .plot import *
from .model_component import Component

from .testing.nosetester import LandlabTester
test = LandlabTester().test
