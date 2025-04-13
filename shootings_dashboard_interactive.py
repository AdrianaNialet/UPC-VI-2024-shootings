import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data

# Data Loading and Preprocessing
st.set_page_config(layout="wide")
st.sidebar.info("Adriana Nialet December'24")

mass_shootings = pd.read_csv('mass-shootings-csv.csv')
population = pd.read_csv('populations-csv.csv')
counties_fips = pd.read_csv('FIPS.csv')
mass_shootings['Year'] = mass_shootings['Year'].astype(int)
population['Population'] = population['Population'].astype(int)
mass_shootings['Shootings'] = 1

region_state_palettes = {
    'Midwest': ['#1f77b4', '#aec7e8', '#17becf', '#9edae5'],
    'Southeast': ['#ff7f0e', '#ffbb78', '#ff9896', '#ff7c7c'],
    'Northeast': ['#2ca02c', '#98df8a', '#b5cf6b', '#cedb9c'],
    'Southwest': ['#d62728', '#ff9896', '#e377c2', '#f7b6d2'],
    'West': ['#9467bd', '#c5b0d5', '#8c564b', '#c49c94']
}

region_colors = {
    'Midwest': '#1f77b4',
    'Southeast': '#ff7f0e',
    'Northeast': '#2ca02c',
    'Southwest': '#d62728',
    'West': '#9467bd'
}

region_palette = alt.Scale(domain=list(region_colors.keys()), range=list(region_colors.values()))
region_palette_schema = {
    'Midwest': alt.Scale(scheme='blues'),
    'Southeast': alt.Scale(scheme='oranges'),
    'Northeast': alt.Scale(scheme='greens'),
    'Southwest': alt.Scale(scheme='reds'),
    'West': alt.Scale(scheme='purples')
}

state_colors = {
    'Alabama': '#ff7f0e',
    'Alaska': '#9b59b6',
    'Arizona': '#e74c3c',
    'Arkansas': '#ff5722',
    'California': '#8e44ad',
    'Colorado': '#9c27b0',
    'Connecticut': '#388e3c',
    'District of Columbia': '#ff8c00',
    'Delaware': '#66bb6a',
    'Florida': '#ff7043',
    'Georgia': '#f4511e',
    'Hawaii': '#7e57c2',
    'Idaho': '#6a4f98',
    'Illinois': '#3498db',
    'Indiana': '#1e88e5',
    'Iowa': '#1976d2',
    'Kansas': '#1565c0',
    'Kentucky': '#f4511e',
    'Louisiana': '#ff7043',
    'Maine': '#388e3c',
    'Maryland': '#ff9800',
    'Massachusetts': '#43a047',
    'Michigan': '#2980b9',
    'Minnesota': '#1e88e5',
    'Mississippi': '#ff7043',
    'Missouri': '#3498db',
    'Montana': '#8e44ad',
    'Nebraska': '#1976d2',
    'Nevada': '#9b59b6',
    'New Hampshire': '#43a047',
    'New Jersey': '#66bb6a',
    'New Mexico': '#c0392b',
    'New York': '#2e7d32',
    'North Carolina': '#ff7043',
    'North Dakota': '#3498db',
    'Ohio': '#1e88e5',
    'Oklahoma': '#c0392b',
    'Oregon': '#7e57c2',
    'Pennsylvania': '#43a047',
    'Rhode Island': '#66bb6a',
    'South Carolina': '#ff7043',
    'South Dakota': '#1565c0',
    'Tennessee': '#ff5722',
    'Texas': '#c0392b',
    'Utah': '#7e57c2',
    'Vermont': '#43a047',
    'Virginia': '#f4511e',
    'Washington': '#8e44ad',
    'West Virginia': '#ff7043',
    'Wisconsin': '#3498db',
    'Wyoming': '#7e57c2'
}

# Filter by year and Metric
year_range = st.sidebar.slider(
    "Select Year Range:",
    min_value=int(mass_shootings['Year'].min()),
    max_value=int(mass_shootings['Year'].max()),
    value=(int(mass_shootings['Year'].min()), int(mass_shootings['Year'].max()))
)

filtered_data = mass_shootings[
    (mass_shootings['Year'] >= year_range[0]) &
    (mass_shootings['Year'] <= year_range[1])
]

selected_metric = st.sidebar.selectbox(
    "Select Metric to Display:",
    options=['Shootings', 'Victims Killed', 'Victims Injured', 'Total Victims', 'Suspects Killed', 'Suspects Arrested'],
    index=0
)

# All Regions Visualization
first_year = year_range[0]
last_year = year_range[1]
st.title(f"US Mass Shootings Dashboard ({first_year} to {last_year})")

