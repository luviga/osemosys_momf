# -*- coding: utf-8 -*-
"""
Created on Sat Aug 21 23:01:47 2021

@author: luisf
"""

import pickle

pickle_bau = pickle.load(open('cleanup_BAU.pickle', 'rb'))
pickle_ndp = pickle.load(open('cleanup_NDP.pickle', 'rb'))