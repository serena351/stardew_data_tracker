import streamlit as st
import xml.etree.ElementTree as ET
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import sessionmaker
# from dotenv import load_dotenv   # use when running app locally
import pandas as pd
import os
import altair as alt
import base64

# Load environment variables
FILEPATH = st.secrets['FILEPATH']
DATBASE_URL = st.secrets['DATABASE_URL']    

# # Load environment variables                        # use this instead when running app locally 
# load_dotenv()
# FILEPATH = os.getenv('FILEPATH')
# DATBASE_URL = os.getenv('DATABASE_URL')        

# Load the save file
tree = ET.parse(FILEPATH)
root = tree.getroot()

# Extract data from the (XML) save file
player_name = root.find('player/name').text
farm_name = root.find('player/farmName').text
weather = root.find('./weatherForTomorrow').text
total_money = root.find('player/totalMoneyEarned').text
luck = root.find('dailyLuck').text 
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
    page_title="Stardew Valley Data Tracker 📈", page_icon="🌿", initial_sidebar_state="auto", layout="wide"
)

# Background image

def set_bg_hack_url():
    '''
    A function to unpack an image from url and set as bg.
    Returns
    -------
    The background.
    '''
        
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url("https://c4.wallpaperflare.com/wallpaper/361/395/783/stardew-valley-stars-simple-simple-background-space-hd-wallpaper-preview.jpg");
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

set_bg_hack_url()

# Main page
st.title("Stardew Valley Data Tracker 📈")

col1, col2, col3 = st.columns([1, 2, 3])

with col2:
    st.subheader("Player Info")
    st.write(f"Player name: {player_name}")
    st.write(f"Farm name: {farm_name} Farm")
    st.write("Farm animals: al (White Chicken) 🐔")

with col1:
    st.image("static/afi.png", use_container_width=False, width=150)   # can be replaced by a screenshot of your character image

with col3:
    st.subheader("Game Info") 
    st.write(f"Today: {today} 🌅")
    st.write(f"Total money earned: {total_money}g 🪙")
    st.write(f"Daily luck: {luck} 🍀")
    st.write(f"Weather for tomorrow: {weather} 🌦️")

# Sidebar background image

def sidebar_bg(side_bg):

   side_bg_ext = 'jpg'

   st.markdown(
      f"""
      <style>
      [data-testid="stSidebar"] > div:first-child {{
          background: url(data:image/{side_bg_ext};base64,{base64.b64encode(open(side_bg, "rb").read()).decode()});
      }}
      </style>
      """,
      unsafe_allow_html=True,
      )

side_bg = 'static/bg.jpg'
sidebar_bg(side_bg)

# Sidebar
st.sidebar.title("Stardew Valley Data Tracker")
st.sidebar.write("Welcome to the Stardew Valley Data Tracker!")
st.sidebar.write("What would you like to visualise?")

# Sidebar options
options = ["Money", "Friendship with Marnie", "Experience Points", "Pet Friendship"]
option = st.sidebar.selectbox("Select an option", options)

# Connect to database and load data into pandas dataframe
engine = create_engine(DATBASE_URL)
metadata = MetaData(schema='student')
Session = sessionmaker(bind=engine)
session = Session()
table = Table('stardew_data_tracker', metadata, autoload_with=engine)
query = session.query(table)
df = pd.read_sql(query.statement, query.session.bind)

# Create 'date' column for correct ordering 
df['date'] = df['day'].str.extract(r'(\d+)').astype(int) 

# Visualisations for each option selected
if option == "Money":
    st.subheader("Money 🪙")
    st.write("Visualising the money data:")
    st.write("Money earned over time")
    chart = (alt.Chart(df).mark_line().encode(x=alt.X('day:O', title='Day', sort=df['date']), y=alt.Y('money', title='Current Earnings', scale=alt.Scale(domain=[20000, 30000]))) +
    alt.Chart(df).mark_circle(size=50).encode(x=alt.X('day:O', sort=df['date']), y='money', tooltip=['day', 'money', 'crops_shipped']))
    st.write(chart)
    
