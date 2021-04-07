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

external_stylesheets = ['/assets/dashStyleSheet.css']

navButton = {
    'width': '20%',
    'height': '100%',
    'align-content': 'center',
    'justify-content': 'center',
    'text-align': 'center',
}


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY, external_stylesheets])

##################
# DASH APP LAYOUT
##################

##Colors
#Blue: #4792C5 
#Orange: #F15922
#Green: #C8D92B


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

ASG_logo = "/assets/logo.png"
"""
nav = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink("ABOUT", active=True, href="#")),
        dbc.NavItem(dbc.NavLink("SPACE VISUALIZATION", href="#")),
        dbc.NavItem(dbc.NavLink("GRAPHICAL ANALYSIS", href="#")),
    ],
    pills=True,
    horizontal='end',
)
"""
"""
nav = html.Nav(
    [
        html.A(html.Div("ABOUT", style=navButton), href="#"),
        html.A(html.Div("SPACE VISUALIZATION", style=navButton), href="#"),
        html.A(html.Div("GRAPHICAL ANALYSIS", style=navButton), href="#"),
    ],
    style={
        'float': 'right',
    }
)

dropdownMenu = dbc.DropdownMenu(
    label='MENU',
    children=[
        dbc.DropdownMenuItem("ABOUT", href="#", className="navButton", style={'background-color': '#F15922'},),
        dbc.DropdownMenuItem("SPACE VISUALIZATION", href="#", className="navButton", style={'background-color': '#F15922'},),
        dbc.DropdownMenuItem("GRAPHICAL ANALYSIS", href="#", className="navButton", style={'background-color': '#F15922'},),
    ],
    style={
        'height': '60px',
        'width': '20%',
        'float': 'right',
    },
    color='link',
)

topbar = html.Div(
    [
        html.Img(src=ASG_logo, height='60px', style={'margin': '5px 20px', 'float': 'left',}),
        html.H1("SENSOR DASHBOARD", style={'vertical-align': 'middle', 'color': 'white', 'float': 'left'}),
        dropdownMenu,
    ],
    style={
        'width': '100%',
        'float':'left',
        'background-color':'#4792C5',
    }
)

topbar = html.Nav(
    dbc.Row(
        [
            dbc.Col(html.A(html.Img(src=ASG_logo, height='60px',)), width=1,),
            dbc.Col(html.H1("SENSOR DASHBOARD"), width=7, style={'color': 'white'}), 
            dbc.Col(dropdownMenu, width=4, align='end',),
        ],
        no_gutters=True,
        style={
            'margin': '5px 20px',
            'width': '100%',
        }
    ),
    style={
        'width': '100%',
        'background-color': '#4792C5',
    }
)
"""

navbar = dbc.Navbar(
    [
        html.A(
            dbc.Row(
                [
                    dbc.Col(html.Img(src=ASG_logo, height='60px')),
                    dbc.Col(dbc.NavbarBrand("sensor_dashboard", style={'color': 'white'})),
                ],
                align='center',
                no_gutters=True,
                
            ),
            href='#',
            
        )
    ], 
    id='navbarNew',
    className='navbarNew',
)

app.layout = html.Div([
    navbar,
    dbc.Row([
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
)])





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