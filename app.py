import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objs as go

# Assuming your CSV file is named "snyk_issues_flat.csv"
df = pd.read_csv("snyk_issues_flat.csv")

# Group data by title and get latest updated date & count
grouped_data = (
    df.groupby("title")
    .agg(
        latest_updated_date=pd.NamedAgg(column="updated_at", aggfunc=max),
        count=("title", "count"),
    )
    .reset_index()
)

# Create a Dash app
app = Dash(__name__)

# Define app layout
app.layout = html.Div(
    children=[
        dcc.Graph(id="scatter-chart"),
    ]
)


@app.callback(
    Output("scatter-chart", "figure"),
    Input("scatter-chart", "relayoutData"),
)
def update_chart(relayout_data):
    """
    Updates the scatter plot based on user interaction.

    Args:
        relayout_data (dict): Optional data from user interaction with the chart.

    Returns:
        dict: Updated scatter plot figure.
    """
    figure = go.Figure(
        data=[
            go.Scatter(
                x=grouped_data["latest_updated_date"],
                y=grouped_data["count"],
                text=grouped_data["title"],  # Text labels for markers
                mode="markers",
                marker={
                    "size": 15,
                    "color": "cornflowerblue",
                    "opacity": 0.7,
                },
                hoverinfo="text",  # Display title on hover
            )
        ],
        layout={
            "title": "Snyk Issue Distribution by Latest Update Date (Title & Count)",
            "xaxis_title": "Latest Update Date",
            "yaxis_title": "Count",
            "hovermode": "closest",
        },
    )
    return figure


if __name__ == "__main__":
    app.run_server(debug=True)
