import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import pandas as pd
import datetime

url = 'http://cwqa/CATSWebNET/main.aspx?WCI=Main&WCE=SubmitQry&WCU=%7c*%7eq%3d8%7c*%7er%3dOverall%20Query%7c*%7ef%3d-1%7c*%7eo%3d2%7c*%7ep%3dComplaint%20Folder%7c*%7es%3dQNDUMFQZKKA5L3EITVLJETQ9K596TO67'

stepID = ['030','040','050','055','090','140']


def createPickle(url):
    df_html = pd.read_html(url)
    data_table = df_html[1]

    col_names = list()

    for index, row in data_table.iloc[[0]].iterrows():
        for i in range(len(data_table.columns)):
            col_names.append(row[i])

    data_table.columns = col_names
    data_table = data_table.drop(data_table.index[0])
    data_table = data_table.set_index('Complaint Number')

    data_table.to_pickle('catsweb.pickle')



def count_table(data_table):
    metric_data = list()

    cf_count_table = data_table.pivot_table(index=['Complaint Owner'], aggfunc='size')
    for item in cf_count_table.iteritems():
        metric_data.append(item)

    metric_data_df = pd.DataFrame(metric_data, columns=['Complaint owner', 'Count'])
    #print(metric_data_df)
    return metric_data_df


def generate_table(dataframe):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), len(dataframe)))]
    )


def stepCount(step_count_table):
    step_data = dict()

    for each_step in stepID:
        step_count = step_count_table[step_count_table['Current Step'] == each_step]
        #step_count = step_count_table[step_count_table.Current_Step.str.contains('|'.join(each_step))]
        #step_count = pd.read_sql(query.format(dbschema, 'Current_Step'), conn, params=(each_step,))
        step_data.update({'Step '+str(each_step) : [step_count['Current Step'].count(),]})

    return pd.DataFrame(step_data)


createPickle(url)
print('Reading 1')
bucket_list = pd.read_pickle('catsweb.pickle')


app = dash.Dash()

app.layout = html.Div(children=[
    html.H4(children='Total Metric Data'),
    html.Div(id='my-output-interval'),
    dcc.Dropdown(id='dropdown', options=[
        {'label': i, 'value': i} for i in bucket_list['Complaint Owner'].unique()
    ], multi=True, placeholder='Filter by name...'),
    html.Div(id='table-container'),
    dcc.Interval(
            id='interval-component 1',
            interval=20000 # in milliseconds
        ),
    dcc.Interval(
            id='interval-component 2',
            interval=1000 # in milliseconds
        )
])

@app.callback(Output('table-container', 'children'),
    [Input('dropdown', 'value'),Input('interval-component 1', 'n_intervals')])
def display_table(dropdown_value, n):
    createPickle(url)
    bucket_list = pd.read_pickle('catsweb.pickle')
    print('Reading 2')
    if dropdown_value is None:
        return generate_table(stepCount(bucket_list))

    dff = bucket_list[bucket_list['Complaint Owner'].str.contains('|'.join(dropdown_value))]
    return generate_table(stepCount(dff))

@app.callback(Output('my-output-interval', 'children'),
    [Input('interval-component 2', 'n_intervals')])
def display_timestamp(n):
    now = datetime.datetime.now()
    bucket_list = pd.read_pickle('catsweb.pickle')
    timeStamp = '{} intervals have passed. It is {}:{}:{} and length is {}'.format(
        n,
        now.hour,
        now.minute,
        now.second,
        bucket_list['Complaint Owner'].count()
    )
    return timeStamp

    

app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

if __name__ == '__main__':
    app.run_server(debug=True, port=5006)








""""""