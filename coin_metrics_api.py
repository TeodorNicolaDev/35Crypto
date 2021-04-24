# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 13:32:26 2021

@author: Yasser
"""

###############################################################################

import datetime as dt

import pandas as pd

import requests

###############################################################################


###############################################################################

class CoinMetricsAPI(object):

    '''
    ###########################################################################

    CoinMetricsAPI Class Documentation
    ----------


    ...

    Attributes
    ----------

        hostName (str)
            Coin Metrics API application address (hostname)

        metrics (str)
            endpoint for sourcing asset metrics

        metricsFields (str)
            endpoint for sourcing asset metric catalog

    Methods
    ----------

        calcDateFromTimestamp(timestamp)
            converts string timestamp to %Y-%m-%d formatted string date

        fetchMetrics(coin, start, end, field, freq)
            execute request to metric fields endpoint

        fetchMetricsDetail(coin)
            source metrics for given metric (field) with defined specifications


    ###########################################################################
    '''

    ###########################################################################

    def __init__(self):

        self.hostName      = 'https://community-api.coinmetrics.io/v4/'

        self.metrics       = self.hostName + 'timeseries/asset-metrics'

        self.metricsFields = self.hostName + 'catalog-all/metrics'

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

    def fetchMetricsDetail(self, coin):

        # ---------------------------------------------------------------------

        self.dest = self.metricsFields

        # ---------------------------------------------------------------------

        resp = requests.get(self.dest).json()

        # ---------------------------------------------------------------------

        self.metricsDetails = pd.DataFrame(resp['data'])

    ###########################################################################


    ###########################################################################

    def fetchMetrics(self, coin,
                           start,
                           end  ,
                           field = 'PriceUSD',
                           freq  = '1d'):

        # ---------------------------------------------------------------------

        self.dest = self.metrics    + \
                    '?assets='     + coin  + \
                        '&metrics='    + field + \
                            '&frequency='  + freq  + \
                                '&start_time=' + start  + \
                                    '&end_time='   + end  + \
                                        '&pretty=true&api_key=xxxx'

        # ---------------------------------------------------------------------

        resp = requests.get(self.dest).json()

        data = resp['data']

        while 'next_page_url' in resp.keys():

            resp = requests.get(resp['next_page_url']).json()

            data.extend(resp['data'])

        data = pd.DataFrame(data)

        data['date'] = \
            data['time'].apply(lambda x: self.calcDateFromTimestamp(x))

        data = data.sort_values('date', ascending = True)

        # ---------------------------------------------------------------------

        return data

    ###########################################################################


###############################################################################
