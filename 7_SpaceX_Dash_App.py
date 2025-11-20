import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-					size': 40}),
    
    html.Br(),

    # Dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
        ],
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),

    html.Br(),

    # Pie chart placeholder
    html.Div(dcc.Graph(id='success-pie-chart')),

    html.Br(),

    html.P("Payload range (Kg):"),

    # Slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0, 
        max=10000,
        step=1000,
        marks={0: '0', 10000: '10k'},
        value=[min_payload, max_payload]
    ),

    html.Br(),

    # Scatter chart placeholder
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])


# -------------------------------
# CALLBACK 1: Pie Chart
# -------------------------------
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(selected_site):
    if selected_site == 'ALL':
        fig = px.pie(
            spacex_df,
            values='class',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        df_site = spacex_df[spacex_df['Launch Site'] == selected_site]
        count_success = int((df_site['class'] == 1).sum())
        count_failure = int((df_site['class'] == 0).sum())

    # build the pie using explicit names and values
        fig = px.pie(
        names=['Failure', 'Success'],
        values=[count_failure, count_success],
        title=f'Success vs Failure for {selected_site}'
        )
    return fig


# -------------------------------
# CALLBACK 2: Scatter Plot
# -------------------------------
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def get_scatter_plot(selected_site, payload_range):

    low, high = payload_range
    df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                   (spacex_df['Payload Mass (kg)'] <= high)]
    
    booster_keywords = {
    'v1.0': 'Falcon 9 v1.0',
    'v1.1': 'Falcon 9 v1.1',
    'FT': 'Falcon 9 FT',
    'B4': 'Falcon 9 B4',
    'B5': 'Falcon 9 B5'
    }

    color_map = {
    'Falcon 9 v1.0': 'red',
    'Falcon 9 v1.1': 'blue',
    'Falcon 9 FT': 'green',
    'Falcon 9 B4': 'purple',
    'Falcon 9 B5': 'orange'
    }

    def map_booster_category(version):
        for keyword, category in booster_keywords.items():
            if keyword in version:
                return category
        return 'Unknown'
    
    spacex_df['Booster_Category'] = spacex_df['Booster Version'].apply(map_booster_category)

    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]

    fig = px.scatter(
        df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster_Category',
        title='Payload vs. Outcome by Booster Version',
        color_discrete_map=color_map,
        hover_data=['Booster Version']
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run()