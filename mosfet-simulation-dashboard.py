import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
import json
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load simulation results
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(SCRIPT_DIR, 'output', 'simulation_results.json')

try:
    with open(JSON_PATH, 'r') as f:
        simulation_results = json.load(f)
    logger.info("Successfully loaded simulation results")
except Exception as e:
    logger.error(f"Error loading simulation results: {str(e)}")
    simulation_results = {}

app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Updated color palette
COLORS = {
    'background': '#F0F4F8',
    'surface': '#FFFFFF',
    'primary': '#005EB8',  # KONE Blue
    'secondary': '#00A5DB',  # KONE Light Blue
    'text': '#333333',
    'text_secondary': '#666666',
    'border': '#E0E0E0',
    'grid': '#E0E0E0',
    'header': '#003B73',  # Darker blue for header
}

# Add a version number to force CSS refresh
CSS_VERSION = "1.6.0"

def create_info_card(title, value):
    return html.Div([
        html.Div(title, className='info-card-title'),
        html.Div(value, className='info-card-value'),
    ], className='info-card')

def create_mosfet_section(mosfet_name, data):
    return html.Div([
        html.H3(mosfet_name, className='mosfet-title'),
        html.Div([
            create_info_card("MOSFET Lifetime (Cycles)", f"{data.get('total_cycles_to_failure', 'N/A'):.2e}"),
            create_info_card("Power Loss in MOSFET in one cycle", f"{data.get('peak_power', 'N/A'):.2f} W"),
            create_info_card("Peak Junction Temperature in cycle", f"{data.get('peak_temp', 'N/A'):.2f}°C"),
        ], className='info-card-container'),
    ], className='mosfet-section')

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                margin: 0;
                padding: 0;
                background-color: ''' + COLORS['background'] + ''';
                color: ''' + COLORS['text'] + ''';
            }
            .dashboard-header {
                background-color: ''' + COLORS['header'] + ''';
                color: ''' + COLORS['surface'] + ''';
                padding: 15px 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .dashboard-header h1 {
                margin: 0;
                font-size: 24px;
                font-weight: 500;
            }
            .dashboard-content {
                padding: 20px;
            }
            .mosfet-section {
                background-color: ''' + COLORS['surface'] + ''';
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .mosfet-title {
                color: ''' + COLORS['primary'] + ''';
                font-size: 18px;
                margin-bottom: 15px;
                font-weight: 500;
            }
            .info-card-container {
                display: flex;
                justify-content: space-between;
                flex-wrap: wrap;
            }
            .info-card {
                background-color: ''' + COLORS['background'] + ''';
                border-radius: 6px;
                padding: 15px;
                width: 31%;
                margin-bottom: 15px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            }
            .info-card-title {
                font-size: 14px;
                color: ''' + COLORS['text_secondary'] + ''';
                margin-bottom: 5px;
            }
            .info-card-value {
                font-size: 18px;
                color: ''' + COLORS['primary'] + ''';
                font-weight: 500;
            }
            .graph-container {
                background-color: ''' + COLORS['surface'] + ''';
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .graph-title {
                color: ''' + COLORS['primary'] + ''';
                font-size: 18px;
                margin-bottom: 15px;
                font-weight: 500;
            }
            @media (max-width: 768px) {
                .info-card {
                    width: 100%;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div([
    # Header
    html.Div([
        html.H1("MOSFET Lifetime Simulation Dashboard"),
        html.Img(src=f'/assets/kone_logo.png?v={CSS_VERSION}', style={'height': '40px'})
    ], className='dashboard-header'),

    # Main content
    html.Div([
        # MOSFET sections
        create_mosfet_section("SPB20N60C3 - Currently used MOSFET (Rds = 0.19 ohms)", simulation_results['SPB20N60C3']),
        create_mosfet_section("STB7ANM60N - Moderate efficiency MOSFET (Rds = 0.9 ohms)", simulation_results['STB7ANM60N']),

        # Graphs
        html.Div([
            html.H3("Brake Voltage and Current profile used in simulation", className='graph-title'),
            dcc.Graph(id='load-pattern-plot')
        ], className='graph-container'),

        html.Div([
            html.H3("Junction Temperature Rise in Every Cycle", className='graph-title'),
            dcc.Graph(id='temperature-rise-plot')
        ], className='graph-container'),

        html.Div([
            html.H3("Life Cycle Comparison of MOSFETs", className='graph-title'),
            dcc.Graph(id='life-expectancy-plot')
        ], className='graph-container'),

    ], className='dashboard-content')
], style={'width': '100%', 'maxWidth': 'none', 'margin': '0 auto', 'padding': '0'})

@app.callback(
    [Output('load-pattern-plot', 'figure'),
     Output('temperature-rise-plot', 'figure'),
     Output('life-expectancy-plot', 'figure')],
    [Input('load-pattern-plot', 'id')]
)
def update_graphs(_):
    try:
        # Brake Voltage and Current Profile Plot
        load_pattern_fig = go.Figure()
        mosfet = list(simulation_results.keys())[0]
        load_pattern_fig.add_trace(go.Scatter(x=simulation_results[mosfet]['t'], y=simulation_results[mosfet]['v_ds'], name='Voltage', line=dict(color=COLORS['primary'], width=2)))
        load_pattern_fig.add_trace(go.Scatter(x=simulation_results[mosfet]['t'], y=simulation_results[mosfet]['i_d'], name='Current', yaxis='y2', line=dict(color=COLORS['secondary'], width=2)))
        
        load_pattern_fig.update_layout(
            xaxis_title='Time (s)',
            yaxis_title='Voltage (V)',
            yaxis2=dict(title='Current (A)', overlaying='y', side='right', showgrid=False),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            margin=dict(l=50, r=50, t=30, b=50),
            plot_bgcolor=COLORS['surface'],
            paper_bgcolor=COLORS['surface'],
            font=dict(color=COLORS['text']),
            xaxis=dict(showgrid=True, gridcolor=COLORS['grid']),
            yaxis=dict(showgrid=True, gridcolor=COLORS['grid']),
            height=400,
        )

        # Temperature Rise Chart
        temp_rise_fig = go.Figure()
        for i, mosfet in enumerate(simulation_results):
            color = COLORS['primary'] if i == 0 else COLORS['secondary']
            temp_rise_fig.add_trace(go.Scatter(x=simulation_results[mosfet]['t'], y=simulation_results[mosfet]['t_j'], name=mosfet, line=dict(color=color, width=2)))
        
        temp_rise_fig.update_layout(
            xaxis_title='Time (s)',
            yaxis_title='Temperature (°C)',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            margin=dict(l=50, r=50, t=30, b=50),
            plot_bgcolor=COLORS['surface'],
            paper_bgcolor=COLORS['surface'],
            font=dict(color=COLORS['text']),
            xaxis=dict(showgrid=True, gridcolor=COLORS['grid']),
            yaxis=dict(showgrid=True, gridcolor=COLORS['grid']),
            height=400,
        )

        # Life Cycle Comparison Horizontal Bar Chart
        life_data = pd.DataFrame({
            'MOSFET': ["SPB20N60C3\n(Rds = 0.19Ω)", "STB7ANM60N\n(Rds = 0.9Ω)"],
            'Cycles': [simulation_results[mosfet].get('total_cycles_to_failure', 0) for mosfet in simulation_results]
        })
        life_fig = px.bar(life_data, y='MOSFET', x='Cycles', 
                          labels={'Cycles': 'MOSFET Lifetime (Cycles)'},
                          color='MOSFET', 
                          color_discrete_sequence=[COLORS['primary'], COLORS['secondary']],
                          orientation='h')
        
        life_fig.update_layout(
            yaxis_title='MOSFET',
            xaxis_title='MOSFET Lifetime (Cycles)',
            xaxis_type='log',
            margin=dict(l=50, r=50, t=30, b=50),
            plot_bgcolor=COLORS['surface'],
            paper_bgcolor=COLORS['surface'],
            font=dict(color=COLORS['text']),
            xaxis=dict(showgrid=True, gridcolor=COLORS['grid']),
            yaxis=dict(showgrid=True, gridcolor=COLORS['grid']),
            height=400,
        )
        life_fig.update_traces(texttemplate='%{x:.2e}', textposition='outside')

        return load_pattern_fig, temp_rise_fig, life_fig

    except Exception as e:
        logger.error(f"Error updating graphs: {str(e)}")
        return [go.Figure() for _ in range(3)]

if __name__ == '__main__':
    app.run_server(debug=True)
