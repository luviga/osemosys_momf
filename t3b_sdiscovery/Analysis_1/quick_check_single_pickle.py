# -*- coding: utf-8 -*-
"""
Created on Sun May 23 10:57:55 2021

@author: luisf
"""
import pickle
import os

all_files = os.listdir()

pickle_files = [f for f in all_files if 'pickle' in f]
pickle_file = open('prim_files_creator.pickle', 'rb')

pickle_dict = pickle.load(pickle_file)