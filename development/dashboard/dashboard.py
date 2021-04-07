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

#Temp
#from navigation import navigation

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

external_stylesheets = ['/assets/dashStyleSheet.css', '/assets/bootstrapStyles/bootstrap.css']


app = dash.Dash(__name__, external_stylesheets=[external_stylesheets])


sidebarStyle = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'background-color': '#4792C5',
    'height': '100%',
    'width': '16.667%',
    'z-index': 1001,
}

contentStyle = {
    'position': 'fixed',
    'top': 0,
    'right': 0,
    'bottom': 0,
    'height': '100%',
    'width': '83.333%',

}

cardStyle = {
    'margin': '10px',
}

logoStyle = {
    'display': 'block',
    'margin-left': 'auto',
    'margin-right': 'auto',
    #'width': '50%',
    'max-height': '100px',
    'min-height': '60px',
}

navStyle = {
    'font-weight': '600',
    'display': 'block',
    'margin-left': 'auto',
    'margin-right': 'auto',
    'align-items': 'center',
    'color': 'white',
}

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
dbList = dBStore_pg.getAllDB()
dbOptions = dropdownOptionFormatter(dbList)
#dcc.Dropdown(dbOptions, placeholder="Select a Database")

ASG_logo = "/assets/logo.png"

########
#Content
########

content = html.Div(
            id='graphical-analysis',
            children=[
                dcc.Graph(id='graph-container')
            ]
        )

###########
#Navigation
###########

##################
cardContent = dbc.Card(
    [
    dbc.CardHeader("DATA SELECTION"),
    dbc.CardBody(
        [
            dcc.Dropdown(id='database-selector', options=dbOptions, placeholder="Select a Database"),
            dcc.Dropdown(id='table-selector', multi=True, placeholder="Select a Sensor"),
            dcc.Dropdown(id='column-selector', options=dropdownOptionFormatter(addKeys()), placeholder="Select a Data Column",),
        ],
    ),],
    id='data-selector',
        color='success',
        outline=True,)

##################
sidebar = html.Div(
    [
        html.Img(src=ASG_logo, style=logoStyle,),
        dbc.Row(
        dbc.Nav(
            dbc.DropdownMenu(
                [
                    dbc.DropdownMenuItem("ABOUT", href="#",),
                    dbc.DropdownMenuItem("SPACE VISUALIZATION", href="#",),
                    dbc.DropdownMenuItem("GRAPHICAL ANALYSIS", href="#",),
                ],
                label="MENU",
                color="info",
            ), 
            style=navStyle,
            ),
            justify='center',
        ),
        html.Hr(),

        html.Div(cardContent, style=cardStyle),
    ],
    className='sidebar',
    style=sidebarStyle,
)



#######
#Layout
#######

app.layout = html.Div(
    [
        html.Div(sidebar, style=sidebarStyle),
        html.Div(content, style=contentStyle),
    ]
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