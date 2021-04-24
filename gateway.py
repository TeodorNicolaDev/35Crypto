# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 18:26:24 2021

@author: Yasser
"""

###############################################################################

import os

import base64

import gunicorn

from urllib.parse import urlparse

import datetime as dt

import pandas as pd

import numpy as np

import requests

import psycopg2

import pandas.io.sql as sqlio

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

###############################################################################


###############################################################################

class Gateway(object):

    '''
    ###########################################################################

    Gateway Class Documentation
    ----------


    ...

    Attributes
    ----------

        launchDatatime (datetime.datetime)
            time at instantiation of the object

    Methods
    ----------

        read_sql(sql_code, connection)
            execute and return dateframe from the request of the sql query (sql_code)


    ###########################################################################
    '''

    ###########################################################################

    def __init__(self):

        self.launchDatatime = dt.datetime.now()

    ###########################################################################


    ###########################################################################

    def read_sql(self,
                 sql_code,
                 connection):

        data = sqlio.read_sql_query(sql_code, connection)

        if data is not None:

            data.columns = [x.upper() for x in data.columns]

        return data

    ###########################################################################


###############################################################################


###############################################################################

class DbConnections(object):

    '''
    ###########################################################################

    DbConnections Class Documentation
    ----------


    ...

    Attributes
    ----------

        connect (dict)
            dictionary that maps database names to connection objects

        gate (gateway.Gateway)
            connection object used to excute modified import and export calls

    Methods
    ----------

        checkTableExists(table_name, connection)
            ping database to validate if table exists in the defined schema (connection)

        createTable(database_name, table_name, column_dict, override)
            execute sql to generate table (table_name) in database (datebase_name) with the specifications defined (column_dict)

        fetchDBDetails()
            source database connection details from system variable

        insert(database_name, table_name, entry)
            execute sql to insert input entry records to target table


    ###########################################################################
    '''

    ###########################################################################

    def __init__(self):

        self.gate    = Gateway()

        self.connect = {'TRADE_PROD'   : None, # DB : SERVER
                        'TRADING_PROD' : None,
                        'SERVER_TEST'  : None} # DB : LOCAL DESKTOP

        self.fetchDBDetails()

    ###########################################################################


    ###########################################################################

    def fetchDBDetails(self):

        for database_url_name in self.connect.keys():

            if database_url_name in os.environ.keys():

                url = urlparse(os.environ[database_url_name])

                con = psycopg2.connect(
                                       dbname   = url.path[1:] ,
                                       user     = url.username ,
                                       password = url.password ,
                                       host     = url.hostname ,
                                       port     = url.port
                                       )

                con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

                self.connect[database_url_name] = con

    ###########################################################################


    ###########################################################################

    def checkTableExists(self,
                         table_name,
                         connection):

        if not isinstance(table_name, str):

            Exception('Input(table_name) : not string')

        # ---------------------------------------------------------------------

        if connection != psycopg2.extensions.connection:

            Exception('Input(connection) : not valid psycopg2 connection')

        # ---------------------------------------------------------------------

        table_name = table_name.upper()

        table_name = table_name.strip()

        # ---------------------------------------------------------------------

        sql = \
            '''
            SELECT * FROM INFORMATION_SCHEMA.TABLES
            WHERE UPPER(TABLE_NAME) = '{}'
            '''.format(table_name)

        data = sqlio.read_sql_query(sql, connection)

        # ---------------------------------------------------------------------

        if data.empty:

            return False

        else:

            return True

    ###########################################################################


    ###########################################################################

    def createTable(self,
                    database_name,
                    table_name   ,
                    column_dict  ,
                    override = False):

        if database_name in os.environ.keys():

            con = self.connect[database_name]

            cur = con.cursor()

            field_declaration = \
                ', '.join([x + ' ' + column_dict[x] for x in column_dict.keys()])

            # -----------------------------------------------------------------

            if override == True:

                cur.execute('DROP TABLE IF EXISTS {}'.format(table_name))

            # -----------------------------------------------------------------

            if self.checkTableExists(table_name, con):

                print('ALERT: "' + table_name.upper() + '" ALREADY EXISTS')

            else:

                sql = '''CREATE TABLE {} ( {} )'''.format(table_name, field_declaration)

                cur.execute(sql)

                print('SUCCESS: "' + table_name.upper() + '" CREATE IN "' + database_name.upper() + '"')

            # -----------------------------------------------------------------

        else:

            Exception('ERROR: DATABASE DETAILS NOT IN ENVIRONMENT VARIABLE')

    ###########################################################################


    ###########################################################################

    def insert(self,
               database_name,
               table_name   ,
               entry):

        if database_name in os.environ.keys():

            con = self.connect[database_name]

            cur = con.cursor()

        # --------------------------------------------------------------------

        updtDttm   = "'" + dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "'"

        field_insert = ', '.join([x for x in entry.keys()]) + ', UPDT_DTTM'

        value_insert = ', '.join(["'" + str(entry[x]).upper() + "'" for x in entry.keys()]) + ', ' + updtDttm


        cur.execute('''INSERT INTO {}({})
                                         VALUES ({})
                    '''.format(table_name, field_insert, value_insert))

        con.commit()

    ###########################################################################

###############################################################################
