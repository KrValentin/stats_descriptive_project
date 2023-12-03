# -*- coding: utf-8 -*-
"""
Module _init_ - projet de statistiques descriptives MACS3
@author: Kraemer Valentin 
"""
__date__ = "2023-11-27"
__version__ = '1.0'

import warnings
warnings.simplefilter(action='ignore', category=UserWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)

from .basic_func import *
from .manipulate_dataframe import *
from .plot_fun import *
from .manipulate_dask_dataframe import *

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os, glob
import scipy
import dask.dataframe as dd
from statsmodels.formula.api import ols
import re