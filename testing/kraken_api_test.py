# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 21:41:41 2021

@author: Yasser
"""

###############################################################################

import os

import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..')))

import kraken_api as kr

###############################################################################


###############################################################################

# TEST CASES ------------------------------------------------------------------

k = kr.KrakenAPI()

orderTest = {'pair'     :'XXLMUSD',
              'type'     :'sell',
              'ordertype':'limit',
              'price'    : '45' ,
              'volume'   :'25'}

k.placeOrder(orderTest)

###############################################################################

