# -*- coding: utf-8 -*-
"""
Created on Thu Apr 15 11:54:53 2021

@author: Yasser
"""

###############################################################################

import os

import json

import inspect

import types

###############################################################################


###############################################################################

class AutoDocumentation(object):

    ###########################################################################

    def __init__(self):

        self.baseDir        = os.path.dirname(os.path.realpath(__file__))

        self.attributesName = os.path.join(self.baseDir, 'attributes.json')
        self.methodsName    = os.path.join(self.baseDir, 'methods.json')

        self.attributes = {}
        self.methods    = {}

        self.importAttributes()
        self.importMethods()

        # ---------------------------------------------------------------------

        self.classHeader = \
            """    ###########################################################################\n\n""" + \
            """    {} Class Documentation\n""" + \
            """    ----------\n\n\n"""                  + \
            """    ... \n\n"""

        self.attributeHeader =  \
            """    Attributes \n""" + \
            """    ----------\n\n"""

        self.attributeTemplate = \
            """        {} ({})\n""" + \
            """            {} \n\n"""


        self.methodHeader = \
            """    Methods \n""" + \
            """    ---------- \n\n"""

        self.methodTemplate = \
            """        {}({})\n""" + \
            """            {} \n\n"""

        self.closer = \
            """\n    ###########################################################################"""

    ###########################################################################


    ###########################################################################

    def importAttributes(self):

        if os.path.exists(self.attributesName):

            with open(self.attributesName, "r") as json_data:

                self.attributes = json.loads(json_data.read())

    ###########################################################################


    ###########################################################################

    def importMethods(self):

        if os.path.exists(self.methodsName):

            with open(self.methodsName, "r") as json_data:

                self.methods = json.loads(json_data.read())

    ###########################################################################


    ###########################################################################

    def exportAttributes(self):

        with open(self.attributesName, 'w') as fp:

            json.dump(self.attributes  ,
                      fp               ,
                      sort_keys = True ,
                      indent    = 4)

    ###########################################################################


    ###########################################################################

    def exportMethods(self):

        with open(self.methodsName, 'w') as fp:

            json.dump(self.methods     ,
                      fp               ,
                      sort_keys = True ,
                      indent    = 4)

    ###########################################################################


    ###########################################################################

    def runDocumentation(self, obj):

        # ---------------------------------------------------------------------

        methods    = {}
        attributes = {}

        # ---------------------------------------------------------------------

        for val in dir(obj):

            if len(val) < 3:

                continue

            if val[:2] != '__':

                valType = type(getattr(obj, val))

                if valType == types.MethodType:

                    inputs = inspect.getfullargspec(getattr(obj, val))[0]

                    inputs = [x for x in inputs if x != 'self']

                    if val in self.methods.keys():

                        desc = self.methods[val]['description']

                    else:

                        desc = ''

                        self.methods[val] = {'type'        : 'method',
                                             'description' : desc}

                        self.exportMethods()

                    methods[val]      = {'type'        : 'method',
                                         'description' : desc,
                                         'inputs'      : inputs}

                else:

                    attributes[val] =  {'type'        : str(valType).replace("<class '", "").replace("'>",""),
                                        'description' : ''}

                    if val in self.attributes.keys():

                        desc = self.attributes[val]['description']

                    else:

                        desc = ''

                        self.attributes[val] = {'description' : desc}

                    attributes[val] =  {'type'        : str(valType).replace("<class '", "").replace("'>",""),
                                        'description' : desc}


                    self.exportAttributes()

        # ---------------------------------------------------------------------

        attributeDoc = self.attributeHeader

        for key, dictVals in attributes.items():

            attributeDoc = attributeDoc + self.attributeTemplate.format(key             ,
                                                                        dictVals['type'],
                                                                        dictVals['description'])

        methodDoc = self.methodHeader

        for key, dictVals in methods.items():

            methodDoc = methodDoc + self.methodTemplate.format(key             ,
                                                               ', '.join(dictVals['inputs']),
                                                               dictVals['description'])

        # ---------------------------------------------------------------------

        className = type(obj).__name__

        doc = self.classHeader + attributeDoc + methodDoc + self.closer

        doc = doc.format(className)

        # ---------------------------------------------------------------------

        className = type(obj).__name__

        with open('documenation_' + className + '.txt', "w") as t:

           t.write(doc)

    ###########################################################################


###############################################################################
