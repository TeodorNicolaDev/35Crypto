# -*- coding: utf-8 -*-
"""
Created on Sun Mar 14 11:59:47 2021

@author: Yasser
"""

###############################################################################

import gateway as gw

###############################################################################


###############################################################################

gate = gw.Gateway()

db   = gw.DbConnections()

###############################################################################


###############################################################################

tableCreation = {
                'ORDER_BOOK_TRACKING' : {'fields'        : {'PAIR'      : 'VARCHAR(8)' ,
                                                            'DIRECTION' : 'VARCHAR(4)' ,
                                                            'DEPTH'     : 'INTEGER'    ,
                                                            'PRICE'     : 'VARCHAR(12)',
                                                            'VOLUME'    : 'VARCHAR(12)',
                                                            'UPDT_DTTM' : 'TIMESTAMP'},
                                        'database_name' : 'TRADE_PROD'},
                }

###############################################################################


###############################################################################

if __name__ == "__main__":

    for table_name in tableCreation.keys():

        db.createTable(tableCreation[table_name]['database_name'],
                       table_name,
                       tableCreation[table_name]['fields'],
                       override = False)

###############################################################################
