import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_html_components as html
import pandas_datareader.data as web
import datetime

app = dash.Dash()

app.layout = html.Div(children=[
    html.H1('Visualize google finance data'),
    dcc.Input(id='input', value='TSLA', type='text'),
    html.Div(id='output-graph')]
)


@app.callback(
        Output(component_id='output-graph', component_property='children'),
        [Input(component_id='input', component_property='value')])
def update_value(input_data):
    start = datetime.datetime(2015, 1, 1)
    end = datetime.datetime(2018, 3, 1)
    df = web.DataReader(input_data, 'google', start, end)
    return dcc.Graph(id='example',
                     figure={
                         'data': [
                             {'x': df.index, 'y': df.Close, 'type': 'line', 'name': input_data}],
                         'layout': {
                             'title': input_data + ' timeline'
                         }
                     })


if __name__ == '__main__':
    app.run_server()
