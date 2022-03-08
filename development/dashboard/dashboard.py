#import flask
#import requests
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objs as go
import psycopg2
import datetime
from scipy import signal

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

import dash_bootstrap_components as dbc

import dBStore_pg
import dBStore_msql
import dBStore_csv
from keyStore import addKeys
from remote_connect import remote_connect

###########################
## NOTES AND ADDED FUNCTONS
###########################
"""
-Add multiple comfort categories (stack temperature and humidity) || DONE
-Add static metrics like average temp, humidity, sound (weighted avg to give less weight to outliers?), time within comfort and non-comfort ranges, etc
-Time selector to specify period (buttons to quick select hour, day, week, month) || DONE
-Outdoor comfort metrics (pull from OpenWeatherMaps)
-Local and remote data server connections || DONE
-Show range values (temp, humidity) to show difference between max and min (total and something to remove outliers) || DONE
-Smooth graph lines || DONE
-Circular data graph (24h clock of data)
-Add accordian effect to cards
"""

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

fileDir = r"/Users/chrishazel/Documents/GitHub/building-sensors/development/dashboard/dataDump"

remote_access = remote_connect()

####INFO STUFF
dbType=[{'label': 'Local Database', 'value': 'local'}, {'label': 'Remote Database', 'value': 'remote'}, {'label': 'CSV Files', 'value': 'csv'}]
timeOptions = dropdownOptionFormatter(['HOUR', 'DAY', 'WEEK', 'MONTH', 'YEAR', 'ALL', 'CUSTOM'])
analysisSelectorOptions = [{'label': ' ALL HOURS', 'value': 'all'}, {'label': ' WORKING HOURS', 'value': 'working'}, {'label': ' NON-WORKING HOURS', 'value': 'nonworking'}]


#### STYLE STUFF
asg_blue = '#4792C5'
asg_orange = '#F15922'
asg_green = '#C8D92B'
asg_purple = '#8864DE'
asg_gray = '#B8B8B8'
#
asg_blueList = [asg_blue, '#2D3B45', '#88B2CE', '#346C91', '#193345', '#92C0DE', '#6C8DA4', '#22465E', '#50A5DE']
asg_orangeList = [asg_orange, '#734432', '#F4906C', '#BF471B', '#732A10', '#40261C', '#CA7759', '#8C3414', '#401809']
asg_greenList = [asg_green, '#55592D', '#D4DF70', '#98A621', '#525912', '#55592D', '#D4DF70', '#98A621', '#525912']
asg_purpleList = [asg_purple, '#4E475E', '#BCABE3', '#694DAB', '#3A2A5E', '#4E475E', '#BCABE3', '#694DAB', '#3A2A5E']
asg_grayList = [asg_gray, '#C7C7C7', '#D4D4D4', '#E0E0E0', '#EDEDED', '#8F8F8F', '#999999', '#A3A3A3', '#ADADAD']


asg_ColorList_Primary = [asg_blue, asg_orange, asg_green, asg_purple, asg_gray]
asg_ColorList_All = [asg_blueList, asg_orangeList, asg_greenList, asg_purpleList, asg_grayList]

sidebarStyle = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'background-color': '#4792C5',
    'height': '99%',
    'width': '16.667%',
    'z-index': 1001,
    'border-radius': '15px',
    'margin': '5px',
    #'box-shadow': '50px, 50px, #000000', #NOT CURRENTLY WORKING
}

