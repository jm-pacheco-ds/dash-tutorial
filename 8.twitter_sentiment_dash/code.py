import dash
from dash.dependencies import Output, Event, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import sqlite3
import pandas as pd

DB_FILE = 'twitter.db'

app = dash.Dash(__name__)
app.layout = html.Div(
    [
        html.Div(html.H2('Live Twitter Sentiment')),
        dcc.Input(id='sentiment_term', value='twitter', type='text'),
        dcc.Graph(id='live-graph', animate=False),
        dcc.Interval(
            id='graph-update',
            interval=1000
        )
    ]
)

@app.callback(
    Output('live-graph', 'figure'),
    [Input(component_id='sentiment_term', component_property='value')],
    events=[Event('graph-update', 'interval')]
)
def update_graph(term):
    conn = sqlite3.connect(DB_FILE)

    # Read tweets from database
    df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE ? ORDER BY unix DESC LIMIT 1000", conn, params=('%' + term + '%',))
    df.sort_values('unix', inplace=True)
    df['date'] = pd.to_datetime(df['unix'], unit='ms')
    df.set_index('date', inplace=True)
    df['smoothed_sentiment'] = df['sentiment'].rolling(int(len(df) / 5)).mean()
    df.dropna(inplace=True)
    df = df.resample('1s').mean()


    X = df.index
    Y = df.smoothed_sentiment.values
    data = go.Scatter(
        x=list(X),
        y=list(Y),
        name='Scatter',
        mode='lines+markers'
    )

    return {'data': [data],
            'layout': go.Layout(xaxis=dict(range=[min(X), max(X)]),
                                yaxis=dict(range=[min(Y), max(Y)]),
                                title="Term: {}".format(term))}


if __name__ == '__main__':
    app.run_server()
