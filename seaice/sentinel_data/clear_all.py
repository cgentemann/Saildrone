# -*- coding: utf-8 -*-
"""
Created on Thu Sep  7 06:57:22 2017

@author: SA01PH
"""
import os

def clear():
    '''clear the shell of the spider application
    use either clear() or cls()'''
    os.system('cls')
    return None
cls = clear

def clear_all():
    '''Clears all the variables from the workspace of the spider'''
    cls()
    gl = globals().copy()
    for var in gl:
        if var[0] == '_': continue
        if 'func' in str(globals()[var]): continue
        if 'module' in str(globals()[var]): continue

    del globals()[var]