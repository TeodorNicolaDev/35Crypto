# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 13:54:58 2021

@author: Yasser
"""

###############################################################################

import os

import krakenex

import pandas as pd

import datetime as dt

###############################################################################


###############################################################################

class KrakenAPI(object):

    '''
    ###########################################################################

    KrakenAPI Class Documenation
    ----------


    ...

    Attributes
    ----------

        acctMsgTypeMap (dict)
            mapping of endpoints to public/private API

        balance (dict)
            current account balance at a currency level

        lastReturn (dict)
            last executed trade according to Kraken

        tradablePairs (dict)
            all tradable pairs and tradability parameters

        tradeBalance (dict)
            current account measures

        tradeHistory (pandas.core.frame.DataFrame)
            log of historically executed transactions

    Methods
    ----------

        calcDateFromTimestamp(timestamp)
            converts string timestamp to %Y-%m-%d formatted string date

        fillOrder(row)
            helper method used to calculate how an order would be filled across the top of the order book versus multiple price levels

        getBalance()
            source current account balance at a currency level

        getBestPrice(pair, direction, quantity)
            calculate the estimated market order price based on the best available trade in the order book *accounts for Kraken transaction cost*

        getOrderBook(pair, depth)
            source current order book for a given currency pair

        getTradablePairs()
            source all tradable pairs and tradability parameters

        getTradeBalance()
            source current account measures, this includes but is not limited to total trade balance, free margin, float valuation, etc.

        getTradeHistory()
            source log of historically executed transactions

        loanAPIKey()
            load Kraken API key from environment variables

        placeOrder(orderDetails)
            send specified order details to execute a trade in Kraken (method validates specific trade specifications)

        trigger(command, payload)
            generalized method for executing Kraken API commands


    ###########################################################################
    '''

    ###########################################################################

    def __init__(self):

        self.k = krakenex.API()

        self.acctMsgTypeMap = {'Balance'      :'private',
                               'TradeBalance' :'private',
                               'TradesHistory':'private',
                               'AddOrder'     :'private',
                               'Time'         :'public' ,
                               'AssetPairs'   :'public' ,
                               'Depth'        :'public' ,
                               }

        self.loanAPIKey()

        # ---------------------------------------------------------------------

        self.getBalance()

        self.getTradeBalance()

        self.getTradeHistory()

        self.getTradablePairs()

    ###########################################################################


    ###########################################################################

    def calcDateFromTimestamp(self, timestamp):

        if len(timestamp) >= 10:

            date = timestamp[0:10]

        else:

            raise Exception('Timestamp length is less than 10.')

        return dt.datetime.strptime(date, '%Y-%m-%d')

    ###########################################################################


    ###########################################################################

    def loanAPIKey(self):

        self.k.key    = os.environ['VAR_K']

        self.k.secret = os.environ['VAR_S']

    ###########################################################################


    ###########################################################################

    def trigger(self, command, payload = False):

        if command in self.acctMsgTypeMap.keys():

            reqType = self.acctMsgTypeMap[command]

            if    reqType == 'private' and payload:

                print(payload)

                result = self.k.query_private(command, payload)

            elif  reqType == 'private' and (not payload):

                result = self.k.query_private(command)

            elif   reqType == 'public' and payload:

                result = self.k.query_public(command, payload)

            elif   reqType == 'public' and (not payload):

                result = self.k.query_public(command)

            self.lastReturn = result

        return result

    ###########################################################################


    ###########################################################################

    def getBalance(self):

        self.balance = self.trigger('Balance')['result']

    ###########################################################################


    ###########################################################################

    def getTradeBalance(self):

        # asset = base asset used to determine balance (default = ZUSD)

        # eb    = equivalent balance (combined balance of all currencies)
        # tb    = trade balance (combined balance of all equity currencies)
        # m     = margin amount of open positions
        # n     = unrealized net profit/loss of open positions
        # c     = cost basis of open positions
        # v     = current floating valuation of open positions
        # e     = equity = trade balance + unrealized net profit/loss
        # mf    = free margin = equity - initial margin (maximum margin available to open new positions)
        # ml    = margin level = (equity / initial margin) * 100

        self.tradeBalance = self.trigger('TradeBalance')['result']

    ###########################################################################


    ###########################################################################

    def getTradeHistory(self):

        # trades    = array of trade info with txid as the key
        # ordertxid = order responsible for execution of trade
        # pair      = asset pair
        # time      = unix timestamp of trade
        # type      = type of order (buy/sell)
        # ordertype = order type
        # price     = average price order was executed at (quote currency)
        # cost      = total cost of order (quote currency)
        # fee       = total fee (quote currency)
        # vol       = volume (base currency)
        # margin    = initial margin (quote currency)
        # misc      = comma delimited list of miscellaneous info
        # closing   = trade closes all or part of a position
        # count     = amount of available trades info matching criteria

        histDict = self.trigger('TradesHistory')['result']['trades']

        histData = pd.DataFrame()

        for k in histDict.keys():

            aux = pd.DataFrame(histDict[k].items())
            aux.set_index(0, inplace=True)

            histData = histData.append(aux.T)

        histData['timestamp'] = histData['time'].apply(lambda x: dt.datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))

        # ---------------------------------------------------------------------

        self.tradeHistory = histData

    ###########################################################################


    ###########################################################################

    def getTradablePairs(self):

        self.tradablePairs = self.trigger('AssetPairs')['result']

    ###########################################################################


    ###########################################################################

    def getOrderBook(self, pair, depth = '100'):

        self.orderBook = self.trigger('Depth', {'pair' : pair,
                                                'count':str(depth)})['result']

    ###########################################################################


    ###########################################################################

    def placeOrder(self, orderDetails):

        pair   = orderDetails['pair']
        volume = orderDetails['volume']

        if int(self.tradablePairs[pair]['ordermin']) > int(volume):

            raise Exception('Order does not meet pair min lot size')

        else:

            self.orderConfirm  = self.trigger('AddOrder', orderDetails)

            return self.orderConfirm

    ###########################################################################


    ###########################################################################

    def fillOrder(self, row):

        if self.unFilled >= 0:

            fill = min(max(min(row['volume']- self.unFilled, 0), self.unFilled), row['volume'])

            self.unFilled = self.unFilled - fill

            return fill

        else:

            return 0

    ###########################################################################


    ###########################################################################

    def getBestPrice(self, pair, direction, quantity):

        self.getOrderBook(pair)

        # ---------------------------------------------------------------------

        if direction == 'buy':

            side     = 'asks'

            feeField = 'fees'

        if direction == 'sell':

            side     = 'bids'

            feeField = 'fees_maker'

        # ---------------------------------------------------------------------

        book = pd.DataFrame(self.orderBook[pair][side],
                            columns = ['price', 'volume', 'timestamp'])

        book['price']  = book['price'].astype(float)

        book['volume'] = book['volume'].astype(float)

        # ---------------------------------------------------------------------

        self.unFilled = quantity

        book['fill'] = book.apply(lambda row: self.fillOrder(row), axis = 1)

        book['fill_per'] = book['fill'] / book['fill'].sum()

        wap = (book['price'] * book['fill_per']).sum()

        # ---------------------------------------------------------------------

        feePercent = float(self.tradablePairs[pair][feeField][0][1]) / 100

        cost       = quantity * wap * (feePercent)

        return wap, cost

    ###########################################################################


###############################################################################
