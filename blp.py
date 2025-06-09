import pandas as pd
import numpy as np
from scipy.optimize import minimize
import scipy
from numba import jit, njit, prange
import time
import multiprocessing as mp
import pickle
from sklearn.linear_model import LinearRegression
import pyblp