st.header("Regional Analysis")
complete_states = mass_shootings[['State', 'FIPS_State', 'Region']].drop_duplicates()
grouped_data_state = filtered_data.groupby(['State', 'Region', 'FIPS_State']).agg(
    **{selected_metric: (selected_metric, 'sum')},
).reset_index()
grouped_data_state = pd.merge(complete_states, grouped_data_state, on=['State', 'FIPS_State', 'Region'], how='left')
grouped_data_state[selected_metric] = grouped_data_state[selected_metric].fillna(0)

grouped_data_region = filtered_data.groupby(['Year', 'Region']).agg(
    **{selected_metric: (selected_metric, 'sum')}
).reset_index()
grouped_data_region= pd.merge(grouped_data_region, population[['Region', 'Population']], on='Region', how='left')
grouped_data_region[f'{selected_metric} per Million'] = round(grouped_data_region[selected_metric] / grouped_data_region['Population'] * 1_000_000,2)

col1, col2 = st.columns(2)
with col1:
    chart_region_line = alt.Chart(grouped_data_region).mark_line(point=True).encode(
        x='Year:O',
        y=f'{selected_metric}:Q',
        color=alt.Color('Region:N', scale=region_palette, legend=None),
        tooltip=['Year', 'Region', f'{selected_metric}']
    ).properties(
        title=f"Total {selected_metric} by Region Over Time",
        width=500,
        height=400
    )
    st.altair_chart(chart_region_line, use_container_width=True)

with col2:
    slope_data_region = grouped_data_region[grouped_data_region['Year'].isin([year_range[0], year_range[1]])].copy()
    slope_data_region['Year'] = slope_data_region['Year'].astype(str)
    chart_region_slope = alt.Chart(slope_data_region).mark_line(point=True).encode(
        x='Year:O',
        y=f'{selected_metric} per Million:Q',
        color=alt.Color('Region:N', scale=region_palette, legend=None),
        tooltip=['Year', 'Region', f'{selected_metric} per Million']
    ).properties(
        title=f"Regional {selected_metric} per Million",
        width=500,
        height=400
    )
    st.altair_chart(chart_region_slope, use_container_width=True)

states_map = alt.topo_feature(data.us_10m.url, feature='states')

chart_global_choropleth = alt.Chart(states_map).mark_geoshape(
    stroke='white',
    strokeWidth=0.5
).encode(
    color=alt.Color(
        'Region:N',
        scale=region_palette,
        legend=alt.Legend(title="Region")
    ),
    fillOpacity=alt.FillOpacity(
        f'{selected_metric}:Q',
        scale=alt.Scale(range=[0.3, 1])
    ),
    tooltip=[
        alt.Tooltip('State:N'),
        alt.Tooltip('Region:N'),
        alt.Tooltip(f'{selected_metric}:Q', title=selected_metric)
    ]
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(grouped_data_state, 'FIPS_State', ['State', 'Region', selected_metric])
).project(
    type='albersUsa'
).properties(
    title=f"{selected_metric} by State and Region",
    width=800,
    height=500
)

st.altair_chart(chart_global_choropleth, use_container_width=True)

# State Visualization
default_states = filtered_data['State'].unique()[:1].tolist()
selected_states = st.sidebar.multiselect(
    "Select States:",
    options=filtered_data['State'].unique(),
    default=default_states
)

