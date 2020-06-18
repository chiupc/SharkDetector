import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Create figure with secondary y-axis
# series = [{'title':[],'x':[],'y':[]},{'title':[],'x':[],'y':[]},{'title':[],'x':[],'y':[]}]
def plot_multi_axes(series,title):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # Add traces
    fig.add_trace(
        go.Scatter(x=series[0]['x'], y=series[0]['y'], name=series[0]['title']),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=series[1]['x'], y=series[1]['y'], name=series[1]['title']),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=series[2]['x'], y=series[2]['y'], name=series[2]['title']),
        secondary_y=True,
    )
    # Add figure title
    fig.update_layout(
        title_text=title
    )
    # Set x-axis title
    fig.update_xaxes(title_text="Date Time")
    # Set y-axes titles
    fig.update_yaxes(title_text="<b>primary</b> yaxis", secondary_y=False)
    fig.update_yaxes(title_text="<b>secondary</b> yaxis", secondary_y=True)
    fig.show()
    
def plot_multi_axes_stacked(series,title):
    #fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=series[0]['x'], y=series[0]['y'], name=series[0]['title']),
        #secondary_y=False,
    )
    fig.add_trace(
        go.Bar(x=series[1]['x'], y=series[1]['y'], name=series[1]['title']),
        #secondary_y=False,
    )
    # Change the bar mode
    #fig.update_layout(barmode='stack')
    #fig.add_trace(
    #    go.Scatter(x=series[2]['x'], y=series[2]['y'], name=series[2]['title']),
    #    secondary_y=True,
    #)
    # Add figure title
    #fig.update_layout(
    #    title_text=title
    #)
    # Set x-axis title
    fig.update_xaxes(title_text="Date Time")
    fig.update_layout(barmode='group', xaxis_tickangle=-45)
    # Set y-axes titles
    #fig.update_yaxes(title_text="<b>primary</b> yaxis", secondary_y=False)
    #fig.update_yaxes(title_text="<b>secondary</b> yaxis", secondary_y=True)
    fig.show()