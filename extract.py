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

money = root.find('player/money').text # current amount of gold for that (in-game) day

al_friendship = root.find('.//friendshipTowardFarmer').text # al's friendship points
friendships = root.find('player').find('friendshipData')
for item in friendships:
    character = item.find('key').find('string').text
    if character == 'Marnie':  
        points = item.find('value').find('Friendship').find('Points').text # friendship points for Marnie

xp_list = root.findall('.//experiencePoints/int') # list of experience points for each skill
farming_xp = xp_list[0].text
mining_xp = xp_list[1].text
foraging_xp = xp_list[2].text
fishing_xp = xp_list[3].text
combat_xp = xp_list[4].text
        
for item in root.findall('player/stats/Values/item'):
    key = item.find('./key/string').text
    if key == 'diamondsFound':
        diamonds_found = int(item.find('./value/unsignedInt').text)
    elif key == 'cropsShipped':
        crops_shipped = int(item.find('./value/unsignedInt').text)
    elif key == 'fishCaught':   
        fish_caught = int(item.find('./value/unsignedInt').text)
    elif key == 'itemsForaged':
        items_foraged = int(item.find('./value/unsignedInt').text)
    elif key == 'monstersKilled':
        monsters_killed = int(item.find('./value/unsignedInt').text)
    elif key == 'rocksCrushed':
        rocks_crushed = int(item.find('./value/unsignedInt').text)
    elif key == 'seedsSown':
        seeds_sown = int(item.find('./value/unsignedInt').text)
    elif key == 'giftsGiven':
        gifts_given = int(item.find('./value/unsignedInt').text)
    elif key == 'chickenEggsLayed':
        eggs = int(item.find('./value/unsignedInt').text)

for item in root.findall('player/friendshipData/item'):
    key = item.find('./key/string').text
    if key == 'Marnie':
        gifts_this_week = int(item.find('value/Friendship/GiftsThisWeek').text)
        gifts_today = int(item.find('value/Friendship/GiftsToday').text)
        talked_today = item.find('value/Friendship/TalkedToToday').text

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
    'stardew_data_tracker', metadata,
    Column('day', String, primary_key=True),
    Column('money', Integer),
    Column('al_friendship', Integer),
    Column('marnie_friendship', Integer),
    Column('farming_xp', Integer),
    Column('mining_xp', Integer),
    Column('foraging_xp', Integer),
    Column('fishing_xp', Integer),
    Column('combat_xp', Integer),
    Column('diamonds_found', Integer),
    Column('crops_shipped', Integer),
    Column('fish_caught', Integer),
    Column('items_foraged', Integer),
    Column('monsters_killed', Integer),
    Column('rocks_crushed', Integer),
    Column('seeds_sown', Integer),
    Column('gifts_given', Integer),
    Column('chicken_eggs_layed', Integer),
    Column('gifts_this_week', Integer),
    Column('gifts_today', Integer),
    Column('talked_to_today', String)
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
    farming_xp=transformed_data['farming_xp'],
    mining_xp=transformed_data['mining_xp'],
    foraging_xp=transformed_data['foraging_xp'],
    fishing_xp=transformed_data['fishing_xp'],
    combat_xp=transformed_data['combat_xp'],
    diamonds_found=diamonds_found,
    crops_shipped=crops_shipped,
    fish_caught=fish_caught,
    items_foraged=items_foraged,
    monsters_killed=monsters_killed,
    rocks_crushed=rocks_crushed,
    seeds_sown=seeds_sown,
    gifts_given=gifts_given,
    chicken_eggs_layed=eggs,
    gifts_this_week=gifts_this_week,
    gifts_today=gifts_today,
    talked_to_today=talked_today
)

# Execute the insert query
session.execute(insert_query)
session.commit()

# Close the session
session.close()

print("Data inserted successfully and table created/updated in schema 'student'.")