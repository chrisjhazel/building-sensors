#About page

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc

def about():
    html.H1(
        "ABOUT"
    )

    html.H2(
        "Ayers Saint Gross | Engage, Create, Enrich"
    )
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
    )

    html.Hr()

    html.H2(
        "Sensor Development"
    )

    html.P(
        """
        The Sensor Development project began in Spring 2020 as 
        an internal research and development project to measure, 
        visualize, and analyze quantitative human comfort metrics. 
        """
    )