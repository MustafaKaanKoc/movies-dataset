import altair as alt
import pandas as pd
import streamlit as st

# Show the page title and description.
st.set_page_config(page_title="Movies dataset", page_icon="⛅")
st.title("⛅ Warsaw Weather Forecasting")
st.write(
    """
    This app allow you to display the previous data and forecast a specific date's weather!
    """
)

# Horizontal navigation using `st.radio`
navigation = st.radio(
    "Navigation",
    ["Home", "Forecasting", "About"],
    horizontal=True,  # Enables horizontal layout
)

# Content for each page
if navigation == "Home":
    st.title("Home")
    st.write("Welcome to the Movies Dataset App!")
    # Load the data from a CSV. We're caching this so it doesn't reload every time the app
    # reruns (e.g. if the user interacts with the widgets).
    @st.cache_data
    def load_data():
        df = pd.read_csv("data/movies_genres_summary.csv")
        return df


    df = load_data()

    # Show a multiselect widget with the genres using `st.multiselect`.
    genres = st.multiselect(
        "Genres",
        df.genre.unique(),
        ["Action", "Adventure", "Biography", "Comedy", "Drama", "Horror"],
    )

    # Show a slider widget with the years using `st.slider`.
    years = st.slider("Years", 1986, 2006, (2000, 2016))

    # Filter the dataframe based on the widget input and reshape it.
    df_filtered = df[(df["genre"].isin(genres)) & (df["year"].between(years[0], years[1]))]
    df_reshaped = df_filtered.pivot_table(
        index="year", columns="genre", values="gross", aggfunc="sum", fill_value=0
    )
    df_reshaped = df_reshaped.sort_values(by="year", ascending=False)


    # Display the data as a table using `st.dataframe`.
    st.dataframe(
        df_reshaped,
        use_container_width=True,
        column_config={"year": st.column_config.TextColumn("Year")},
    )

    # Display the data as an Altair chart using `st.altair_chart`.
    df_chart = pd.melt(
        df_reshaped.reset_index(), id_vars="year", var_name="genre", value_name="gross"
    )
    chart = (
        alt.Chart(df_chart)
        .mark_line()
        .encode(
            x=alt.X("year:N", title="Year"),
            y=alt.Y("gross:Q", title="Gross earnings ($)"),
            color="genre:N",
        )
        .properties(height=320)
    )
    st.altair_chart(chart, use_container_width=True)

elif navigation == "Forecasting":
    st.title("Forecasting")
    st.write("Use this section to forecast weather based on historical data.")
    
    # Add a text input field for the user to enter a date to forecast
    forecast_date = st.text_input("Enter the date you want to forecast (YYYY-MM-DD):")
    
    if forecast_date:
        st.write(forecast_date)

elif navigation == "About":
    st.title("About")
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
    


