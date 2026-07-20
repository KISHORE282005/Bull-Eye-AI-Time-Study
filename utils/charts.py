import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


##############################################################
# VA vs NVA
##############################################################

def va_nva_chart(overall):

    values = [
        overall["estimated_value_added_time"],
        overall["estimated_non_value_added_time"]
    ]

    labels = [
        "Value Added",
        "Non Value Added"
    ]

    fig = px.pie(
        names=labels,
        values=values,
        hole=0.55,
        title="Value Added vs Non Value Added"
    )

    fig.update_traces(
        textinfo="percent+label"
    )

    return fig


##############################################################
# Timeline Chart
##############################################################

def timeline_chart(df):

    fig = px.timeline(

        df,

        x_start="start_timestamp",

        x_end="end_timestamp",

        y="process_name",

        color="value_added",

        title="Process Timeline"

    )

    fig.update_yaxes(
        autorange="reversed"
    )

    return fig


##############################################################
# KPI Gauge
##############################################################

def efficiency_gauge(va_percent):

    fig = go.Figure(

        go.Indicator(

            mode="gauge+number",

            value=va_percent,

            title={"text":"Efficiency %"},

            gauge={

                "axis":{"range":[0,100]}

            }

        )

    )

    return fig