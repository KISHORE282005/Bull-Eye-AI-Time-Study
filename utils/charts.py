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
# Waste Chart
##############################################################

def waste_chart(df):

    if "waste_type" not in df.columns:
        return go.Figure()

    waste = df.copy()

    waste = waste[
        waste["waste_type"] != ""
    ]

    if len(waste) == 0:
        return go.Figure()

    chart = (
        waste["waste_type"]
        .value_counts()
        .reset_index()
    )

    chart.columns = [
        "Waste",
        "Count"
    ]

    fig = px.bar(
        chart,
        x="Waste",
        y="Count",
        text="Count",
        title="Waste Distribution"
    )

    return fig


##############################################################
# Duration Chart
##############################################################

def duration_chart(df):

    fig = px.bar(

        df,

        x="process_name",

        y="duration_seconds",

        color="value_added",

        title="Process Duration"

    )

    fig.update_layout(
        xaxis_title="Process",
        yaxis_title="Seconds"
    )

    return fig


##############################################################
# Confidence Chart
##############################################################

def confidence_chart(df):

    fig = px.line(

        df,

        x="process_no",

        y="confidence",

        markers=True,

        title="AI Confidence"

    )

    fig.update_layout(
        yaxis_range=[0,1]
    )

    return fig


##############################################################
# Activity Chart
##############################################################

def activity_chart(df):

    chart = (

        df["process_name"]

        .value_counts()

        .reset_index()

    )

    chart.columns = [
        "Process",
        "Count"
    ]

    fig = px.bar(

        chart,

        x="Process",

        y="Count",

        text="Count",

        title="Activities Detected"

    )

    return fig


##############################################################
# Timeline Chart
##############################################################

def timeline_chart(df):

    fig = px.timeline(

        df,

        x_start="start_time",

        x_end="end_time",

        y="process_name",

        color="value_added",

        title="Process Timeline"

    )

    fig.update_yaxes(
        autorange="reversed"
    )

    return fig


##############################################################
# Tool Usage
##############################################################

def tool_chart(df):

    if "tools_used" not in df.columns:

        return go.Figure()

    tools = []

    for row in df["tools_used"]:

        if isinstance(row,list):

            tools.extend(row)

    if len(tools)==0:

        return go.Figure()

    chart = pd.Series(

        tools

    ).value_counts().reset_index()

    chart.columns = [

        "Tool",

        "Count"

    ]

    fig = px.bar(

        chart,

        x="Tool",

        y="Count",

        title="Tools Used"

    )

    return fig


##############################################################
# Machine Usage
##############################################################

def machine_chart(df):

    if "machine_used" not in df.columns:

        return go.Figure()

    chart = (

        df["machine_used"]

        .value_counts()

        .reset_index()

    )

    chart.columns=[

        "Machine",

        "Count"

    ]

    fig = px.bar(

        chart,

        x="Machine",

        y="Count",

        title="Machine Usage"

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