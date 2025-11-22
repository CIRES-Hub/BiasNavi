import dash_bootstrap_components as dbc
from dash import dcc, html


def menu():
    return dbc.Row(justify="center", align="center", children=[
            html.Div(children=[

                dcc.Store(id="base-styles", data={}),
                html.Div(id="overlay",
                         style={"position": "fixed", "top": "0", "left": "0", "width": "100%", "height": "100%",
                                "backgroundColor": "rgba(0, 0, 0, 0.7)", "z-index": "100", "display": "none"}),

                # ================= Menu
                html.Img(src='../assets/logo.svg', className="logo"),
                html.P('BiasNavi', className="title mb-1"),
                dbc.Nav(
                    className='navbar d-flex flex-wrap',
                    children=[
                        dbc.DropdownMenu(
                            [dbc.DropdownMenuItem(
                                "Import Dataset", id="menu-import-data")],
                            label="Import",
                            nav=True,
                            toggleClassName="dropdown-toggle",
                            className='menu-item',
                            id="menu-dataset",

                        ),
                        # dbc.DropdownMenu(
                        #     [
                        #         dbc.DropdownMenuItem("Export Chat History", id="menu-export-chat"),
                        #         dbc.DropdownMenuItem(
                        #             "Export Dataset Analysis Report")],
                        #     label="Export",
                        #     nav=True,
                        #     toggleClassName="dropdown-toggle",
                        #     className='menu-item',
                        #     id="menu-export",
                        # ),
                        # dbc.DropdownMenu(
                        #     [dbc.DropdownMenuItem("Predefined Prompt 1"),
                        #      dbc.DropdownMenuItem("Predefined Prompt 2"),
                        #      dbc.DropdownMenuItem("Custom Prompt")],
                        #     label="Prompts",
                        #     nav=True,
                        #     toggleClassName="dropdown-toggle",
                        #     className='menu-item'
                        # ),
                        dbc.DropdownMenu(
                            [dbc.DropdownMenuItem("GPT-4o-mini", id="menu-model-gpt4omini"),
                             dbc.DropdownMenuItem("GPT-4o  ✔", id="menu-model-gpt4o")],
                            label="LLM Models",
                            nav=True,
                            toggleClassName="dropdown-toggle",
                            className='menu-item',
                            id="menu-model",
                        ),
                        dbc.DropdownMenu(
                            [
                                dbc.DropdownMenuItem("Baseline Mode", id="menu-baseline-view"),
                                dbc.DropdownMenuItem("Non-expert Mode  ✔", id="menu-nex-view"),
                                dbc.DropdownMenuItem("Expert Mode", id="menu-ex-view"),
                             ],
                            label="Mode",
                            nav=True,
                            toggleClassName="dropdown-toggle",
                            className='menu-item',
                            id="menu-view",
                        ),
                        dbc.NavLink("Prompts", id="menu-prompt", className='nav-item'),
                        dbc.NavLink("User Profile", id="menu-profile", className='nav-item'),
                        # dbc.DropdownMenu(
                        #     [dbc.DropdownMenuItem("Wizard", id="menu-help-wizard"),
                        #      dbc.DropdownMenuItem("Tutorial", id="menu-help-tutorial",
                        #                           href="https://jayhuynh.github.io/biasnavi-website/"), ],
                        #     label="Help",
                        #     nav=True,
                        #     toggleClassName="dropdown-toggle",
                        #     className='menu-item',
                        #     id="menu-help"
                        # ),
                        dbc.DropdownMenu(
                            [
                                dbc.DropdownMenuItem(
                                    "About CIRES", href="https://cires.org.au/"),
                                dbc.DropdownMenuItem(
                                    "Logout", id="logout-button", href="/")
                            ],
                            label="More",
                            nav=True,
                            toggleClassName="dropdown-toggle",
                            className='menu-item'
                        )
                    ],
                ),
                dcc.Location(id='url', refresh=False)
            ], className='banner'),
        ])
