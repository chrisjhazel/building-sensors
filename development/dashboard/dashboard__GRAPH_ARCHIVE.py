#import flask
#import requests
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

## external_stylesheets = ['dashboardStyle.css']

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

##################
# DASH APP LAYOUT
##################



############
#Page1: ABOUT
#1 columns--About ASG, About sensor development project, devices used
############


############
#Page2: SPACE VISUALIZATION
#2 columns (.67, .33)--Mesh model of the project space | description and mesh viz selectors
############


############
#Page3: GRAPHICAL ANALYSIS
#2 columns (.33, .67)--data dropdown selectors | Analysis graph
############


# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
dbList = dBStore_pg.getAllDB()
dbOptions = dropdownOptionFormatter(dbList)
#dcc.Dropdown(dbOptions, placeholder="Select a Database")

"""
app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Dropdown(
        label='Select Project', id='database-selector', options=dbOptions, placeholder="Select a Database"
    ),

    dcc.Dropdown(
        id='table-selector', multi=True, placeholder="Select a Sensor"
    ),

    dcc.Dropdown(
        id='column-selector', options=dropdownOptionFormatter(addKeys()), placeholder="Select a Data Column", 
    ),

    dcc.Graph(id='graph-container'),

])
"""

app.layout = dbc.Row([
    dbc.Col(html.Div(
    id='data-selector',
    children=[
        html.H3("DATA SELECTION:"),
        
        dcc.Dropdown(
        id='database-selector', options=dbOptions, placeholder="Select a Database"
        ),

        dcc.Dropdown(
            id='table-selector', multi=True, placeholder="Select a Sensor"
        ),

        dcc.Dropdown(
            id='column-selector', options=dropdownOptionFormatter(addKeys()), placeholder="Select a Data Column", 
        ),]), width=3,),
        
    dbc.Col(
        html.Div(
            id='graphical-analysis',
            children=[
                dcc.Graph(id='graph-container')
            ]
        ), width=9
    )]
)





@app.callback(
    #callback for getting table data
    Output('graph-container', 'figure'),
    Input('database-selector', 'value'),
    Input('table-selector', 'value'),
    Input('column-selector', 'value'))
def getTableData(selDb, selSensor, selCol):
    #tableData = dBStore_pg.getLocalTableData(selDb, selTable)
    if isinstance(selSensor, list):
        dfTotal = pd.DataFrame()
        #figList = []
        #print(selSensor)
        for table in selSensor:
            dfSub = (dBStore_pg.createDataFrame(selDb, table))
            dfTotal = dfTotal.append(dfSub, ignore_index=True)
        
        #return figList[0]

        print(dfTotal)
        fig = px.line(dfTotal, x='time', y=selCol.lower(), color='sensor_name')
        return fig
    
    else:
        df = dBStore_pg.createDataFrame(selDb, selSensor)
        fig = px.line(df, x='time', y=selCol.lower())
    return fig

@app.callback(
    #callback for database table dropdown
    Output('table-selector', 'options'),
    Input('database-selector', 'value'))
def getDBTables(selDb):
    tableList = dBStore_pg.getAllTables(selDb)
    sensorList, toss = getSensorName(tableList)
    return [{'label': i, 'value': i} for i in sensorList]

"""
@app.callback(
    #callback for database selector dropdown
    Output('dd-output-container', 'children'),
    Input('database-selector', 'value'))
def update_output(value):
    return 'You have selected "{}"'.format(value)
    """

if __name__ == '__main__':
    app.run_server(debug=True)