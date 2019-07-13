import pandas as pd
import sqlite3

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_scripts = ['https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js']

url1 = 'http://cwprod/CATSWebNET/main.aspx?WCI=Main&WCE=SubmitQry&WCU=%7c*%7eq%3d8%7c*%7er%3dOverall%20Query%201%7c*%7ef%3d-1%7c*%7eo%3d2%7c*%7ep%3dComplaint%20Folder%7c*%7es%3d7AOP68DR3CIA0WWVZNHNAFSVYRGB51S9'

url2 = 'http://cwprod/CATSWebNET/main.aspx?WCI=Main&WCE=SubmitQry&WCU=s%3D7AOP68DR3CIA0WWVZNHNAFSVYRGB51S9%7C%2A%7Er%3DOverall%20Query%202%7C%2A%7Eq%3DCAQuery%7C%2A%7Ef%3D%252D1%7C%2A%7Eo%3D2'

dbschema = 'catsweb'
stepID = ['030','040','050','055','090','140']
columnName = 'Current_Step'

def createDF(url):
	print('Reading...')
	df_html = pd.read_html(url)
	data_table = df_html[1]

	col_names = list()

	for index, row in data_table.iloc[[0]].iterrows():
		for i in range(len(data_table.columns)):
			col_names.append(row[i].replace(" ", "_"))


	data_table.columns = col_names
	data_table = data_table.drop(data_table.index[0])
	data_table = data_table.set_index('Complaint_Number')
	print('Done')
	return data_table

def createDB():
	print('Refreshing Database')
	data_table1 = createDF(url1)
	data_table2 = createDF(url2)

	data_table = pd.concat([data_table1, data_table2])

	conn = sqlite3.connect(dbschema+'.db')
	data_table.to_sql(dbschema, conn, if_exists="replace")
	data_table.to_excel('output.xlsx')
	cur = conn.cursor()

