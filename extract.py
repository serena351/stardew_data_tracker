import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import sessionmaker
import pandas as pd

# Load environment variables
load_dotenv()
FILEPATH = os.getenv('FILEPATH')
DATABASE_URL = os.getenv("DATABASE_URL")

# Load the save file
tree = ET.parse(FILEPATH)
root = tree.getroot()

# Extract data from the (XML) save file
day = root.find('player/dayOfMonthForSaveGame').text 
season = root.find('player/seasonForSaveGame').text
money = root.find('player/money').text # current amount of gold for that in-game day
al_friendship = root.find('.//friendshipTowardFarmer').text # al's friendship level
health = root.find('.//player/health').text # current health level
xp_list = root.findall('.//experiencePoints/int')
farming_xp = xp_list[0].text
mining_xp = xp_list[1].text
foraging_xp = xp_list[2].text
fishing_xp = xp_list[3].text
combat_xp = xp_list[4].text
friendships = root.find('player').find('friendshipData')
for item in friendships:
    character = item.find('key').find('string').text
    if character == 'Marnie':  # Replace 'Marnie' with the character you're looking for
        points = item.find('value').find('Friendship').find('Points').text

# Transform the data
if season == '0':
    season = 'Spring'
elif season == '1':        
    season = 'Summer'
elif season == '2':
    season = 'Fall'
else:
    season = 'Winter'                       
transformed_data = {'day': f"Day {day} of {season}", 
                    'money': int(money),
                    'al': int(al_friendship),
                    'health': int(health),
                    'farming_xp': int(farming_xp),
                    'mining_xp': int(mining_xp),
                    'foraging_xp': int(foraging_xp),
                    'fishing_xp': int(fishing_xp),
                    'combat_xp': int(combat_xp),
                    'marnie': int(points)}

# Load the data into PostgreSQL using SQLAlchemy

# Create an engine and metadata
engine = create_engine(DATABASE_URL)
metadata = MetaData(schema='student')

# Define the table
stats_table = Table(
    'stardew_data', metadata,
    Column('day', String, primary_key=True),
    Column('money', Integer),
    Column('al_friendship', Integer),
    Column('marnie_friendship', Integer),
    Column('health', Integer),
    Column('farming_xp', Integer),
    Column('mining_xp', Integer),
    Column('foraging_xp', Integer),
    Column('fishing_xp', Integer),
    Column('combat_xp', Integer)
)

# Create the table if it doesn't already exist
metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Insert data into the table
insert_query = stats_table.insert().values(
    day=transformed_data['day'],
    money=transformed_data['money'],
    al_friendship=transformed_data['al'],
    marnie_friendship=transformed_data['marnie'],
    health=transformed_data['health'],
    farming_xp=transformed_data['farming_xp'],
    mining_xp=transformed_data['mining_xp'],
    foraging_xp=transformed_data['foraging_xp'],
    fishing_xp=transformed_data['fishing_xp'],
    combat_xp=transformed_data['combat_xp']
)

# Execute the insert query
session.execute(insert_query)
session.commit()

# Close the session
session.close()

print("Data inserted successfully and table created in schema 'student'.")