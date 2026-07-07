import streamlit as st


def load_css():

    st.markdown("""

<style>

/* -------------------------------------------------- */
/* Main Background */
/* -------------------------------------------------- */

.stApp{

    background-color:#FF0000;

}


/* -------------------------------------------------- */
/* Header */
/* -------------------------------------------------- */

.title{
    font-size:52px;
    font-weight:800;
    color:#D60000;
    line-height:1.1;
    letter-spacing:1px;
}

.subtitle{
    font-size:24px;
    font-weight:500;
    color:#444444;
    margin-top:8px;
}


/* -------------------------------------------------- */
/* KPI Cards */
/* -------------------------------------------------- */

.metric-card{

    background:white;

    border-radius:15px;

    padding:20px;

    box-shadow:0px 3px 10px rgba(0,0,0,.08);

}


/* -------------------------------------------------- */
/* Sidebar */
/* -------------------------------------------------- */

[data-testid="stSidebar"]{

    background:#0F172A;

}

[data-testid="stSidebar"] *{

    color:white;

}


/* -------------------------------------------------- */
/* Buttons */
/* -------------------------------------------------- */

.stButton>button{

    width:100%;

    border-radius:10px;

    background:#2563EB;

    color:white;

    border:none;

    height:45px;

    font-weight:600;

}

.stButton>button:hover{

    background:#1D4ED8;

}


/* -------------------------------------------------- */
/* Download Button */
/* -------------------------------------------------- */

.stDownloadButton>button{

    width:100%;

    border-radius:10px;

    height:45px;

}


/* -------------------------------------------------- */
/* Dataframe */
/* -------------------------------------------------- */

[data-testid="stDataFrame"]{

    border-radius:10px;

}


/* -------------------------------------------------- */
/* Metric */
/* -------------------------------------------------- */

[data-testid="metric-container"]{

    background:white;

    padding:15px;

    border-radius:12px;

    box-shadow:0px 2px 8px rgba(0,0,0,.08);

}


/* -------------------------------------------------- */
/* Success */
/* -------------------------------------------------- */

.stSuccess{

    border-radius:10px;

}


/* -------------------------------------------------- */
/* Warning */
/* -------------------------------------------------- */

.stWarning{

    border-radius:10px;

}


/* -------------------------------------------------- */
/* Info */
/* -------------------------------------------------- */

.stInfo{

    border-radius:10px;

}


/* -------------------------------------------------- */
/* Expander */
/* -------------------------------------------------- */

.streamlit-expanderHeader{

    font-size:18px;

    font-weight:bold;

}


/* -------------------------------------------------- */
/* Footer */
/* -------------------------------------------------- */

footer{

    visibility:hidden;

}


/* -------------------------------------------------- */
/* Streamlit Menu */
/* -------------------------------------------------- */

#MainMenu{

    visibility:hidden;

}

header{

    visibility:hidden;

}

</style>

""",
unsafe_allow_html=True)