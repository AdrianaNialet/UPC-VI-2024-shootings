import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data

# Set consistent color scheme
MAIN_COLOR = "#1f77b4"  # Primary blue
COLOR_SCHEME = "blues"   # Consistent color scheme for maps
BACKGROUND_COLOR = "#ffffff"
ACCENT_COLOR = "#9eb8da"  # For secondary lines/elements
MAP_ZERO_COLOR = '#eef1f7'  # For counties with index zero

# Page config
st.set_page_config(layout="wide")

# Load your datasets (same as before)
mass_school_shootings = pd.read_csv('MassShootingCounty2.csv')
counties = pd.read_csv('FIPSCounties2.csv', delimiter = ';')
state_coord = pd.read_csv('2019USCensus.csv', delimiter = ';')
fips = pd.read_csv('FIPS.csv')
population = pd.read_excel('population.xlsx')
population.columns = population.columns.astype(str)
population['State'] = population['State'].str.replace('.', '', regex=False)

# Preprocessing for Mass Shooting (STATE)
population['Population'] = population['2023']
mass_school_shootings['Shootings'] = 1
counties['Shootings'] = 1

states = mass_school_shootings[mass_school_shootings['File'] == 'MS']

states = states.apply(lambda x: x.astype(str) if x.name not in ['Shootings','Victims Killed', 'Victims Injured', 'Total Victims', 'Suspects Killed', 'Suspects Injured', 'Suspects Arrested']  else x)
state = states.groupby('State').sum(numeric_only=True).reset_index()
state_year = states.groupby(['State', 'Year']).sum(numeric_only=True).reset_index()
year = states.groupby('Year').sum(numeric_only=True).reset_index()
month = states.groupby(['Year', 'Month']).sum(numeric_only=True).reset_index()
month['Year-Month'] = month['Year'].astype(str) + '-' + month['Month'].astype(str).str.zfill(2)

state = pd.merge(state, population, on='State', how='left')
state_year = pd.merge(state_year, population, on='State', how='left')

state['Shootings per Citizen'] = (state['Shootings'] / state['Population'])
state['Shootings per Million'] = (state['Shootings'] / state['Population']) * 1_000_000
state['Victims per Citizen'] = (state['Total Victims'] / state['Population'])
state['Victims per Million'] = (state['Total Victims']/ state['Population']) * 1_000_000

# Add FIPS codes for states
state_fips = {
    'Alabama': '1', 'Alaska': '2', 'Arizona': '4', 'Arkansas': '5', 'California': '6', 'Colorado': '8', 'Connecticut': '9',
    'Delaware': '10', 'Florida': '12', 'Georgia': '13', 'Hawaii': '15', 'Idaho': '16', 'Illinois': '17', 'Indiana': '18',
    'Iowa': '19', 'Kansas': '20', 'Kentucky': '21', 'Louisiana': '22', 'Maine': '23', 'Maryland': '24', 'Massachusetts': '25',
    'Michigan': '26', 'Minnesota': '27', 'Mississippi': '28', 'Missouri': '29', 'Montana': '30', 'Nebraska': '31', 'Nevada': '32',
    'New Hampshire': '33', 'New Jersey': '34', 'New Mexico': '35', 'New York': '36', 'North Carolina': '37', 'North Dakota': '38',
    'Ohio': '39', 'Oklahoma': '40', 'Oregon': '41', 'Pennsylvania': '42', 'Rhode Island': '44', 'South Carolina': '45',
    'South Dakota': '46', 'Tennessee': '47', 'Texas': '48', 'Utah': '49', 'Vermont': '50', 'Virginia': '51', 'Washington': '53',
    'West Virginia': '54', 'Wisconsin': '55', 'Wyoming': '56'
}
state['id'] = state['State'].map(state_fips)

# Preprocessing for Mass Shootings (COUNTY)
county = counties[counties['File'] == 'MS']
county['FIPS'] = county['FIPS'].fillna(0).astype(int)
county = county[county['FIPS'] != 0]

county = county.groupby('FIPS').agg(
    Total_Victims=('Total Victims', 'sum'),
    Shootings=('Shootings', 'sum'),
    Population=('Population', 'first'),
    County=('County', 'first'),
    State=('State', 'first') 
).reset_index()

county['Shootings per Citizen'] = (county['Shootings']/ county['Population'])
county['Shootings per Million'] = (county['Shootings']/ county['Population']) * 1000000

