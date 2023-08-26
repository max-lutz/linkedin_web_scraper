'''
Streamlit app to download recent job offers from linkedin based on keyword given by the user

Usage: 
streamlit run monitoring_app.py
'''


import os
import json
import requests
import pandas as pd
from tqdm import tqdm

import streamlit as st
import time
import plotly.express as px


# configuration of the page
st.set_page_config(layout="wide")


SPACER = .2
ROW = 1

title_spacer1, title, title_spacer_2 = st.columns((.1, ROW, .1))
with title:
    st.title('Linkedin web-scraper')
    st.markdown("""
            This app allows you scrape job offers from Linkedin
            * The code can be accessed at [code](https://github.com/max-lutz/linkedin_web_scraper).
            * Click on how to use this app to get more explanation.
            """)

title_spacer2, title_2, title_spacer_2 = st.columns((.1, ROW, .1))
with title_2:
    with st.expander("How to use this app"):
        st.markdown("""
            This app allows you to interact with a salary prediction model hosted on AWS. \n\n
            The menu on the left allows you to predict the salary based on the inputs. \n\n
            If you click on the button "Run aws api test", the app makes 15 predictions using the api and display some
            data used to monitor the api.
            """)
        st.write("")

st.sidebar.header('Web scraper inputs')
title = st.sidebar.text_input('Job title', placeholder="Data analyst")
location = st.sidebar.text_input('Location (City, State)', placeholder="Chicago")
experience = st.sidebar.selectbox(
    'Experience level', ['ENTRY_LEVEL', 'ASSOCIATE', 'MID_SENIOR', 'DIRECTOR', 'EXECUTIVE'])
number_of_scrape = st.sidebar.slider('Number of job offers to scrape', 5, 100, 10)
st.sidebar.write("")
run_web_scraper = st.sidebar.button("Run web scraper")


if (run_web_scraper):
    placeholder = st.empty()

    with placeholder:
        st.write("Web scraper is running...")
