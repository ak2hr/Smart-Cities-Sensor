import plotly.graph_objs as go
import plotly.plotly as plty

from db_scripts.get_server_data import get_table_for_variable

flow_df = get_table_for_variable('1')
flow_df = flow_df.sort_index()
tide_df = get_table_for_variable('4')
tide_df = tide_df[flow_df.index[0]:]

flow_trace = go.Scatter(x=flow_df.index, y=flow_df['Value'], name='Flow at Storm Drain (cfs)')

tide_trace = go.Scatter(x=tide_df.index, y=tide_df['Value'], name='Level at tide gauge (ft)')
data = [tide_trace, flow_trace]

url = plty.plot(data, filename='flow data at storm drain')
# here is the plot: "https://plot.ly/~jsadler2/193.embed"