# Preprocessing for School Incidents (STATE)
school_states = mass_school_shootings[mass_school_shootings['File'] == 'SS']
school_states = school_states.apply(lambda x: x.astype(str) if x.name not in ['Shootings','Victims Killed', 'Victims Injured', 'Total Victims', 'Suspects Killed', 'Suspects Injured', 'Suspects Arrested']  else x)
school_state = school_states.groupby('State').sum(numeric_only=True).reset_index()
school_state_year = school_states.groupby(['State', 'Year']).sum(numeric_only=True).reset_index()
school_year = school_states.groupby('Year').sum(numeric_only=True).reset_index()
school_month = school_states.groupby(['Year', 'Month']).sum(numeric_only=True).reset_index()
school_month['Year-Month'] = school_month['Year'].astype(str) + '-' + school_month['Month'].astype(str).str.zfill(2)

school_state = pd.merge(school_state, population, on='State', how='left')
school_state_year = pd.merge(school_state_year, population, on='State', how='left')
school_state.columns = school_state.columns.astype(str)

school_state['Shootings per Citizen'] = (school_state['Shootings'] / school_state['Population'])
school_state['Shootings per Million'] = (school_state['Shootings'] / school_state['Population']) * 1_000_000

school_state['id'] = school_state['State'].map(state_fips)

# Preprocessing for School Incidents (COUNTY)
school_county = counties[counties['File'] == 'SS']
school_county['FIPS'] = school_county['FIPS'].fillna(0).astype(int)
school_county = school_county[school_county['FIPS'] != 0]

school_county = school_county.groupby('FIPS').agg(
    Total_Victims=('Total Victims', 'sum'),
    Shootings=('Shootings', 'sum'),
    Population=('Population', 'first'),
    County=('County', 'first'),
    State=('State', 'first') 
).reset_index()


school_county['Shootings per Citizen'] = (school_county['Shootings'] / school_county['Population'])
school_county['Shootings per Million'] = (school_county['Shootings'] / school_county['Population']) * 1_000_000

# Maps
states_map = alt.topo_feature(data.us_10m.url, feature='states')
county_map = alt.topo_feature(data.us_10m.url, 'counties')

