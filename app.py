'''
Streamlit app to download recent job offers from linkedin based on keyword given by the user

Usage: 
streamlit run app.py
'''

import os
import json
import pandas as pd
import streamlit as st
import requests
import wget
import zipfile
import os
import time
from threading import Thread
from streamlit.runtime.scriptrunner import add_script_run_ctx


from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData, EventMetrics
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import RelevanceFilters, TypeFilters, ExperienceLevelFilters

EXP_LVL_STR = ['ENTRY_LEVEL', 'ASSOCIATE', 'MID_SENIOR', 'DIRECTOR', 'EXECUTIVE']
EXP_LVL_CLASS = [ExperienceLevelFilters.ENTRY_LEVEL, ExperienceLevelFilters.ASSOCIATE,
                 ExperienceLevelFilters.MID_SENIOR, ExperienceLevelFilters.DIRECTOR, ExperienceLevelFilters.EXECUTIVE]
EXP_LVL_INDEX = 0
search_keyword = ''
rows = []
progress = 0
n_queries = 10


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


def print_df():
    st.write(pd.DataFrame(rows, columns=['search_keyword', 'title', 'company', 'link', 'location',
                                         'description', 'date', 'experience']))


def display_placeholder(display_dowload_button=False):
    global placeholder
    global n_queries
    global rows
    with placeholder.container():
        st.write("")
        spacer1, row_1, spacer_2 = st.columns((.1, ROW, .1))
        progress = len(rows)
        with row_1:
            if (progress == n_queries):
                st.write("Web scraping complete")
            else:
                st.write("Web scraper is running...")
            st.progress(progress/n_queries)

            st.write("")
            df = pd.DataFrame(rows, columns=['search_keyword', 'title', 'company', 'link', 'location',
                                             'description', 'date', 'experience'])
            if (len(df) > 0):
                st.write(df)

            if (display_dowload_button):
                st.write("")
                csv = convert_df(df)

                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name='linkedin_job_offers.csv',
                    mime='text/csv',
                )


def get_latest_driver():
    if (not os.path.exists(os.path.join(os.getcwd(), 'chromedriver-linux64', 'chromedriver'))):
        # get the latest chrome driver version number
        url = 'https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json'
        response = requests.get(url)
        version_number = json.loads(response.text)['channels']['Stable']['version']

        print(version_number)

        # build the donwload url
        download_url = "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/" + \
            version_number + "/linux64/chromedriver-linux64.zip"

        # download the zip file using the url built above
        latest_driver_zip = wget.download(download_url, 'chromedriver.zip')

        # extract the zip file
        with zipfile.ZipFile(latest_driver_zip, 'r') as zip_ref:
            zip_ref.extractall()  # you can specify the destination folder path here
        # delete the zip file downloaded above
        os.remove(latest_driver_zip)
        os.chmod(os.path.join(os.getcwd(), 'chromedriver-linux64', 'chromedriver'), 0o777)


def get_scrapper(slow):
    return LinkedinScraper(
        # Custom Chrome executable path (e.g. /foo/bar/bin/chromedriver)
        chrome_executable_path=os.path.join(os.getcwd(), 'chromedriver-linux64', 'chromedriver'),
        chrome_options=None,  # Custom Chrome options here
        headless=True,  # Overrides headless mode only if chrome_options is None
        # How many threads will be spawned to run queries concurrently (one Chrome driver for each thread)
        max_workers=3,
        slow_mo=slow,  # Slow down the scraper to avoid 'Too many requests 429' errors (in seconds)
        page_load_timeout=40  # Page load timeout (in seconds)
    )


# Fired once for each page (25 jobs)
def on_metrics(metrics: EventMetrics):
    print('[ON_METRICS]', str(metrics))


def on_error(error):
    print('[ON_ERROR]', error)


def on_end():
    print('[ON_END]')


def run_query(scraper, keyword, location, experience_level, n_queries):
    queries = [
        Query(
            query=keyword,
            options=QueryOptions(
                locations=[location],
                apply_link=False,
                skip_promoted_jobs=True,
                page_offset=0,
                limit=n_queries,
                filters=QueryFilters(
                    relevance=RelevanceFilters.RECENT,
                    type=[TypeFilters.FULL_TIME],
                    experience=[experience_level]
                )
            )
        ),
    ]

    scraper.run(queries)


# configuration of the page
st.set_page_config(layout="wide")
SPACER = .2
ROW = 1

get_latest_driver()

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
n_queries = st.sidebar.slider('Number of job offers to scrape', 5, 100, 10)
st.sidebar.write("")
run_web_scraper = st.sidebar.button("Run web scraper")


placeholder = st.empty()


def on_data(data: EventData):
    print('[ON_DATA]')
    rows.append([search_keyword, data.title, data.company, data.link, data.place, data.description,
                data.date, EXP_LVL_STR[EXP_LVL_INDEX]])

    # thread = Thread(target=display_placeholder)
    # add_script_run_ctx(thread)
    # thread.start()
    # thread.join()
    # display_placeholder()


if (run_web_scraper):

    scraper = get_scrapper(2)

    # Add event listeners
    scraper.on(Events.DATA, on_data)
    scraper.on(Events.ERROR, on_error)
    scraper.on(Events.END, on_end)

    search_keyword = title
    EXP_LVL_INDEX = EXP_LVL_STR.index(experience)
    thread = Thread(target=run_query, args=(scraper, title, location, EXP_LVL_CLASS[EXP_LVL_INDEX], n_queries))
    # st.scriptrunner.add_script_run_ctx(thread)
    thread.start()

    # run_query(scraper, title, location, EXP_LVL_CLASS[EXP_LVL_INDEX], n_queries)

    while (len(rows) != n_queries):
        display_placeholder(display_dowload_button=False)
        time.sleep(1)

    placeholder.empty()
    display_placeholder(display_dowload_button=True)

    thread.join()
