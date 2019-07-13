import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import plotly.graph_objs as go
import pandas as pd
import datetime

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_scripts = ['https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js']

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



createPickle(url)
print('Reading 1')
bucket_list = pd.read_pickle('catsweb.pickle')
files_140 = bucket_list[bucket_list['Current Step'] == '140']
bucket_list = count_table(bucket_list)
files_140 = count_table(files_140)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

data_dict = {
		"Bucket List":bucket_list,
		"140 files": files_140
}

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts)

app.layout = html.Div([
    html.Div(id='my-output-interval'),
    dcc.Dropdown(id='graph_name',
                 options=[{'label': s, 'value': s}
                          for s in data_dict.keys()],
                 value=['Bucket List','140 files'],
                 multi=True
                 ),
    #html.Button(id='submit-button', n_clicks=0, children='Submit'),
    html.Div(id='output-state'),
    html.Div(children=[html.Div(id='graphs'), ], className='row'),
    html.Div(id='table'),
    dcc.Interval(
            id='interval-component 1',
            interval=20000 # in milliseconds
        ),
    dcc.Interval(
            id='interval-component 2',
            interval=1000 # in milliseconds
        )
])

print('Summa22')

@app.callback([Output('graphs', 'children'), Output('my-output-interval', 'children')],
    					[Input('interval-component 1', 'n_intervals'), Input('graph_name', 'value')])

def update_output(n, data_names):
	graphs = []
	createPickle(url)
	bucket_list = pd.read_pickle('catsweb.pickle')
	files_140 = bucket_list[bucket_list['Current Step'] == '140']
	bucket_list = count_table(bucket_list)
	files_140 = count_table(files_140)



	data_dict["Bucket List"] = bucket_list
	data_dict["140 files"] = files_140

	for data_name in data_names:
		graph_item = data_dict[data_name]
		xList = len(graph_item['Complaint owner'])
		yList = graph_item['Count']
		data = go.Bar(x=graph_item['Complaint owner'], y=graph_item['Count'])

		graphs.append(html.Div(dcc.Graph(id=data_name, 
										className="six columns", 
										animate=True, 
										figure={'data': [data],
										'layout' : go.Layout(title='{}'.format(data_name))}), 
								)
					)

	now = datetime.datetime.now()
	timeStamp = '{} intervals have passed. It is {}:{}:{} and length is {}'.format(
      n,
      now.hour,
      now.minute,
      now.second,
      now.year
  )
	
	return graphs, timeStamp

if __name__=="__main__":
	app.run_server(debug=True, port=5005)