# Create index selector
st.title("US Mass Shootings Dashboard")
st.sidebar.info("Adriana Nialet November'24")
st.markdown("""
<style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Add an index/selector for detailed view
st.sidebar.markdown('<p class="big-font">Detailed View Selector</p>', unsafe_allow_html=True)
chart_options = {
    "Overview Dashboard": "Show all charts",
    "Top States Analysis": "Charts 1 & 2",
    "Mass Shooting Geographic Distribution": "Charts 3 & 4",
    "School Shooting Geographic Distribution": "Charts 5 & 6",
    "Mass Shooting and School Shooting Comparison": "Charts 3, 4, 5 & 6",
    "Temporal Analysis": "Charts 7, 8",
    "Income Analysis": "Charts 9"
}
selected_view = st.sidebar.radio("Select View", list(chart_options.keys()))

# Enhanced visualizations with consistent styling
# Chart 1: Top 5 States by Shootings
top_5_states = state.sort_values(by='Shootings per Citizen', ascending=False).head(5)
chart1 = alt.Chart(top_5_states).mark_bar(color=MAIN_COLOR).encode(
    alt.Y('State:N', sort='-x'),
    alt.X('Shootings per Million:Q', title='Shootings per Million Citizen'),
    tooltip=['State:N', 'Shootings per Citizen:Q', 'Shootings per Million:Q']
).properties(
    title=alt.TitleParams(
        text='Top 5 States by Shootings per Citizen',
        fontSize=16
    ),
    width=500,
    height=300
)

# Chart 2: Top 5 States by Victims
top_5_states = state.sort_values(by='Victims per Million', ascending=False).head(5)

top_5_states_victims = top_5_states.melt(
    id_vars='State', 
    value_vars=['Victims Injured', 'Victims Killed'],
    var_name='Category', 
    value_name='Count'
)
chart2 = alt.Chart(top_5_states_victims).mark_bar().encode(
    alt.X('Count:Q', title='Number of Victims'),
    alt.Y('State:N', title='State', sort='-x'),
    alt.Color('Category:N', title='Category', scale=alt.Scale(scheme='blues')), 
    alt.Order('Category:N', sort='descending'),
    tooltip=[
        alt.Tooltip('State:N', title='State'),
        alt.Tooltip('Category:N', title='Category'),
        alt.Tooltip('Count:Q', title='Count')
    ]
).properties(
    title='Top 5 States with the Most Mass Shooting Victims',
    width=500,
    height=300
)

# Chart 3: State Map
chart3 = alt.Chart(states_map).mark_geoshape().encode(
    alt.Color('Shootings per Million:Q', 
              scale=alt.Scale(scheme=COLOR_SCHEME),
              legend=alt.Legend(title="Shootings per Million")),
    tooltip=['State:N', 'Shootings per Million:Q', 'Shootings:Q', 'Population:Q']
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(state, 'id', ['State', 'Shootings per Million', 'Shootings', 'Population'])
).project(
    type='albersUsa'
).properties(
    title=alt.TitleParams(text="Shootings per Million Citizen by State", fontSize=16),
    width=500,
    height=300
)

# Chart 4: County Map
map_layer = alt.Chart(county_map).mark_geoshape().encode(
    color=alt.value(MAP_ZERO_COLOR)  # Light blue for base map (as a zero)
).project(
    type='albersUsa'
)

shootings_layer = alt.Chart(county_map).mark_geoshape().encode(
    color=alt.Color('Shootings per Million:Q',
                   scale=alt.Scale(scheme=COLOR_SCHEME),
                   legend=alt.Legend(title="Shootings per Million")),
    tooltip=['County:N', 'State:N', 'Shootings per Million:Q', 'Shootings:Q', 'Population:Q']
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(county, 'FIPS', ['Shootings per Million', 'County', 'State', 'Shootings', 'Population'])
)

chart4 = (map_layer + shootings_layer).properties(
    title=alt.TitleParams(
        text="Mass Shootings per Million Citizen by County",
        fontSize=16
    ),
    width=500,
    height=300
)

# Chart 5: School Shootings State Map
chart5 = alt.Chart(states_map).mark_geoshape().encode(
    alt.Color('Shootings per Million:Q',
              scale=alt.Scale(scheme=COLOR_SCHEME),
              legend=alt.Legend(title="Shootings per Million")),
    tooltip=['State:N', 'Shootings per Million:Q', 'Shootings:Q', 'Population:Q']
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(school_state, 'id', ['State', 'Shootings per Million', 'Shootings', 'Population'])
).project(
    type='albersUsa'
).properties(
    title=alt.TitleParams(
        text="School Shootings per Million Citizen by State",
        fontSize=16
    ),
    width=500,
    height=300
)

# Chart 6: School Shootings County Map
shootings_layer2 = alt.Chart(county_map).mark_geoshape().encode(
    color=alt.Color('Shootings per Million:Q',
                   scale=alt.Scale(scheme=COLOR_SCHEME),
                   legend=alt.Legend(title="Shootings per Million")),
    tooltip=['County:N', 'State:N', 'Shootings per Million:Q', 'Shootings:Q', 'Population:Q']
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(school_county, 'FIPS', ['Shootings per Million', 'County', 'State', 'Shootings', 'Population'])
)

chart6 = (map_layer + shootings_layer2).properties(
    title=alt.TitleParams(
        text="School Shootings per Million Citizen by County",
        fontSize=16
    ),
    width=500,
    height=300
)

# Chart 7: Time Evolution Line Chart

chart7 = alt.Chart(month).mark_line(
    color=MAIN_COLOR
).encode(
    x=alt.X('Year-Month:T', title='Year'),
    y=alt.Y('Total Victims:Q', title='Number of Shootings'),
    tooltip=['Shootings']
).properties(
    title=alt.TitleParams(
        text="Time Evolution of Mass Shootings",
        fontSize=16
    ),
    width=500,
    height=300
)

# Chart 8: Mass Shootings vs School Shootings Time Evolution
school_month.rename(columns={'Shootings': 'School_Shootings'}, inplace=True)
month_data = pd.merge(month, school_month, on='Year-Month')

base = alt.Chart(month_data).encode(
    x=alt.X('Year-Month:T', title='Year-Month')
)

line1 = base.mark_line(color=MAIN_COLOR).encode(
    y=alt.Y('Shootings:Q', title='Number of Shootings'),
    tooltip=['Shootings']
)

line2 = base.mark_line(color=ACCENT_COLOR).encode(
    y=alt.Y('School_Shootings:Q'),
    tooltip=['School_Shootings']
)

legend = alt.Chart({
    'values': [
        {'category': 'Mass Shootings', 'color': MAIN_COLOR},
        {'category': 'School Shootings', 'color': ACCENT_COLOR}
    ]
}).mark_point().encode(
    y=alt.Y('category:N', title=None),
    color=alt.Color('color:N', title=None)
)

chart8 = (line1 + line2 ).properties(
    title=alt.TitleParams(
        text="Time Evolution of Mass Shootings and School Shootings",
        fontSize=16
    ),
    width=500,
    height=300
)

# Preprocessing for income (STATES)

fips['counties'] = 1
fips['Median Income'] = fips['Median Income'].str.replace('$', '', regex=False)
fips['Median Income'] = fips['Median Income'].str.replace(',', '.', regex=False)
fips['Median Income'] = fips['Median Income'].astype(float)

state_income = fips.groupby('State').agg(
    Income=('Median Income', 'sum'),
    Counties=('counties', 'sum')
).reset_index()

state_income['Income'] = state_income['Income'] / state_income['Counties']
state = pd.merge(state, state_income, on='State', how='left')
state = pd.merge(state, state_coord, on= 'State', how='left')

# Chart 9: Income Graph
base_map = alt.Chart(states_map).mark_geoshape(tooltip=True).encode(
    color=alt.Color('Income:Q',
                   scale=alt.Scale(scheme=COLOR_SCHEME),
                   legend=alt.Legend(title="County's income")),
    tooltip =['State:N', 'Income:Q', 'Shootings per Million:Q', 'Population:Q'] 
).transform_lookup(
    lookup ='id',  
    from_=alt.LookupData(state, 'id', ['State', 'Shootings per Million', 'Population', 'Income'])
).project(
    type ='albersUsa' 
)

shootings_circles = alt.Chart(state).mark_circle(color='red').encode(
    longitude='long:Q',  
    latitude='lat:Q',   
    size='Shootings:Q', 
    tooltip=['State:N', 'Shootings:Q']  
).properties(
    width=500,   
    height=300   
)

chart9 = base_map + shootings_circles

# Add subtle grid lines to charts 7 and 8
for chart in [chart7, chart8]:
    chart = chart.configure_axis(
        grid=True,
        gridColor='#f0f0f0',
        gridWidth=0.5
    )

# Layout based on selection
if selected_view == "Overview Dashboard":
    # Original 3x3 grid layout
    col1, col3, col5 = st.columns(3)
    with col1:
        st.altair_chart(chart1, use_container_width=True)
    with col3:
        st.altair_chart(chart3, use_container_width=True)
    with col5:
        st.altair_chart(chart5, use_container_width=True)
    
    col2, col4, col6 = st.columns(3)
    with col2:
        st.altair_chart(chart2, use_container_width=True)
    with col4:
        st.altair_chart(chart4, use_container_width=True)
    with col6:
        st.altair_chart(chart6, use_container_width=True)
    
    col7, col8, col9 = st.columns(3)
    with col7:
        st.altair_chart(chart7, use_container_width=True)
    with col8:
        st.altair_chart(chart8, use_container_width=True)
    with col9:
        st.altair_chart(chart9, use_container_width=True)

elif selected_view == "Top States Analysis":
    st.altair_chart(chart1, use_container_width=True)
    st.altair_chart(chart2, use_container_width=True)

elif selected_view == "Mass Shooting Geographic Distribution":
    st.altair_chart(chart3, use_container_width=True)
    st.altair_chart(chart4, use_container_width=True)

elif selected_view == "School Shooting Geographic Distribution":
    st.altair_chart(chart5, use_container_width=True)
    st.altair_chart(chart6, use_container_width=True)

elif selected_view == "Mass Shooting and School Shooting Comparison":
    col1, col2 = st.columns(2) 
    with col1:
        st.altair_chart(chart3, use_container_width=True)
        st.altair_chart(chart4, use_container_width=True) 

    with col2:
        st.altair_chart(chart5, use_container_width=True)
        st.altair_chart(chart6, use_container_width=True)

elif selected_view == "Temporal Analysis":
    st.altair_chart(chart7, use_container_width=True)
    st.altair_chart(chart8, use_container_width=True)

else:  
    st.altair_chart(chart9, use_container_width=True)

# Add footer with information
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 10px;'>
    Dashboard shows mass shooting data across the United States. 
    Use the sidebar to switch between different views.
</div>
""", unsafe_allow_html=True)
