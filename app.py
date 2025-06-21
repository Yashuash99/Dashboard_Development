import dash
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

# Load and clean data
df = pd.read_csv('heart.csv')
df['Date'] = pd.date_range(start='2025-01-01', periods=len(df), freq='D')
df['Date'] = pd.to_datetime(df['Date'])

# Replace missing or unrealistic values
df = df[df['Cholesterol'] > 0]

# App setup
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Personalized Healthcare Dashboard"

# Layout
app.layout = dbc.Container([
    html.H1("Personalized Healthcare Insights Dashboard", className='text-center mt-4 mb-4 fw-bold'),

    dbc.Row([
        dbc.Col([
            dcc.DatePickerRange(
                id='date-range',
                start_date=df['Date'].min(),
                end_date=df['Date'].max(),
                display_format='YYYY-MM-DD',
                className='mb-3'
            ),
            dcc.Dropdown(
                id='metric-dropdown',
                options=[
                    {'label': 'Cholesterol', 'value': 'Cholesterol'},
                    {'label': 'Resting Blood Pressure', 'value': 'RestingBP'},
                    {'label': 'Max Heart Rate', 'value': 'MaxHR'}
                ],
                value='Cholesterol',
                clearable=False,
                className='mb-4'
            )
        ])
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Summary Stats"),
                dbc.CardBody([
                    html.P(id='avg-value', className='card-text'),
                    html.P(id='max-value', className='card-text'),
                ])
            ])
        ], width=4),
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='line-chart')
        ], width=12)
    ], className='mt-4'),

    html.Hr(),

    html.H4("Cholesterol vs MaxHR (Colored by Heart Disease)", className='mt-4 mb-2'),
    dcc.Graph(id='scatter-plot')

], fluid=True)

# Callbacks
@app.callback(
    [Output('line-chart', 'figure'),
     Output('avg-value', 'children'),
     Output('max-value', 'children'),
     Output('scatter-plot', 'figure')],
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('metric-dropdown', 'value')]
)
def update_dashboard(start_date, end_date, metric):
    mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
    filtered = df.loc[mask]

    # Line chart
    line_fig = px.line(filtered, x='Date', y=metric, title=f'{metric} Over Time',
                       line_shape='linear', markers=True)

    # Summary
    avg = filtered[metric].mean()
    max_val = filtered[metric].max()
    avg_text = f"Average {metric}: {avg:.2f}"
    max_text = f"Maximum {metric}: {max_val:.2f}"

    # Scatter plot
    scatter_fig = px.scatter(
        filtered, x='Cholesterol', y='MaxHR', color='HeartDisease',
        title='Cholesterol vs Max Heart Rate by Heart Disease',
        labels={"HeartDisease": "Heart Disease"}
    )

    return line_fig, avg_text, max_text, scatter_fig

if __name__ == '__main__':
    app.run(debug=True)
