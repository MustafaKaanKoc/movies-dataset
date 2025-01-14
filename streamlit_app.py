import altair as alt
import pandas as pd
import streamlit as st
import numpy as np
import seaborn as sns
import nbformat
import sqlite3
import matplotlib.pyplot as plt


# the following two funnctions are prepared by using ChatGPT to be able to display the content of notebook file inside the website.
def load_notebook(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)
    return notebook
def render_notebook(notebook):
    for cell in notebook['cells']:
        if cell['cell_type'] == 'markdown':
            st.markdown(cell['source'])
        elif cell['cell_type'] == 'code':
            st.code(cell['source'])
            if 'outputs' in cell:
                for output in cell['outputs']:
                    if 'text' in output:
                        st.text(output['text'])
                    elif 'data' in output and 'text/plain' in output['data']:
                        st.text(output['data']['text/plain'])



weather=pd.read_csv('warsaw.csv')
#this line was debbuged by chat GPT
weather['DATE']=pd.to_datetime(weather['DATE']).dt.date
#data cleaning
mean_PRCP=np.round(np.mean(weather.PRCP),2)
weather.PRCP=weather.PRCP.fillna(mean_PRCP)
weather.SNWD=weather.SNWD.fillna(0)
avg_tem_max_difference=np.round(np.mean(weather.TMAX-weather.TAVG),2)
weather.TMAX=weather.TMAX.fillna(np.round(weather.TAVG+avg_tem_max_difference,2))
avg_tem_min_difference=np.round(np.mean(weather.TAVG-weather.TMIN),2)
weather.TMIN=weather.TMIN.fillna(np.round(weather.TAVG-avg_tem_min_difference,2))

# Show the page title and description.
st.set_page_config(page_title="Warsaw Weather Forecasting", page_icon="⛅")
st.title("⛅ Warsaw Weather Forecasting")

#create database
conn = sqlite3.connect('weatherdata.db')
conn.close()
#creating connection to database
conn = sqlite3.connect('weatherdata.db')

#uploading database
weather.to_sql('weather', conn, if_exists='replace')

#closing connection
conn.close()
conn = sqlite3.connect('weatherdata.db')

c = conn.cursor()

#selecting every table from dataset
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()
for tableName in tables:
    print(tableName)

# We do not have to commit anything as we didn't make any changes.
conn.close()


conn = sqlite3.connect('weatherdata.db')
c = conn.cursor()

months_names=("january","february","march", "april","may","june","july","august","september","october","november","december")
for i in range(1, 13):
    table_name = f"{months_names[i-1]}_weather"
    month_number = f"{i:02d}"
    
    # this part is changed a bit by using ChatGPT not to create an already existing table.
    # it was not a problem when we were running in jupyter notebook since we could be able to run it once.
    # but we needed to check it if it already exist
    c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    table_exists = c.fetchone()  
    if not table_exists:
        c.execute(f"""
            CREATE TABLE "{table_name}" AS 
            SELECT * FROM weather 
            WHERE strftime('%m', DATE) = '{month_number}';
        """)
    

conn.commit()
conn.close()

conn = sqlite3.connect('weatherdata.db')

c = conn.cursor()

#selecting every table from dataset
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()
for tableName in tables:
    print(tableName)

# We do not have to commit anything as we didn't make any changes.
conn.close()
conn = sqlite3.connect('weatherdata.db')
c = conn.cursor()

# this part is changed a bit by using ChatGPT not to create an already existing table.
# it was not a problem when we were running in jupyter notebook since we could be able to run it once.
# but we needed to check it if it already exist
for i in range(1993, 2023):
    table_name = f"{i}_weather"    
    c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    table_exists = c.fetchone()    
    if not table_exists:
        c.execute(f"""
            CREATE TABLE "{table_name}" AS 
            SELECT * FROM weather 
            WHERE strftime('%Y', DATE) = '{i}';
        """)
    

conn.commit()
conn.close()
conn = sqlite3.connect('weatherdata.db')

c = conn.cursor()

