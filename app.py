# Streamlit Project by Jonathan Smith
# Exploring Data from Department of Transportation 
# Domestic Airline Consumer Airfare Report
# https://www.transportation.gov/policy/aviation-policy/domestic-airline-consumer-airfare-report

# import required packages
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Streamlit page initialize
st.set_page_config('Consumer Airfare Report',
                   page_icon=':flight_arrival:',
                   layout='wide')

st.header('Data From USDoT Domestic Airline Consumer Airfare Report')

# Load dataset
# import the data
# @st.cache_data  # Add the caching decorator
# def load_data(url):
#     """Function reading .csv files."""
#     dframe = pd.read_csv(url, index_col=0)
#     return dframe


air_travel_df = pd.read_csv("./us_airfares_processed.csv")

#-----------------------------------------------------------------------------------------------------
# Raw Dataframe 

st.subheader('Dataset Viewer')
year_list = air_travel_df.year.sort_values().unique()
year_filter = st.selectbox('Select Year:', year_list, index=0)  #Select the year

air_travel_df.sort_values(by=['year', 'quarter'], inplace=True)
air_travel_df['year'] = air_travel_df['year'].astype(str) #can't get rid of thousands comma

st.dataframe(air_travel_df[air_travel_df['year']==year_filter.astype(str)], use_container_width=True)

#-----------------------------------------------------------------------------------------------------
# Histogram of Average Quarterly Passenger Volume per Route

st.subheader('Passenger Volume by City-Pair')
just_top_500 = st.checkbox('Limit data to top 500 routes',True)
air_travel_df['city-pair'] = air_travel_df['city1'] + \
              ' - ' + air_travel_df['city2']
pax_vol = air_travel_df.groupby('city-pair')\
                        .agg({'passengers':'mean'})\
                        .sort_values(by='passengers', ascending=False)\
                        .reset_index(drop=True)
if just_top_500:
    fig = px.histogram(pax_vol.head(500), x='passengers')
else:
    fig = px.histogram(pax_vol, x='passengers')

st.plotly_chart(fig, theme='streamlit', use_container_width=True)

#-----------------------------------------------------------------------------------------------------
# Scatterplot Revealing How Fares and Distance Interact

st.subheader('Miles vs. Fares')
air_travel_df['fare_per_mile'] = air_travel_df.fare / air_travel_df.nonstop_miles
air_travel_df['year'] = air_travel_df['year'].astype(int)
range_selection = st.slider('Select the time range for the plot:',
                            air_travel_df.year.min(),
                            air_travel_df.year.max(),
                            (1999, 2013))
flight_year_df = air_travel_df[air_travel_df['year']\
                               .between(range_selection[0],
                                        range_selection[1], 
                                        inclusive='both'
                                        )]
fig_a = px.scatter(flight_year_df, 
                   x='nonstop_miles', 
                   y='fare', 
                   trendline='ols',
                   color='airline_largest', 
                   color_continuous_scale='speed')
st.plotly_chart(fig_a, use_container_width=True)

#-----------------------------------------------------------------------------------------------------
# Geoplot of Routes with Highest Revenues
st.subheader('Top Revenue-Generating Routes')

air_travel_df['revenue'] = air_travel_df['passengers'] * air_travel_df['fare']
col1, col2 = st.columns(2)
with col1:
    revenue_year = st.slider('Select the year:',
                            air_travel_df.year.min(),
                            air_travel_df.year.max(),
                            2017
                            )
with col2:
    size_select = st.slider('Select the number of routes to plot:',
                            1,
                            500,
                            100)

revenue_df = air_travel_df[air_travel_df['year']==revenue_year].groupby('city-pair').agg({'revenue':'sum',
                                                                    'passengers':'sum',
                                                                    'airline_largest':lambda x:x.value_counts().index[0],
                                                                    'city1':'first',
                                                                    'city2':'first',
                                                                    'city1_lon':'first',
                                                                    'city2_lon':'first',
                                                                    'city1_lat':'first',
                                                                    'city2_lat':'first'})\
                                            .sort_values(by='revenue', ascending=False).head(size_select)

plot_airports_df = revenue_df[['city1', 'city1_lon', 'city1_lat']]
plt_apts2 = revenue_df[['city2', 'city2_lon', 'city2_lat']]
plt_apts2.columns = plot_airports_df.columns
plot_airports_df = pd.concat([plot_airports_df, plt_apts2], axis=0)




fig_rev = go.Figure()

for i in range(len(revenue_df)):
    fig_rev.add_trace(
        go.Scattergeo(
            locationmode='USA-states',
            lon=[revenue_df['city1_lon'][i], revenue_df['city2_lon'][i]],
            lat=[revenue_df['city1_lat'][i], revenue_df['city2_lat'][i]],
            mode = 'lines',
            line = dict(width = 1,color = 'red'),
            opacity = float(i) / float(size_select)
        )
    )

fig_rev.add_trace(go.Scattergeo(
    #locationmode = "USA-states",
    lon = plot_airports_df['city1_lon'],
    lat = plot_airports_df['city1_lat'],
    hoverinfo= 'text',
    text = plot_airports_df['city1'],
    mode='markers',
    marker=dict(
            size = 5,
            color = 'rgb(255, 0, 0)',
            line = dict(
            width = 20,
            color = 'rgba(68, 68, 68, 0)'
            ),
    
    )))
fig_rev.update_layout(
    title_text = 'Biggest Markets in the USA by Revenue',
    title_x=0.4,
    title_y=0.9,
    showlegend = False,
    autosize = True,
    width=1200, height=720,    
    geo = dict(
        scope = 'north america',
        projection_type = 'azimuthal equal area',
        showland = True,
        landcolor = 'rgb(243, 243, 243)',
        countrycolor = 'rgb(204, 204, 204)'           
    ),
)
fig_rev.update_geos(fitbounds='locations')


st.plotly_chart(fig_rev, use_container_width=True)

st.dataframe(revenue_df[['passengers', 'revenue']], height=720, use_container_width=True)