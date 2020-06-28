import pandas as pd
from klse_scrapper import *
from shareinvestor_scrapper import *
import plotly.graph_objects as go
from datetime import timedelta, time, date,datetime
from utils import get_counter_list

def cal_price_diff(list_):
    list__=list_.values
    slope=list__[-1]-list__[0]
    return slope
    return fibo

def cal_price_diff_pct(list_):
    list__=list_.values
    slope=(list__[-1]-list__[0])/list__[0]*100
    return slope

def cal_fibonacci(df):
    df['Datetime']=pd.to_datetime(df['Datetime'])
    df=df.set_index('Datetime')
    df_max_slope=pd.DataFrame()
    max_slope_list=[]
    for i in range(1,30):
        df['CloseLast']=df['Close'].rolling(i).apply(lambda x: x[-1])
        df['CloseFirst']=df['Close'].rolling(i).apply(lambda x: x[0])
        df['Grad']=df['Close'].rolling(i).apply(lambda x: cal_price_diff(x))
        df['Grad_Pct']=df['Close'].rolling(i).apply(lambda x: cal_price_diff_pct(x))
        df_=df[df['Grad']==df['Grad'].max()]
        df_['rolling_days']=i
        df_max_slope=df_max_slope.append(df_)
    df_max_slope=df_max_slope.reset_index()
    df_max=df_max_slope[df_max_slope['Grad']==df_max_slope['Grad'].max()]
    df_max['Fibo236']=df_max['CloseLast']-df_max['Grad']*0.236
    df_max['Fibo382']=df_max['CloseLast']-df_max['Grad']*0.382
    df_max['Fibo500']=df_max['CloseLast']-df_max['Grad']*0.500
    df_max['Fibo618']=df_max['CloseLast']-df_max['Grad']*0.618
    df_max['Fibo764']=df_max['CloseLast']-df_max['Grad']*0.764
    df_max_datetime_idx=df.index.get_loc(df_max['Datetime'].iloc[0])
    df_max['FiboStartDate']=df.reset_index()['Datetime'].iloc[df_max_datetime_idx - df_max['rolling_days'].iloc[0]]
    df_max['FiboStartPrice']=df.reset_index()['Close'].iloc[df_max_datetime_idx - df_max['rolling_days'].iloc[0]]
    return df_max.drop(columns=['Open','High','Low','Volume'])

def calc_fibonacci_dist(df,df_max):
    df_=pd.DataFrame()
    df_['Fibo236_dist']=df['Close'] - df_max['Fibo236'].iloc[0]
    df_['Fibo382_dist']=df['Close'] - df_max['Fibo382'].iloc[0]
    df_['Fibo500_dist']=df['Close'] - df_max['Fibo500'].iloc[0]
    df_['Fibo618_dist']=df['Close'] - df_max['Fibo618'].iloc[0]
    df_['Fibo764_dist']=df['Close'] - df_max['Fibo764'].iloc[0]
    df_['Close']=df['Close']
    return df_

def calc_retracement_level(df, df_fibo):
    df_max_time=df_fibo['Datetime'].iloc[0].timestamp()
    df_filtered=df[df['Datetime'].apply(lambda x: x.timestamp()) > df_max_time]
    df_dist=calc_fibonacci_dist(df_filtered,df_fibo)
    df_dist=df_dist.abs()
    retracement_level=df_dist.loc[df_dist['Close'].idxmin()].idxmin()
    return retracement_level

def mine_retracement_level(category="All",period=90):
    listings_code,listings_symbol=get_counter_list(category)
    for i in range(len(listings_symbol)):
        #get counter price history
        try:
            from_=datetime.combine(date.today()-timedelta(days=period), time(18)).timestamp()
            to_=datetime.combine(date.today(), time(9)).timestamp()
            event={'symbol':listings_symbol[i],'counter':listings_code[i],'from':int(from_),'to':int(to_),'resolution':'D'}
            df=klse_price_data(event)
            df['Datetime']=pd.to_datetime(df['Datetime'])
            df['Close']=df['Close'].astype(float)
            df_fibo=cal_fibonacci(df)
            retracement_level=[]
            retracement_level.append(calc_retracement_level(df,df_fibo))
        except Exception as e:
            retracement_level.append(None)
            logger.error(e)
    dict_={'symbol':listings_symbol, 'code':listings_code,'retracement_level':retracement_level}
    df_retracement=pd.DataFrame.from_dict(dict_)
    return df_retracement

def plot_fibonacci(df,df_max,symbol):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=df['Datetime'], y=df['Close'], name='Price')
    )
    #fibo datetime
    start_time=df.iloc[0]['Datetime']
    end_time=df.iloc[-1]['Datetime']
    fibo_list=list()
    fibo_list.append({'name':'Fibonacci 0.236','value':df_max['Fibo236'].values[0]})
    fibo_list.append({'name':'Fibonacci 0.382','value':df_max['Fibo382'].values[0]})
    fibo_list.append({'name':'Fibonacci 0.500','value':df_max['Fibo500'].values[0]})
    fibo_list.append({'name':'Fibonacci 0.618','value':df_max['Fibo618'].values[0]})
    fibo_list.append({'name':'Fibonacci 0.764','value':df_max['Fibo764'].values[0]})
    for fibo in fibo_list:
        fig.add_trace(
            go.Scatter(name=fibo['name'],x=[start_time,end_time],y=[fibo['value'],fibo['value']],line=dict(color="Red",width=2))
        )
    fig.add_trace(go.Scatter(
    x=[df_max.iloc[0]['FiboStartDate'],df_max.iloc[0]['Datetime']],
    y=[df_max.iloc[0]['FiboStartPrice'],df_max.iloc[0]['CloseLast']],
    marker=dict(color="crimson", size=10),
    mode="markers",
    name='Shallow Low - Shallow High'
    ))
    fig.update_layout(title_text=symbol)
    fig.show()
    
def plot_fibonacci(df,df_max,symbol):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=df['Datetime'], y=df['Close'], name='Price')
    )
    #fibo datetime
    start_time=df.iloc[0]['Datetime']
    end_time=df.iloc[-1]['Datetime']
    fibo_list=list()
    fibo_list.append({'name':'Fibonacci 0.236','value':df_max['Fibo236'].values[0]})
    fibo_list.append({'name':'Fibonacci 0.382','value':df_max['Fibo382'].values[0]})
    fibo_list.append({'name':'Fibonacci 0.500','value':df_max['Fibo500'].values[0]})
    fibo_list.append({'name':'Fibonacci 0.618','value':df_max['Fibo618'].values[0]})
    fibo_list.append({'name':'Fibonacci 0.764','value':df_max['Fibo764'].values[0]})
    for fibo in fibo_list:
        fig.add_trace(
            go.Scatter(name=fibo['name'],x=[start_time,end_time],y=[fibo['value'],fibo['value']],line=dict(color="Red",width=2))
        )
    fig.add_trace(go.Scatter(
    x=[df_max.iloc[0]['FiboStartDate'],df_max.iloc[0]['Datetime']],
    y=[df_max.iloc[0]['FiboStartPrice'],df_max.iloc[0]['CloseLast']],
    marker=dict(color="crimson", size=10),
    mode="markers",
    name='Shallow Low - Shallow High'
    ))
    fig.update_layout(title_text=symbol)
    fig.show()