#selecting every table from dataset
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()
for tableName in tables:
    print(tableName)

# We do not have to commit anything as we didn't make any changes.
conn.close()

# Connect to the SQLite database
conn = sqlite3.connect('weatherdata.db')
c = conn.cursor()

# Table name for February weather
table_name = '1993_weather'

# Inspect the first 5 rows of data from the table
c.execute(f"SELECT * FROM '{table_name}' lIMIT 300;")
rows = c.fetchall()
print(f"Sample data from '{table_name}':")
for row in rows:
    print(row)

# Close the connection
conn.close()
conn = sqlite3.connect('weatherdata.db')
c = conn.cursor()

# this part is changed a bit by using ChatGPT not to create an already existing table.
# it was not a problem when we were running in jupyter notebook since we could be able to run it once.
# but we needed to check it if it already exist
snowy_days = "snowy_days"
c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{snowy_days}';")
table_exists = c.fetchone()
if not table_exists:
    c.execute("""
        CREATE TABLE snowy_days AS 
        SELECT * FROM weather 
        WHERE SNWD > 0;
    """)
    



conn.commit()
conn.close()

conn = sqlite3.connect('weatherdata.db')
c = conn.cursor()

frosty_days = "frosty_days"
# this part is changed a bit by using ChatGPT not to create an already existing table.
# it was not a problem when we were running in jupyter notebook since we could be able to run it once.
# but we needed to check it if it already exist
c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{frosty_days}';")
table_exists = c.fetchone()
if not table_exists:
    c.execute("""
        CREATE TABLE frosty_days AS 
        SELECT * FROM weather 
        WHERE TAVG < 0;
    """)


conn.commit()
conn.close()


#FORECASTING FUNCTIONS
def avg (numbers):
        return round(sum(numbers)/len(numbers),1)
        
def forecast_for_day (date):
    past_temperatures = past_property_for_date(date, "TAVG")
    past_precipitation = past_property_for_date(date, "PRCP")
    past_snow_depth = past_property_for_date(date, "SNWD")
    precipitation_probability = len(list(filter(lambda x: x > 0, past_precipitation)))/len(past_precipitation)
    return avg(past_temperatures), avg(past_precipitation), avg(past_snow_depth), round(precipitation_probability, 4)

def past_property_for_date (date, prop):
    target_day = date.day
    target_month = date.month
    return weather[weather["DATE"].apply(lambda x: x.day == target_day and x.month == target_month)][prop].tolist()

def get_desc_for_prcp (prcp):
    if prcp > 0.5:
        return "High chance of precipitation - better to stay inside today!"
    elif prcp > 0.2:
        return "Moderate chance of precipitation - take an umbrella with you!"
    return "Low chance of precipitation - enjoy your day!"

def get_desc_for_temp (temp):
    if temp > 19:
        return "Hot day ahead! Stay hydrated!"
    elif temp > 13:
        return "Comfortably warm weather"
    elif temp > 7:
        return "Mild weather today. A light jacket should do!"
    elif temp >= 0:
        return "Cool weather. A scarf and gloves might come in handy!"
    return "It's frosty outside. Dress in layers and stay cozy!"


temperature, precipitation, snow_depth, precipitation_probability = forecast_for_day(pd.Timestamp(year=2025, month=7, day=3))

print("Temperature:", temperature)
print(get_desc_for_temp(temperature))
print("Precipitation:", precipitation, "\nPrecipitation probability:", precipitation_probability*100, "%")
print(get_desc_for_prcp(precipitation_probability))
print("Snow depth:", snow_depth)




st.write("""
    This app allow you to display the previous data and forecast a specific date's weather!
    """)

# the component that seperates the tabs
navigation = st.radio(
    "Navigation",
    ["Home", "Visualization","Notebook", "Forecasting"],
    horizontal=True,
)



