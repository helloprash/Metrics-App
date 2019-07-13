import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import plotly.graph_objs as go
import pandas as pd
import sqlite3


dbschema = 'catsweb'
FactorName = '140'
columnName = 'Current_Step'

def count_table(data_table):
	metric_data = list()

	cf_count_table = data_table.pivot_table(index=['Primary_Complaint_Owner'], aggfunc='size')
	for item in cf_count_table.iteritems():
		metric_data.append(item)

	metric_data_df = pd.DataFrame(metric_data, columns=['Complaint owner', 'Count'])
	#print(metric_data_df)
	return metric_data_df


app = dash.Dash(__name__)


fullQuery = """SELECT * FROM {}"""
query140 = """SELECT * FROM {} WHERE {}=? """


conn = sqlite3.connect(dbschema+'.db')
cur = conn.cursor()
bucket_list = pd.read_sql(query140.format(dbschema, 'Current_Step'), conn, params=('140',))
bucket_list = count_table(bucket_list)
files_140 = pd.read_sql(fullQuery.format(dbschema), conn)
files_140 = count_table(files_140)

data_dict = {"Bucket List":bucket_list,
						 "140 files": files_140}



def update_obd_values(bucket_list, files_140):
    conn = sqlite3.connect(dbschema+'.db')
    cur = conn.cursor()
    bucket_list = pd.read_sql(query140.format(dbschema, 'Current_Step'), conn, params=('140',))
    bucket_list = count_table(bucket_list)
    files_140 = pd.read_sql(fullQuery.format(dbschema), conn)
    files_140 = count_table(files_140)
    return bucket_list, files_140


bucket_list, files_140 = update_obd_values(bucket_list, files_140)

app.layout = html.Div([
    html.Div([
        html.H2('Metrics Data 2',
                style={'float': 'left',
                       }),
        ]),
    dcc.Dropdown(id='graph_name',
                 options=[{'label': s, 'value': s}
                          for s in data_dict.keys()],
                 value=['Bucket List','140 files'],
                 multi=True
                 ),
    html.Div(children=html.Div(id='graphs'), className='row'),
    ], className="container",style={'width':'98%','margin-left':10,'margin-right':10,'max-width':50000})


@app.callback(
    dash.dependencies.Output('graphs','children'),
    [dash.dependencies.Input('graph_name', 'value')],
    #events=[dash.dependencies.Event('graph-update', 'interval')]
    )
def update_graph(data_names):
    graphs = []
    update_obd_values(bucket_list, files_140)
    if len(data_names)>2:
        class_choice = 'col s12 m6 l4'
    elif len(data_names) == 2:
        class_choice = 'col s12 m6 l6'
    else:
        class_choice = 'col s12'


    for data_name in data_names:
        graph_item = data_dict[data_name]
        print(graph_item, 'Here')
        times = graph_item['Complaint owner']
        
        data = go.Bar(x=graph_item['Complaint owner'], y=graph_item['Count'])

        graphs.append(html.Div(dcc.Graph(
	        id=data_name,
	        animate=True,
	        figure={'data': [data],'layout' : go.Layout(title='{}'.format(data_name), showlegend=False)}
	        ), className=class_choice))

    return graphs

if __name__=="__main__":
    app.run_server(debug=True, port=5000)