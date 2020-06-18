import pandas as pd
from utils import *
from datetime import datetime
from workalendar.asia import Malaysia
from klse_scrapper import *

def split_buy_sell_queue(df_):
    def split_queue(col):
        test=df_[col].str.split(" ", n = 1, expand = True)
        buy_vol_chg=list()
        buy_vol = list()
        for item in list(test[0].fillna('0').values):
            try:
                buy_vol_chg.append(int(item.replace(',','').replace('(','').replace(')','')))
            except Exception as e:
                buy_vol_chg.append(0)
        for item in list(test[1].fillna('0').values):
            try:
                buy_vol.append(int(item.replace(',','')))
            except Exception as e:
                buy_vol.append(0)
        return buy_vol_chg,buy_vol 
    buy_vol_chg,buy_vol =split_queue('buy_queue_vol')
    sell_vol_chg,sell_vol =split_queue('sell_queue_vol')
    df_['buy_queue_vol']=buy_vol
    df_['buy_vol_chg']=buy_vol_chg
    df_['sell_queue_vol']=sell_vol
    df_['sell_vol_chg']=sell_vol_chg
    return df_

def calculate_force_data(event_,interval='1min'):
    date_=datetime.fromtimestamp(event_['to']).strftime("%Y-%m-%d")
    csv_path=build_quote_movements_csv(event_)
    row={'symbol':event_['symbol'],'counter':event_['counter'],'date':date_}
    if os.path.exists(csv_path):
        df_=pd.read_csv(csv_path,parse_dates=['time'])
        df_=split_buy_sell_queue(df_)
        df_=df_.iloc[::-1]
        df_=df_.set_index('time')
        dfcal_=pd.DataFrame()
        dfcal_=df_[df_['type'].notna()].resample(interval).agg({'last_done_vol':'sum','last_done_price':'last'})
        dfcal_['price_change_pct']=dfcal_['last_done_price'].pct_change()*100
        dfcal_['force']=dfcal_['price_change_pct']*dfcal_['last_done_vol']
        row['force_sum']=dfcal_['force'].sum()
        row['force_max']=dfcal_['force'].max()
        row['force_min']=dfcal_['force'].min()
        row['force_mean']=dfcal_['force'].mean()
        row['force_std']=dfcal_['force'].std()
        row['price_change_min']=dfcal_['price_change_pct'].min()
        row['price_change_max']=dfcal_['price_change_pct'].max()
        row['price_change_std']=dfcal_['price_change_pct'].std()
        row['buy_vol_chg_max']=df_.resample(interval).agg({'buy_vol_chg':'max'})['buy_vol_chg'].max()
        row['buy_vol_chg_mean']=df_.resample(interval).agg({'buy_vol_chg':'mean'})['buy_vol_chg'].mean()
        row['sell_vol_chg_max']=df_.resample(interval).agg({'sell_vol_chg':'max'})['sell_vol_chg'].max()
        row['sell_vol_chg_mean']=df_.resample(interval).agg({'sell_vol_chg':'mean'})['sell_vol_chg'].mean()
        return row

def mine_force_data(board,category,from_,to_,interval):
    date_start=datetime.fromtimestamp(from_).strftime("%Y-%m-%d")
    date_end=datetime.fromtimestamp(to_).strftime("%Y-%m-%d")
    dir_=build_force_dir(category)
    if not os.path.exists(dir_): os.makedirs(dir_)   
    df=get_board_category_listings(board,category)
    lists_=df[['symbol','code','cat']].to_dict('records')
    events=build_event_lists(lists_=lists_,from_=from_,to_=to_)
    rows=[]
    for event in events:
        events_=distribute_requests(event)
        for event_ in events_:
            csv_path=build_quote_movements_csv(event_)
            if os.path.exists(csv_path):
                try:
                    row=calculate_force_data(event_,interval)
                    rows.append(row)
                except Exception as e:
                    print('Error occurred when processing: '+csv_path + '\nError: ' + str(e))
    df_=pd.DataFrame(rows)
    path=build_force_csv(category)
    df_.to_csv(path,index=False)
    
def bulk_update_threshold(category,interval):
    df_cal=pd.DataFrame()
    dir_='./history/calculated_data/'+ category +'/force/'
    filename=category.replace('&','').replace(' ','').lower()+'_force'
    df_=pd.read_csv(dir_+filename+'.csv',parse_dates=['date'],index_col='date')
    df_=df_.iloc[::-1]
    df_cal['buy_vol_chg_max_mean']=df_.groupby(['symbol','counter']).rolling(interval).agg({'buy_vol_chg_max':'mean'})['buy_vol_chg_max']
    df_cal['buy_vol_chg_max_std']=df_.groupby(['symbol','counter']).rolling(interval).agg({'buy_vol_chg_max':'std'})['buy_vol_chg_max']
    df_cal['sell_vol_chg_max_mean']=df_.groupby(['symbol','counter']).rolling(interval).agg({'sell_vol_chg_max':'mean'})['sell_vol_chg_max']
    df_cal['sell_vol_chg_max_std']=df_.groupby(['symbol','counter']).rolling(interval).agg({'sell_vol_chg_max':'std'})['sell_vol_chg_max']
    df_cal.reset_index().to_feather(dir_+filename)
    return df_cal