# home page that contains description about the website
if navigation == "Home":
    st.title("Home")
    st.write(""" 🌦️ Your Weather Companion

    Weather shapes our daily decisions, from what to wear to planning outdoor activities. That’s why we’re creating a simple yet powerful weather app to help you prepare for whatever the skies have in store.

    This app uses the “Warsaw Weather Daily” dataset to deliver forecasts based on historical weather patterns. With detailed information such as:

    📅 Measurement Date (YYYY-MM-DD)
             
    📍 Station Details (ID, Name, Latitude, Longitude, Elevation)
             
    🌧️ Precipitation
             
    ❄️ Snow Depth
             
    🌡️ Temperatures (Average, Maximum, Minimum)
             
    Our goal is to transform this data into actionable insights for you, so you’re ready for sunny skies, snowy days, or anything in between.

    Stay prepared. Stay ahead. Stay weather-wise. 🌈""")
    
# visualization page that shows some graphs for the historical data
elif navigation == "Visualization":

    #a sub navigation component to seperate the visuals categoraically
    navigation2 = st.radio(
        "Heatmap / Yearly / Monthly",
        ["Heatmap","Yearly", "Monthly"],
        horizontal=True,    
    )

    conn = sqlite3.connect('weatherdata.db')
    c = conn.cursor()

    months_names=('january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december')

    #we create a loop in order to get seperate data frames for each month
    for month in months_names:
        data = f'SELECT DATE, PRCP, SNWD, TAVG, TMAX, TMIN FROM {month}_weather'
        #the line of code below was developed with the help of chat GPT
        globals()[f"{month}_data"] = pd.read_sql_query(data, conn)

    conn.close()

    print(january_data.head())
    
    for month in months_names:
        month_data = globals()[f'{month}_data']
        month_data['DATE'] = pd.to_datetime(month_data['DATE'])
        month_data['YEAR'] = month_data['DATE'].dt.year
        month_data['MONTH'] = month_data['DATE'].dt.month
        month_data['MAVG'] = month_data.groupby(['YEAR', 'MONTH'])['TAVG'].transform('mean').round(2)
        month_data['M_D'] = month_data['DATE'].dt.strftime('%m-%d')
        month_data['DAVG'] = month_data.groupby('M_D')['TAVG'].transform('mean').round(2)
        month_data['AVG_PRCP'] = month_data.groupby('M_D')['PRCP'].transform('mean').round(2)

    print(january_data.head(40))

    years = range(1993, 2023)
    
    #graphs for yearly data
    if navigation2 == "Yearly":
        years = [1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]
        user_year = st.selectbox("Pick a year between 1993-2022:",years)     
        st.title("Yearly Visualization")
        if 1993 <= int(user_year) <= 2022:

            #graph of average temperature graph
            user_year = int(user_year)  
            st.subheader("Average Temperature Graph")       
            plt.figure(figsize=(12, 6))            
            for month in months_names:
                month_data = globals()[f'{month}_data']
                month_year_data = month_data[month_data['YEAR'] == user_year]
                plt.plot(month_year_data['DATE'], month_year_data['TAVG'], label=month.capitalize())
            
            plt.title(f'Average Temperature Trends for {user_year}')
            plt.xlabel('Date')
            plt.ylabel('Average Temperature')
            plt.legend(loc='upper right', ncol=2)
            plt.grid(True)
            
            st.pyplot(plt)
            plt.clf() 

            #graph of snow depth

            st.subheader("Snow Depth Graph")
            plt.figure(figsize=(12,6))            
            for month in months_names:
                month_data = globals()[f'{month}_data']
                month_year_data = month_data[month_data['YEAR'] == user_year]
                plt.plot(month_year_data['DATE'], month_year_data['SNWD'], label=month.capitalize())
                
            plt.title(f'Snow depth for {user_year}')
            plt.xlabel('Date')
            plt.ylabel('Snow depth')
            plt.legend(loc='upper right', ncol=2)
            plt.grid(True)
            st.pyplot(plt)
            plt.clf()
        
        #precipitation plot is created in here
        if user_year: 
            user_year = int(user_year) 
            st.subheader("Precipitation Graph")

            plt.figure(figsize=(12, 6))

            for month in months_names:
                month_data = globals()[f'{month}_data']
                month_year_data = month_data[month_data['DATE'].dt.year == user_year]
                plt.plot(month_year_data['DATE'], month_year_data['PRCP'], label=month.capitalize())

            plt.title(f'Precipitation in {user_year}')
            plt.xlabel('Date')
            plt.ylabel('Precipitation')
            plt.legend(loc='upper right', ncol=2)
            plt.grid(True)
            st.pyplot(plt)
            plt.clf()
            
            
    if navigation2 == "Monthly":
        st.title("Monthly Visualization")
        years = [1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]
        user_year = st.selectbox("Pick a year between 1993-2022:",years)        
        user_month = st.selectbox("Pick a month:", months_names)

        user_year = int(user_year)
        for month in months_names:                        
            if month == user_month:
                st.subheader("Average Temperature Graph")
                plt.figure(figsize=(10, 4))
                month_year_data = globals()[f'{month}_data'][
                globals()[f'{month}_data']['DATE'].dt.year == user_year]

                plt.plot(
                    month_year_data['DATE'].dt.strftime('%d-%m'),
                    month_year_data['DAVG'],
                    label=f"{month.capitalize()} {user_year}",
                )
                plt.title(f'Average Temperature for {month.capitalize()} {user_year}')
                plt.xlabel('Date')
                plt.ylabel('Average Temperature')
                plt.xticks(rotation=45)
                plt.grid(True)
                st.pyplot(plt)                                
                plt.clf()


                # precipitation data
                st.subheader("Average Precipitation Graph")

                plt.plot(
                    month_year_data['DATE'].dt.strftime('%d-%m'),
                    month_year_data['AVG_PRCP'],
                    label=f"{month.capitalize()} {user_year}",
                )
                plt.title(f'Average Precipitation for {month.capitalize()} {user_year}')
                plt.xlabel('Date')
                plt.ylabel('Precipitation (mm)')
                plt.xticks(rotation=45)
                plt.grid(True)
                st.pyplot(plt)                
                plt.clf()
    #heatmap graph creation
    if navigation2 == "Heatmap":
        st.title("Heatmap")
        mavg_data = {}

        for month in months_names:
            month_data = globals()[f'{month}_data']
            yearly_avg = month_data.groupby('YEAR')['MAVG'].mean()
            mavg_data[month] = yearly_avg

        mavg = pd.DataFrame(mavg_data)

        plt.figure(figsize=(20,12))
        sns.heatmap(mavg.T, annot=True, cmap='coolwarm', linewidths=0.5, cbar_kws={'label': 'Average Temperature'})
        plt.title('Heatmap: Average Monthly Temperatures (1993-2024)')
        plt.xlabel('Year')
        plt.ylabel('Month')
        plt.yticks(ticks=range(12), labels=[month.capitalize() for month in months_names])
        st.pyplot(plt)
        plt.clf()

# notebook tab contains the jupyter notebook content

elif navigation == "Notebook":
    st.subheader("Jupyter Notebook Content of The Website")
    st.warning("""In this tab, the content of notebobok file is displayed. 
               Also some of the print statements are visible in this page.
                However, graphs are not visible in this tab. You need to visit the 'visualization' tab to see them.""")
    notebook = load_notebook("weather-app.ipynb" )
    render_notebook(notebook)
    

# forecasting tab

elif navigation=="Forecasting":    

    st.title("Forecasting")
    user_date = st.date_input("Select a date to forecast:", min_value=pd.Timestamp.today())
    
    if user_date:
        temperature, precipitation, snow_depth, precipitation_probability = forecast_for_day(user_date)

        st.subheader(f"Weather Forecast for {user_date.strftime('%B')} {user_date.year}")
        
        st.write(f"**Temperature**: {temperature}°C")
        st.write("-",get_desc_for_temp(temperature))
        st.write(f"**Precipitation**: {precipitation} mm")
        st.write(f"**Precipitation Probability**: {precipitation_probability * 100}%")
        st.write("-",get_desc_for_prcp(precipitation_probability))
        st.write(f"**Snow Depth**: {snow_depth} cm")
    
    


