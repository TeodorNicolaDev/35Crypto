# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 21:50:21 2021

@author: Yasser
"""

###############################################################################

import os

import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..')))

# -----------------------------------------------------------------------------

import autodoc as ad

# -----------------------------------------------------------------------------

import gateway

import coin_metrics_api

###############################################################################


###############################################################################

# Loan Automatic Documenation Generator

AutoDoc = ad.AutoDocumentation()

# -----------------------------------------------------------------------------

# Run automatic documentation generator for each object

AutoDoc.runDocumentation(gateway.Gateway())

AutoDoc.runDocumentation(gateway.DbConnections())

AutoDoc.runDocumentation(coin_metrics_api.CoinMetricsAPI())

###############################################################################
