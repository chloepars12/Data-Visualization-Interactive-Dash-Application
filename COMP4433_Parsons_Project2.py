# Chloe Parsons
# COMP 4433
# Project 2, Week 10
# 8/20/2025

# data is for first 6 months of 2025 (01/01/2025 - 06/30/2025)
# earthquakes of magnitude 2.5+
# source: USGS
# records: 12545


import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio
from dash import Dash, dcc, html, Input, Output, callback
from dash.exceptions import PreventUpdate

pio.renderers.default = 'browser'
pio.templates.default = 'simple_white'

df = pd.read_csv(r"C:\Users\Chloe.Parsons\COMP4433\Project_2\earthquake_usgs_2025.csv")

#figures
def mag_dist(df, bins):
    fig = px.histogram(
        df,
        x='mag',
        nbins=bins,
        marginal='box',
        title='Earthquake Magnitude Distribution'
    )
    fig.update_layout(
        bargap=0.05,
        xaxis=dict(title='Magnitude', dtick=0.5),
        yaxis=dict(title='Number of Earthquakes')
    )
    fig.update_traces(marker_color='teal')
    return fig

def mag_vs_depth(df, color_mag):
    color_arg = 'mag' if 'color' in color_mag else None
    fig = px.scatter(
        df,
        x='depth',
        y='mag',
        color=color_arg,
        color_continuous_scale='Viridis' if color_arg else None,
        title='Magnitude vs. Depth',
        hover_data={'place': True, 'time': True}
    )
    fig.update_layout(
        xaxis=dict(title='Depth (km)'),
        yaxis=dict(title='Magnitude')
    )
    fig.update_traces(marker=dict(size=4))
    return fig

def gap_vs_net(df, selected_nets):
    filtered_df = df[df['net'].isin(selected_nets)]
    fig = px.box(
        filtered_df,
        x='net',
        y='gap',
        title='Network Contributor vs. Azimuthal Gap',
        color='net',
        color_discrete_sequence=px.colors.qualitative.Dark24
    )
    fig.update_layout(
        xaxis=dict(title='Network Name'),
        yaxis=dict(title='Gap (deg.)')
    )
    return fig

def place_num(df, top_n):
    df['get_place'] = df['place'].str.split(',').str[-1].str.strip()
    top_places = df['get_place'].value_counts().nlargest(top_n).reset_index()
    top_places.columns = ['place', 'count']

    fig = px.bar(
        top_places,
        x='count',
        y='place',
        orientation='h',
        color='place',
        color_discrete_sequence=px.colors.qualitative.Prism,
        text='count',
        title=f'Earthquake Count per Place (Top {top_n})',
        labels={'count': 'Number of Earthquakes', 'place': 'Location'}
    )
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False)
    fig.update_traces(textposition='outside')
    return fig


# app layout

app = Dash(__name__)

app.layout = html.Div([
    html.H1('Earthquake Dashboard', style={'textAlign': 'center'}),

    html.Div([
        dcc.Markdown("""
    ## Welcome to the Earthquake Data Analysis Dashboard  
    Use the menu below to explore the visualizations of USGS data.
    """)
    ], style={'padding': '10px'}),

    html.Br(),

    dcc.Markdown("### Select an option:"),
    dcc.Dropdown(
        id='dropdown-comp',
        options=[
            {'label': 'Magnitude Distribution', 'value': 'mag_dist'},
            {'label': 'Magnitude vs. Depth', 'value': 'mag_vs_depth'},
            {'label': 'Network vs. Gap', 'value': 'gap_vs_net'},
            {'label': 'Location Frequencies', 'value': 'place_num'}
        ],
        value=None,
        placeholder='Click to see the dropdown menu'
    ),
    html.Br(),

    # download component
    html.Button("Download Data", id="download-button"), dcc.Download(id="download-data"),

    # plot components
    html.Div([
        dcc.Markdown("**Input number of bins for histogram:**"),
        dcc.Input(id='input-comp', type='number', min=5, max=200, step=5, value=50)
    ], id='mag-dist-controls', style={'display': 'none'}),
    html.Br(),

    html.Div([
        dcc.Markdown("**Check the box to color points by magnitude:**"),
        dcc.Checklist(id='color-comp', options=[{'label': 'Color by magnitude', 'value': 'color'}], value=[])
    ], id='mag-depth-controls', style={'display': 'none'}),
    html.Br(),

    html.Div([
        dcc.Markdown("**Check box to select network:**"),
        dcc.Checklist(
            id='box-comp',
            options=[{'label': n, 'value': n} for n in sorted(df['net'].unique())],
            value=sorted(df['net'].unique())[:5],
            inline=True
        )
    ], id='gap-net-controls', style={'display': 'none'}),
    html.Br(),

    html.Div([
        dcc.Markdown("**Select number to show:**"),
        dcc.Slider(id='slider-comp', min=5, max=50, step=5, value=10, marks={i: str(i) for i in range(5, 55, 5)})
    ], id='place-controls', style={'display': 'none'}),
    html.Br(),

    dcc.Graph(id='dropdown-selected')
])

#dropdown callback
@app.callback(
    Output('mag-dist-controls', 'style'),
    Output('mag-depth-controls', 'style'),
    Output('gap-net-controls', 'style'),
    Output('place-controls', 'style'),
    Input('dropdown-comp', 'value')
)
def display_controls(plot_choice):
    style_hidden = {'display': 'none'}
    style_visible = {'display': 'block'}
    return (
        style_visible if plot_choice == 'mag_dist' else style_hidden,
        style_visible if plot_choice == 'mag_vs_depth' else style_hidden,
        style_visible if plot_choice == 'gap_vs_net' else style_hidden,
        style_visible if plot_choice == 'place_num' else style_hidden
    )

#plots callback
@app.callback(
    Output('dropdown-selected', 'figure'),
    Input('dropdown-comp', 'value'),
    Input('input-comp', 'value'),
    Input('color-comp', 'value'),
    Input('box-comp', 'value'),
    Input('slider-comp', 'value')
)
def update_plot(plot_choice, bins, color_mag, selected_nets, top_n):
    if plot_choice == 'mag_dist':
        return mag_dist(df, bins)
    elif plot_choice == 'mag_vs_depth':
        return mag_vs_depth(df, color_mag)
    elif plot_choice == 'gap_vs_net':
        return gap_vs_net(df, selected_nets)
    elif plot_choice == 'place_num':
        return place_num(df, top_n)
    else:
        return {}

# download callback
@app.callback(
    Output("download-data", "data"),
    Input("download-button", "n_clicks"),
    prevent_initial_call=True
)
def download_data(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    else:
        return dcc.send_data_frame(df.to_csv, "earthquake_data.csv")



if __name__ == '__main__':
    app.run(debug=True)