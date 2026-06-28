import pandas as pd
import plotly.express as px
from plotly.io import show
from fastf1.ergast import Ergast

# Load results for season 2022
ergast = Ergast()
races = ergast.get_race_schedule(2022)
results = []

# For each race in the season
for rnd, race in races['raceName'].items():
    # Get results (round no. starts from 1)
    temp = ergast.get_race_results(season=2022, round=rnd + 1)
    temp = temp.content[0]
    
    # If there is a sprint, get the results as well
    sprint = ergast.get_sprint_results(season=2022, round=rnd + 1)
    if sprint.content and sprint.description['round'][0] == rnd + 1:
        temp = pd.merge(temp, sprint.content[0], on='driverCode', how='left')
        # Add sprint points and race points to get the total
        temp['points'] = temp['points_x'] + temp['points_y']
        temp.drop(columns=['points_x', 'points_y'], inplace=True)
    
    # Add round no. and grand prix name
    temp['round'] = rnd + 1
    temp['race'] = race.removesuffix(' Grand Prix')
    temp = temp[['round', 'race', 'driverCode', 'points']]
    results.append(temp)

# Append all races into a single dataframe
results = pd.concat(results)
races = results['race'].drop_duplicates()

# Reshape to wide table (drivers as rows, races as columns)
results = results.pivot(index='driverCode', columns='round', values='points')

# Rank drivers by total points
results['total_points'] = results.sum(axis=1)
results = results.sort_values(by='total_points', ascending=False)
results.drop(columns='total_points', inplace=True)

# Use race names as column names
results.columns = races

# Plot heatmap using plotly
fig = px.imshow(
    results,
    text_auto=True,
    aspect='auto',
    color_continuous_scale=[[0,    'rgb(198, 219, 239)'],
                            [0.25, 'rgb(107, 174, 214)'],
                            [0.5,  'rgb(33,  113, 181)'],
                            [0.75, 'rgb(8,   81,  156)'],
                            [1,    'rgb(8,   48,  107)']],
    labels={'x': 'Race',
            'y': 'Driver',
            'color': 'Points'}
)
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='')
fig.update_yaxes(tickmode='linear')
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey',
                 showline=False,
                 tickson='boundaries')
fig.update_xaxes(showgrid=False, showline=False)
fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
fig.update_layout(coloraxis_showscale=False)
fig.update_layout(xaxis=dict(side='top'))
fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))
show(fig)