import dash
import dash_table
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


fullQuery = """SELECT * FROM {}"""
query140 = """SELECT * FROM {} WHERE {}=? """


conn = sqlite3.connect(dbschema+'.db')
cur = conn.cursor()

bucket_list = pd.read_sql(fullQuery.format(dbschema), conn)
bucket_list = count_table(bucket_list)
files_140 = pd.read_sql(query140.format(dbschema, 'Current_Step'), conn, params=('140',))
files_140 = count_table(files_140)

app = dash.Dash(__name__)

app.layout = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in files_140.columns],
    data=files_140.to_dict('records'),
)

if __name__ == '__main__':
    app.run_server(debug=True)