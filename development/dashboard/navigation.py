#Navigation File

import dash_bootstrap_components as dbc

############
#Navigation
############
ASG_logo = "_assets/logo.png"

def navigation():

    nav = dbc.Nav(
        [
            dbc.NavItem(dbc.NavLink("ABOUT", active=True, href="#")),
            dbc.NavItem(dbc.NavLink("SPACE VISUALIZATION", href="#")),
            dbc.NavItem(dbc.NavLink("GRAPHICAL ANALYSIS", href="#")),
        ]
        pills=True,
    )

    navbar = dbc.Navbar(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=ASG_logo, height="30px")),
                        dbc.Col(dbc.NavbarBrand("Sensor Dashboard")),
                    ],
                    align="center",
                    no_gutters=True,
                ),
                href="https://asg-architects.com/",
            ),
        ],
        color="dark",
        dark=True,
        children=nav,
    )

    return navbar