contentStyle = {
    'position': 'fixed',
    'top': 0,
    'right': 0,
    'bottom': 0,
    'height': '100%',
    'width': '83.333%',
    'padding': '10px 20px',

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

staticMetricContainer = {
    'background-color': '#fafafa',
    'color': 'black',
    'align-items': 'center',
    'border-radius': '10px',
    'width': '18%',
    'padding': '10px',
}

staticMetricContainer_header = {
    'height': '25px',
    #'position': 'absolute',
    #'left': '50%',
}

staticMetricContainer_body = {
    'height': '125px',
    #'position': 'absolute',
    #'left': '50%',
    'font-weight': 'bold',
    'font-size': '55px',
}

staticRadioItemContainer_body = {
    'height': '125px',
    'font-weight': 'bold',
    'font-size': '15px',
    'bottom': '0px',
}

container_spacer = {
    'background-color': '#ffffff',
    'height': '15px',
}

###############
#CONTENT GROUPS
###############

#About Content
about_content = html.Div(
    [
        html.H2(
            "Ayers Saint Gross | Engage, Create, Enrich"
        ),
        html.P(
            """
        Ayers Saint Gross is an internationally recognized, 
        employee-owned design firm with expertise in architecture, 
        planning, landscape architecture, graphic design, 
        interiors, and space analytics. Since our founding 
        in 1912, we have built a reputation for designing 
        environments of enduring value. The majority of our 
        work is in support of colleges, universities, and 
        cultural facilities. Our design is inspired by critical 
        and analytical discourse, a respect for past wisdom, 
        a mind to future potential, and a belief that we have 
        an obligation to leave places better than we found them.
        """
        ),

        html.Hr(),

        html.H2(
            "Sensor Development"
        ),

        html.P(
            """
        The Sensor Development project began in Spring 2020 as 
        an internal research and development project to measure, 
        visualize, and analyze quantitative human comfort metrics. 
        """
        ),
    ], 

)

about_cardContent = html.Div('test')




# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
#dbList = dBStore_pg.getAllDB()
#dbOptions = dropdownOptionFormatter(dbList)
#dcc.Dropdown(dbOptions, placeholder="Select a Database")

ASG_logo = "/assets/logo.png"

########
#Content
########

graph_content = html.Div(
            id='graphical-analysis',
            children=[
                html.Div(
                    children=[
                        html.Div(children=[
                            html.Div("Analysis_Selector:", style=staticMetricContainer_header),
                            dcc.RadioItems(id='analysis_selector', options=analysisSelectorOptions, value='all', style=staticRadioItemContainer_body),
                            
                        ],
                        style=staticMetricContainer),

                        html.Div(children=[
                            html.Div("Temperature_Average:", style=staticMetricContainer_header),
                            html.Div(id='temperature_average', style=staticMetricContainer_body),
                        ],
                        style=staticMetricContainer),

                        html.Div(children=[
                            html.Div("Temperature_Range:", style=staticMetricContainer_header),
                            html.Div(id='temperature_range', style=staticMetricContainer_body),
                        ],
                        style=staticMetricContainer),

                        html.Div(children=[
                            html.Div("Humidity_Average:", style=staticMetricContainer_header),
                            html.Div(id='humidity_average', style=staticMetricContainer_body),
                        ],
                            style=staticMetricContainer),

                        html.Div(children=[
                            html.Div("Humidity_Range:", style=staticMetricContainer_header),
                            html.Div(id='humidity_range', style=staticMetricContainer_body),
                        ],
                            style=staticMetricContainer),

                    ],
                    style={
                        'display': 'flex',
                        'justify-content': 'space-between',
                        'width': '100%',
                        'height': '150px',
                    }
                ),
                html.Div(style=container_spacer),
                dbc.Card(dcc.Graph(id='graph-container'), color="primary", outline=True),

                #Store the dataframe as JSON
                dcc.Store(id='analysis_dataframe')

                
            ]
        )

###########
#Navigation
###########

##################
## Add accordian to cards to lessen content
## https://www.w3schools.com/bootstrap/tryit.asp?filename=trybs_collapsible_accordion&stacked=h
##################
graph_cardContent = html.Div(
    dbc.Card(
        [
            dbc.CardHeader("DATA SELECTION"),
            dbc.CardBody(
                [
                    dcc.Dropdown(id='local_remote_selector', options=dbType, placeholder="Select a Database"),
                    dcc.Dropdown(id='database-selector', placeholder="Select a Project"),
                    dcc.Dropdown(id='table-selector', multi=True, placeholder="Select Sensors"),
                    dcc.Dropdown(id='column-selector', multi=True, options=dropdownOptionFormatter(addKeys()), placeholder="Select a Data Column"),
                ],
            ), 

            dbc.CardHeader("PERIOD SELECTOR"),
            dbc.CardBody(
                [
                    #dcc.Dropdown(id='time_selector', options=timeOptions, placeholder="Select a time period"),
                    dcc.DatePickerRange(id='date_selector', start_date_placeholder_text="Start Period", end_date_placeholder_text="End Period", with_portal=True)
                ]
            ), 

            dbc.CardHeader("PLOT OPTIONS"),
            dbc.CardBody(
                [
                    dcc.Checklist(id='smooth_option', options=[{'label': '   SMOOTH DATA ', 'value': 'smooth'}], value=['smooth']),
                    dcc.Checklist(id='group_option', options=[{'label': '   GROUP BY SENSOR', 'value': 'sensor'}]),
                ]
            ),

        ],
        color='success',
        outline=True,
    )
)


##################
sidebar = html.Div(
    [
        html.Img(src=ASG_logo, style=logoStyle,),
        dbc.Row(
        dbc.Nav(
            dbc.DropdownMenu(
                [
                    dbc.DropdownMenuItem("ABOUT", href="/about",),
                    dbc.DropdownMenuItem("SPACE VISUALIZATION", href="#",),
                    dbc.DropdownMenuItem("GRAPHICAL ANALYSIS", href="/graph",),
                ],
                label="MENU",
                color="info",
            ), 
            style=navStyle,
            ),
            justify='center',
        ),
        html.Hr(),

        html.Div(id="card_content", style=cardStyle),
    ],
    className='sidebar',
    style=sidebarStyle,
)



#######
#Layout
#######

app.layout = html.Div(
    [
        dcc.Location(id="url"),
        html.Div(sidebar, style=sidebarStyle),
        html.Div(id="content_container", style=contentStyle),
    ]
)


@app.callback(
    #navigation callback to direct content container
    Output('content_container', 'children'),
    Output('card_content', 'children'),
    Input('url', 'pathname'),)
def render_content_container(pathname):
    if pathname == "/about":
        return about_content, about_cardContent
    elif pathname == "/graph":
        return graph_content, graph_cardContent
"""
@app.callback(
    #disable/enable date selector
    Output('date_selector', 'disabled'),
    Input('time_selector', 'value'),)
def enable_date_selector(selectorEnable):
    if selectorEnable == "CUSTOM":
        return False
    else:
        return True
"""

@app.callback(
    #callback to choose between local and remote database
    Output('database-selector', 'options'),
    Input('local_remote_selector', 'value'),)
def databaseSelector(selector):
    if selector == 'local':
        #dbList = dBStore_pg.getAllDB()
        return None
        
    elif selector == 'remote':
        dbList = dBStore_msql.getAllDB(remote_access[0], remote_access[1]) #Remove before upload

    elif selector == 'csv':
        dbList = ['csv_folder']
    
    dbOptions = dropdownOptionFormatter(dbList)
    return dbOptions


@app.callback(
    Output('temp-container', 'children'),
    Input('date_selector', 'start_date'),
    Input('date_selector', 'end_date'),
)
def printDate(dateStart, dateEnd):
    if dateStart == None or dateEnd == None:
        raise PreventUpdate
    else:
        startDate = datetime.date.fromisoformat(dateStart)
        endDate = datetime.date.fromisoformat(dateEnd)
        print(startDate, endDate)
        return 'test'

@app.callback(
    #callback for getting table data
    Output('graph-container', 'figure'),
    Output('analysis_dataframe', 'data'),
    Input('database-selector', 'value'),
    Input('table-selector', 'value'),
    Input('column-selector', 'value'), 
    Input('local_remote_selector', 'value'),
    Input('date_selector', 'start_date'),
    Input('date_selector', 'end_date'),
    Input('smooth_option', 'value'),
    Input('group_option', 'value'),)
def getTableData(selDb, selSensor, selCol_list, selector, startDate, endDate, smoother, grouper):
    if selDb == None or selSensor == None or selCol_list == None or selector == None or startDate == None or endDate == None:
        raise PreventUpdate
    else:

        dfTotal = pd.DataFrame()

        if selector == 'local':
            for table in selSensor:
                dfSub = (dBStore_pg.createDataFrame(selDb, table))
                dfTotal = dfTotal.append(dfSub, ignore_index=True)
        
        elif selector == 'remote':
            for table in selSensor:
                dfSub = (dBStore_msql.createDataFrame(remote_access[0], remote_access[1], table))
                dfTotal = dfTotal.append(dfSub, ignore_index=True)
        
        elif selector == 'csv':
            for table in selSensor:
                dfSub = (dBStore_csv.createDataFrame(table, fileDir))
                dfTotal = dfTotal.append(dfSub, ignore_index=True)

        mask = (dfTotal['time'] >= startDate) & (dfTotal['time'] <= endDate)
        dfTotal = dfTotal.loc[mask]

        if len(selCol_list) == 1:
            #Single Column Data
            selCol = selCol_list[0]

            if smoother:
                fig = px.line(dfTotal, x='time', y=signal.savgol_filter(dfTotal[selCol.upper()], 53, 3), color='sensor_name')
            else:
                fig = px.line(dfTotal, x='time', y=selCol.upper(), color='sensor_name')
        
        elif 2 <= len(selCol_list) <= 5:
            #Two data columns, show scale on both sides
            fig = go.Figure(layout = go.Layout(height=700))

            column1Title = selCol_list[0]
            column2Title = selCol_list[1]
            if len(selCol_list) > 2: column3Title = selCol_list[2]
            else: column3Title = " "
            if len(selCol_list) > 3: column4Title = selCol_list[3]
            else: column4Title = " "
            if len(selCol_list) > 4: column5Title = selCol_list[4]
            else: column5Title = " "

            fig.update_layout(
                yaxis = {'title': column1Title},
                yaxis2 = {'title': column2Title, 'side': 'right'},
                yaxis3 = {'title': column3Title, 'side': 'right', 'overlaying': 'y', 'position': .85},
                yaxis4 = {'title': column4Title, 'side': 'right', 'overlaying': 'y', 'position': .90},
                yaxis5 = {'title': column5Title, 'side': 'right', 'overlaying': 'y', 'position': .95},
                legend = {'orientation': 'h'},
                showlegend = True,
            )

            for s, sensor in enumerate(selSensor):
                sensorMask = dfTotal['sensor_name'] == sensor
                sensorName_sub = sensor.split('__')
                sensorName = sensorName_sub[0]
                dfSensor = dfTotal.loc[sensorMask]
                legendGroup_sensor = "group{}".format(s)

                for c, column in enumerate(selCol_list):
                    legendGroup_category = "group{}".format(c)

                    if grouper:
                        legendGroup = legendGroup_sensor
                    else:
                        legendGroup = legendGroup_category

                    if c > 0:
                        yaxisStr = "y{}".format(c+1)
                        if smoother:
                            fig.add_trace(go.Scattergl(x=dfSensor['time'], y=signal.savgol_filter(dfSensor[column.upper()], 53, 3), line={'color': asg_ColorList_All[c][s]}, yaxis=yaxisStr, name="{} | {}".format(column.upper(), sensorName), legendgroup=legendGroup))
                        else:
                            fig.add_trace(go.Scattergl(x=dfSensor['time'], y=dfSensor[column.upper()], line={'color': asg_ColorList_All[c][s]}, yaxis=yaxisStr, name="{} | {}".format(column.upper(), sensorName), legendgroup=legendGroup))
                    else:
                        if smoother:
                            fig.add_trace(go.Scattergl(x=dfSensor['time'], y=signal.savgol_filter(dfSensor[column.upper()], 53, 3), line={'color': asg_ColorList_All[c][s]}, name="{} | {}".format(column.upper(), sensorName), legendgroup=legendGroup))
                        else:
                            fig.add_trace(go.Scattergl(x=dfSensor['time'], y=dfSensor[column.upper()], line={'color': asg_ColorList_All[c][s]}, name="{} | {}".format(column.upper(), sensorName), legendgroup=legendGroup))

        else:
            print('too many columns selected. whomp whomp.')
            return None, None

        #convert dfTotal to JSON String to store in browser
        #dfJSON = dfTotal.to_json(date_format='iso', orient='split')
        #print(dfJSON)
        return fig, dfTotal.to_json(date_format='iso', orient='split')

@app.callback(
    #Callback for averages and anallysis
    Output('temperature_average', 'children'),
    Output('temperature_range', 'children'),
    Output('humidity_average', 'children'),
    Output('humidity_range', 'children'),
    Input('analysis_selector', 'value'),
    Input('analysis_dataframe', 'data'),)
def dataframeAnalysis(selector, dfJSON):
    if dfJSON == None:
        raise PreventUpdate
    else:
        dfTime = pd.read_json(dfJSON, orient='split')
        dfTime['time'] = pd.to_datetime(dfTime['time'])
        dfTime.set_index('time', inplace=True)

        if selector == 'all':
            dfSelect = dfTime

        elif selector == 'working':
            #Find values for working hours only
            dfSelect = dfTime.between_time(datetime.time(hour=8), datetime.time(hour=18))
        
        elif selector == 'nonworking':
            #Find values for non-working hours only
            dfSelect = dfTime.between_time(datetime.time(hour=18), datetime.time(hour=8))

        roundSet = 1

        meanVal_tempNum = dfSelect['TEMPERATURE'].mean()
        meanVal_temp = "{} °F".format(round(meanVal_tempNum), roundSet)
        rangeVal_tempNum = abs(dfSelect['TEMPERATURE'].max()-dfSelect['TEMPERATURE'].min())
        rangeVal_temp = "{} °F".format(round(rangeVal_tempNum), roundSet)
        meanVal_humNum = dfSelect['HUMIDITY'].mean()
        meanVal_hum = "{}%".format(round(meanVal_humNum), roundSet)
        rangeVal_humNum = abs(dfSelect['HUMIDITY'].max()-dfSelect['HUMIDITY'].min())
        rangeVal_hum = "{}%".format(round(rangeVal_humNum), roundSet)

        return meanVal_temp, rangeVal_temp, meanVal_hum, rangeVal_hum

@app.callback(
    #callback for database table dropdown
    Output('table-selector', 'options'),
    Input('database-selector', 'value'),
    Input('local_remote_selector', 'value'),)
def getDBTables(selDb, selector):
    if selDb == None or selector == None:
        raise PreventUpdate
    else:
        if selector == 'local':
            tableList = dBStore_pg.getAllTables(selDb)
            sensorList, toss = getSensorName(tableList)
        elif selector == 'remote':
            tableList = dBStore_msql.getAllTables(remote_access[0], remote_access[1]) #Remove before upload
            sensorList = []
            for s in tableList:
                if "data" in s[0].lower():
                    sensorList.append(s[0])
        elif selector == 'csv':
           sensorList  = dBStore_csv.getAllTables(fileDir)
           sensorList.sort()

        tableSelect = [{'label': i, 'value': i} for i in sensorList]
        return tableSelect


if __name__ == '__main__':
    app.run_server(debug=True)