elif option == "Friendship with Marnie":
    st.subheader("Friendship with Marnie 💚")
    st.write("Visualising the friendship data:")
    st.write("Friendship with Marnie over time")
    chart = (alt.Chart(df).mark_line().encode(x=alt.X('day:O', title='Day', sort=df['date']), y=alt.Y('marnie_friendship', title='Friendship Points', scale=alt.Scale(domain=[1100, 1400]))) +
             alt.Chart(df).mark_circle(size=50).encode(x=alt.X('day:O', sort=df['date']), y='marnie_friendship', tooltip=['day', 'marnie_friendship', 'gifts_given', 'gifts_this_week', 'gifts_today', 'talked_to_today']))
    st.write(chart)

elif option == "Experience Points":
    skills = ["Farming", "Mining", "Foraging", "Fishing", "Combat"]
    skill = st.selectbox("Select a skill", skills)
    st.subheader("Experience Points 🏅")   
    if skill == "Farming":
        st.write("Visualising the farming data:")
        st.write("Farming experience points over time 🌱")
        chart = (alt.Chart(df).mark_line().encode(x=alt.X('day:O', title='Day', sort=df['date']), y=alt.Y('farming_xp', title='Farming XP', scale=alt.Scale(domain=[6300, 7400]))) +
                alt.Chart(df).mark_circle(size=50).encode(x=alt.X('day:O', sort=df['date']), y='farming_xp', tooltip=['day', 'farming_xp', 'seeds_sown', 'chicken_eggs_layed']))
        st.write(chart)
    elif skill == "Mining":
        st.write("Visualising the mining data:")
        st.write("Mining experience points over time 💎")
        chart = (alt.Chart(df).mark_line().encode(x=alt.X('day:O', title='Day', sort=df['date']), y=alt.Y('mining_xp', title='Mining XP', scale=alt.Scale(domain=[11900, 12900]))) +
             alt.Chart(df).mark_circle(size=50).encode(x=alt.X('day:O', sort=df['date']), y='mining_xp', tooltip=['day', 'mining_xp', 'rocks_crushed', 'diamonds_found']))
        st.write(chart)
    elif skill == "Foraging":
        st.write("Visualising the foraging data:")
        st.write("Foraging experience points over time 🌲")
        chart = (alt.Chart(df).mark_line().encode(x=alt.X('day:O', title='Day', sort=df['date']), y=alt.Y('foraging_xp', title='Foraging XP', scale=alt.Scale(domain=[10100, 11100]))) +
                alt.Chart(df).mark_circle(size=50).encode(x=alt.X('day:O', sort=df['date']), y='foraging_xp', tooltip=['day', 'foraging_xp', 'items_foraged']))
        st.write(chart)
    elif skill == "Fishing":
        st.write("Visualising the fishing data:")
        st.write("Fishing experience points over time 🎣")
        chart = (alt.Chart(df).mark_line().encode(x=alt.X('day:O', title='Day', sort=df['date']), y=alt.Y('fishing_xp', title='Fishing XP', scale=alt.Scale(domain=[11400, 12000]))) +
                alt.Chart(df).mark_circle(size=50).encode(x=alt.X('day:O', sort=df['date']), y='fishing_xp', tooltip=['day', 'fishing_xp', 'fish_caught']))
        st.write(chart)
    else:
        st.write("Visualising the combat data:")
        st.write("Combat experience points over time 🗡️")
        chart = (alt.Chart(df).mark_line().encode(x=alt.X('day:O', title='Day', sort=df['date']), y=alt.Y('combat_xp', title = 'Combat XP', scale=alt.Scale(domain=[8600, 9000]))) +
                alt.Chart(df).mark_circle(size=50).encode(x=alt.X('day:O', sort=df['date']), y='combat_xp', tooltip=['day', 'combat_xp', 'monsters_killed']))
        st.write(chart)

else: 
    st.subheader("Pet Friendship")
    st.write("Visualising the pet friendship data:")
    st.write("Friendship with al over time 🐔")
    chart = (alt.Chart(df).mark_line().encode(x=alt.X('day:O', title='Day', sort=df['date']), y=alt.Y('al_friendship', title='Friendship Points', scale=alt.Scale(domain=[685, 805]))) +
             alt.Chart(df).mark_circle(size=50).encode(x=alt.X('day:O', sort=df['date']), y='al_friendship', tooltip=['day', 'al_friendship', 'chicken_eggs_layed']))
    st.write(chart)