if selected_states:
    st.header("State Analysis")

    state_data = filtered_data[filtered_data['State'].isin(selected_states)]
    grouped_data_state_year = state_data.groupby(['Year', 'State']).agg(
        **{selected_metric: (selected_metric, 'sum')},
        FIPS_State=('FIPS_State', 'first'),
        Region=('Region', 'first')
    ).reset_index()

    years = range(year_range[0], year_range[1] + 1)
    complete_index = pd.MultiIndex.from_product([selected_states, years], names=['State', 'Year'])
    complete_states = pd.DataFrame(index=complete_index).reset_index()
    grouped_data_state_year = pd.merge(complete_states, grouped_data_state_year, on=['State', 'Year'], how='left')
    grouped_data_state_year  = grouped_data_state_year.fillna({selected_metric: 0, 'FIPS_State': grouped_data_state_year['FIPS_State'].iloc[0], 'Region': grouped_data_state_year['Region'].iloc[0]})

    grouped_data_state_year = pd.merge(grouped_data_state_year, population[['State', 'Population']], on='State', how='left')
    grouped_data_state_year[f'{selected_metric} per Million'] = round(grouped_data_state_year[selected_metric] / grouped_data_state_year['Population'] * 1_000_000,2)

    state_colors = {state: state_colors[state] for state in selected_states if state in state_colors}
    state_palette = alt.Scale(domain=list(state_colors.keys()), range=list(state_colors.values()))

    col3, col4 = st.columns(2)
    with col3:
        
        chart_state_line = alt.Chart(grouped_data_state_year).mark_line(point=True).encode(
            x='Year:O',
            y=f'{selected_metric}:Q',
            color=alt.Color('State:N', scale=state_palette, legend=None),
            tooltip=['Year', 'State', f'{selected_metric}']
        ).properties(
            title=f"{selected_metric} Trend for Selected States",
            width=500,
            height=400
        )
        st.altair_chart(chart_state_line, use_container_width=True)

    with col4:
        slope_data_state = grouped_data_state_year[grouped_data_state_year['Year'].isin([first_year, last_year])].copy()
        slope_data_state['Year'] = slope_data_state['Year'].astype(str)

        chart_state_slope = alt.Chart(slope_data_state).mark_line(point=True).encode(
            x='Year:O',
            y=f'{selected_metric} per Million:Q',
            color=alt.Color('State:N', scale=state_palette, legend=alt.Legend(title="States")),
            tooltip=['Year', 'State', f'{selected_metric} per Million']
        ).properties(
            title=f"State-Level {selected_metric} per Million Trends",
            width=500,
            height=400
        )
        st.altair_chart(chart_state_slope, use_container_width=True)

    # County Visualization
    st.header("County Analysis")

    counties_fips = counties_fips[counties_fips['State'].isin(selected_states)]

    grouped_data_county = filtered_data.groupby(['FIPS', 'Year']).agg(   
        **{selected_metric: (selected_metric, 'sum')},
        State=('State', 'first'),
        County=('County', 'first')
    ).reset_index()

    grouped_data_county = counties_fips.merge(grouped_data_county, on=['State','FIPS'], how='left')
    grouped_data_county[selected_metric].fillna(0, inplace=True)
    
    counties_map = alt.topo_feature(data.us_10m.url, feature='counties')

    counties = alt.Chart(counties_map).mark_geoshape().encode(
        color=alt.Color(
            'State:N',
            scale=state_palette,
            legend=alt.Legend(title="State")
        ),
        fillOpacity=alt.FillOpacity(
            f'{selected_metric}:Q',
            scale=alt.Scale(range=[0.3, 1])
        ),
        tooltip=['State:N', 'County2:N', f'{selected_metric}:Q'] 
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(grouped_data_county, 'FIPS', ['County2', 'State', selected_metric, 'Region'])
    )

    chart_county_cloropleth = (counties).project(
        type='albersUsa'
    ).properties(
        title=f"County-Level {selected_metric} in Selected State(s)",
        width=800,
        height=500
    )

    st.altair_chart(chart_county_cloropleth, use_container_width=True)

    for state in selected_states:
        state_data = filtered_data[filtered_data['State'] == state]
        region = state_data['Region'].iloc[0]
        counties = state_data['County'].unique()

        years = range(year_range[0], year_range[1] + 1)
        county_year_index = pd.MultiIndex.from_product([counties, years], names=['County', 'Year'])
        complete_county_data = pd.DataFrame(index=county_year_index).reset_index()

        grouped_data_county_year = state_data.groupby(['County', 'Year']).agg(
            **{selected_metric: (selected_metric, 'sum')}
        ).reset_index()

        complete_county_data = pd.merge(
            complete_county_data,
            grouped_data_county_year,
            on=['County', 'Year'],
            how='left'
        ).fillna({selected_metric: 0})  

        chart_county_heatmap = alt.Chart(complete_county_data).mark_rect().encode(
            x=alt.X('Year:O', title="Year"),
            y=alt.Y('County:N', title="County"),
            color=alt.Color(
                f'{selected_metric}:Q',
                scale=region_palette_schema[region],
                legend=alt.Legend(title=selected_metric)
            ),
        tooltip=['Year', 'County', f'{selected_metric}']
        ).properties(
            title=f"{state} County-Level Heatmap of {selected_metric}",
            width=700,
            height=400
        )
        st.altair_chart(chart_county_heatmap, use_container_width=True)
    st.write('Selected States Data:')
    st.write(state_data)


# Summary Global US Data
st.sidebar.metric(f"Total {selected_metric} US ({first_year} to {last_year})", filtered_data[selected_metric].sum())
st.sidebar.metric(f"Average {selected_metric} per Year", round(filtered_data[selected_metric].sum() / len(filtered_data['Year'].unique()), 2))
