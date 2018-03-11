import dash
from dash.dependencies import Output, Input, Event
import dash_core_components as dcc
import dash_html_components as html
import time
import random
import plotly.graph_objs as go
from collections import deque

app = dash.Dash('vehicle-data')

MAX_LENGTH = 20
times = deque(maxlen=MAX_LENGTH)
oil_temps = deque(maxlen=MAX_LENGTH)
intake_temps = deque(maxlen=MAX_LENGTH)
coolant_temps = deque(maxlen=MAX_LENGTH)
rpms = deque(maxlen=MAX_LENGTH)
speeds = deque(maxlen=MAX_LENGTH)
throttle_pos = deque(maxlen=MAX_LENGTH)

data_dict = {
    'Oil Temperature': oil_temps,
    'Intake Temperature': intake_temps,
    'Coolant Temperature': coolant_temps,
    'RPM': rpms,
    'Speed': speeds,
    'Throttle Position': throttle_pos
}


def update_obd_values(times, oil_temps, intake_temps, coolant_temps, rpms, speeds, throttle_pos):
    times.append(time.time())
    if len(times) == 1:
        # initialize relevant values
        oil_temps.append(random.randrange(180, 230))
        intake_temps.append(random.randrange(95, 115))
        coolant_temps.append(random.randrange(170, 220))
        rpms.append(random.randrange(1000, 9500))
        speeds.append(random.randrange(30, 140))
        throttle_pos.append(random.randrange(10, 90))
    else:
        for data_of_interest in [oil_temps, intake_temps, coolant_temps, rpms, speeds, throttle_pos]:
            data_of_interest.append(data_of_interest[-1] + data_of_interest[-1]*random.uniform(-0.0001, 0.0001))

    return times, oil_temps, intake_temps, coolant_temps, rpms, speeds, throttle_pos


app.layout = html.Div(
    [
        html.Div([
            html.H2('Vehicle Data',
                    style={'float': 'left',
                           }),
        ]),
        dcc.Dropdown(id='vehicle-data-name',
                     options=[{'label': s, 'value': s} for s in data_dict.keys()],
                     value=['Coolant Temperature', 'Oil Temperature', 'Intake Temperature'],
                     multi=True),
        html.Div(children=html.Div(id='graphs'), className='row'),
        dcc.Interval(
            id='graph-update',
            interval=100),
    ], className='container', style={'width': '98%',
                                     'margin-left': 10,
                                     'margin-right': 10,
                                     'max-width': 50000})


@app.callback(
    Output('graphs', 'children'),
    [Input('vehicle-data-name', 'value')],
    events=[Event('graph-update', 'interval')]
)
def update_graph(data_names):
    graphs = []
    global times
    global oil_temps
    global intake_temps
    global coolant_temps
    global rpms
    global speeds
    global throttle_pos
    times, oil_temps, intake_temps, coolant_temps, rpms, speeds, throttle_pos = \
        update_obd_values(times, oil_temps, intake_temps, coolant_temps, rpms, speeds, throttle_pos)

    class_choice = 'col s12'
    if len(data_names) > 2:
        class_choice = 'col s12 m6 14'
    elif len(data_names) == 2:
        class_choice = 'col s12 m6 16'

    for data_name in data_names:

        data = go.Scatter(
            x=list(times),
            y=list(data_dict[data_name]),
            name='Scatter',
            fill='tozeroy',
            fillcolor='#6897bb')

        graphs.append(html.Div(dcc.Graph(
            id=data_name,
            animate=True,
            figure={
                'data': [data],
                'layout': go.Layout(xaxis=dict(range=[min(times), max(times)]),
                                    yaxis=dict(range=[min(data_dict[data_name]), max(data_dict[data_name])]),
                                    margin={'l': 50,
                                            'r': 1,
                                            't': 45,
                                            'b': 1},
                                    title='{}'.format(data_name))}
        ), className=class_choice))
    return graphs


external_css = ["https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css"]
for css in external_css:
    app.css.append_css({'external_url': css})

external_js = ["https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/js/materialize.min.js"]
for js in external_js:
    app.scripts.append_script({'external_url': js})

if __name__ == '__main__':
    app.run_server()
