import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Get min and max payload values
max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

# Create a Dash application
app = dash.Dash(__name__)

# Create launch site dropdown options
launch_sites = spacex_df["Launch Site"].unique().tolist()

site_dropdown_options = [{"label": "All Sites", "value": "ALL"}]
site_dropdown_options += [
    {"label": site, "value": site} for site in launch_sites
]

# Create app layout
app.layout = html.Div(
    children=[
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={
                "textAlign": "center",
                "color": "#503D36",
                "font-size": 40,
            },
        ),

        dcc.Dropdown(
            id="site-dropdown",
            options=site_dropdown_options,
            value="ALL",
            placeholder="Select a Launch Site here",
            searchable=True,
        ),

        html.Br(),

        html.Div(
            dcc.Graph(id="success-pie-chart")
        ),

        html.Br(),

        html.P("Payload range (Kg):"),

        dcc.RangeSlider(
            id="payload-slider",
            min=0,
            max=10000,
            step=1000,
            marks={
                0: "0",
                2500: "2500",
                5000: "5000",
                7500: "7500",
                10000: "10000",
            },
            value=[min_payload, max_payload],
        ),

        html.Br(),

        html.Div(
            dcc.Graph(id="success-payload-scatter-chart")
        ),
    ]
)


@app.callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value"),
)
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        fig = px.pie(
            spacex_df,
            values="class",
            names="Launch Site",
            title="Total Success Launches by Site",
        )
        return fig
    else:
        filtered_df = spacex_df[spacex_df["Launch Site"] == entered_site]
        success_counts = filtered_df["class"].value_counts().reset_index()
        success_counts.columns = ["class", "count"]

        fig = px.pie(
            success_counts,
            values="count",
            names="class",
            title=f"Total Success Launches for site {entered_site}",
        )
        return fig


@app.callback(
    Output(component_id="success-payload-scatter-chart", component_property="figure"),
    [
        Input(component_id="site-dropdown", component_property="value"),
        Input(component_id="payload-slider", component_property="value"),
    ],
)
def update_scatter_chart(entered_site, payload_range):
    low, high = payload_range

    filtered_df = spacex_df[
        (spacex_df["Payload Mass (kg)"] >= low)
        & (spacex_df["Payload Mass (kg)"] <= high)
    ]

    if entered_site == "ALL":
        fig = px.scatter(
            filtered_df,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
            title="Correlation between Payload and Success for all Sites",
        )
        return fig
    else:
        site_df = filtered_df[filtered_df["Launch Site"] == entered_site]

        fig = px.scatter(
            site_df,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
            title=f"Correlation between Payload and Success for site {entered_site}",
        )
        return fig


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)