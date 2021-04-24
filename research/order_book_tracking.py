# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 18:13:47 2021

@author: Yasser
"""

###############################################################################

import os

import sys

import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..')))

# -----------------------------------------------------------------------------

import datetime as dt

# -----------------------------------------------------------------------------

import kraken_api as kr

import gateway as gw

###############################################################################


###############################################################################

gate = gw.Gateway()

db   = gw.DbConnections()

K    = kr.KrakenAPI()

###############################################################################


###############################################################################

if __name__ == "__main__":

    # -------------------------------------------------------------------------

    orderBookTrackingSql = \
        '''
        SELECT * FROM ORDER_BOOK_TRACKING
        '''

    orderBookTracking = gate.read_sql(orderBookTrackingSql, db.connect['TRADE_PROD'])

    # -------------------------------------------------------------------------

    if len(orderBookTracking) > float(2000000):

        sys.exit()

    else:

        snapShotDatetime = dt.datetime.now().strftime('%Y%m%d_%H%M%S')

        print(snapShotDatetime + ' : UPDATE')

        pair = 'XDGUSD'

        K.getOrderBook(pair, depth = 10)

        orderBook = K.orderBook

        orderBook[pair].keys()

        for direction in orderBook[pair].keys():

            orders = orderBook[pair][direction]

            for ix, entry in enumerate(orders):

                price  = entry[0]
                volume = entry[1]

                db.insert('TRADE_PROD',
                          'ORDER_BOOK_TRACKING',
                          {'PAIR'      : pair,
                           'DIRECTION' : direction ,
                           'DEPTH'     : ix,
                           'PRICE'     : price,
                           'VOLUME'    : volume})

        time.sleep(5 * 60)

###############################################################################



