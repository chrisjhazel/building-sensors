#Graphical Analysis Page

import pandas as pd
import plotly
import plotly.express as px
import psycopg2

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc

import dBStore_pg
import dBStore_msql
from keyStore import addKeys

from app import app

###################
## Functions
###################
def dropdownOptionFormatter(objList):
    returnDictList = []
    for item in objList:
        if isinstance(item, tuple):
            returnDictList.append({'label': str(item[0]), 'value': str(item[0])})
        else:
            returnDictList.append({'label': str(item), 'value': str(item)})
    
    return returnDictList

def getSensorName(tables):
    sensorName = []
    dateInfo = []

    for table in tables:
        splitName = table[0].split("__")
        if splitName[0] not in sensorName:
            sensorName.append(splitName[0])
        dateInfo.append(splitName[1])

    return sensorName, dateInfo

