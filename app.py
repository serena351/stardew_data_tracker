import streamlit as st
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import sessionmaker
import pandas as pd
import os
import altair as alt
import matplotlib.pyplot as plt

# Load environment variables
FILEPATH = st.secrets('FILEPATH')
DATBASE_URL = st.secrets('DATABASE_URL')

# Load the save file
tree = ET.parse(FILEPATH)
root = tree.getroot()

# Extract data from the (XML) save file
player_name = root.find('player/name').text
farm_name = root.find('player/farmName').text
weather = root.find('./weatherForTomorrow').text
total_money = root.find('player/totalMoneyEarned').text
season = root.find('player/seasonForSaveGame').text
if season == '0':
    season = 'Spring'
elif season == '1':        
    season = 'Summer'
elif season == '2':
    season = 'Fall'
else:
    season = 'Winter'   
today = f"Day {root.find('player/dayOfMonthForSaveGame').text} of {season}"

# Main page
st.set_page_config(
    page_title="Stardew Valley Data Tracker", page_icon="🌿", initial_sidebar_state="collapsed"
)

# Background image
background_image = """
<style>
[data-testid="stAppViewContainer"] > .main {
    background-image: url("https://c4.wallpaperflare.com/wallpaper/361/395/783/stardew-valley-stars-simple-simple-background-space-hd-wallpaper-preview.jpg");
    background-size: 100vw 100vh;  
    background-position: center;  
    background-repeat: no-repeat;
}
</style>
"""

st.markdown(background_image, unsafe_allow_html=True)

input_style = """
<style>
input[type="text"] {
    background-color: transparent;
    color: #a19eae; 
}
div[data-baseweb="base-input"] {
    background-color: transparent !important;
}
[data-testid="stAppViewContainer"] {
    background-color: transparent !important;
}
</style>
"""
st.markdown(input_style, unsafe_allow_html=True)

# Main page
st.title("Stardew Valley Data Tracker")

col1, col2, col3 = st.columns([1, 2, 3])

with col1:
    st.subheader("Player Info")
    st.write(f"Player Name: {player_name}")
    st.write(f"Farm Name: {farm_name} Farm")
    st.write("Pet name: al (White Chicken)")

with col2:
    st.image("example.jpg", use_container_width=True)

with col3:
    st.subheader("Game Info") 
    st.write(f"Today: {today}")
    st.write(f"Total money earned: {total_money}g") # total money earned
    st.write(f"Weather for tomorrow: {weather}")

# Sidebar
st.sidebar.title("Stardew Valley Data Tracker")
st.sidebar.write("Welcome to the Stardew Valley Data Tracker!")
st.sidebar.write("What would you like to visualise?")

# Sidebar options
options = ["Money", "Friendships", "Health", "Experience Points"]
option = st.sidebar.selectbox("Select an option", options)

# Connect to database and load data into pandas dataframe then display depending on option selected
engine = create_engine(DATBASE_URL)
metadata = MetaData(schema='student')
Session = sessionmaker(bind=engine)
session = Session()
table = Table('stardew_data', metadata, autoload_with=engine)
query = session.query(table)
df = pd.read_sql(query.statement, query.session.bind)
st.write(df)    