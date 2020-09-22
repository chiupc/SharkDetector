import requests
from bs4 import BeautifulSoup
import pandas as pd
from session_handler import *
import json
from datetime import datetime,date,timezone
import pytz
import urllib.parse
from klse_scrapper import *
from utils import *
import os
from workalendar.asia import Malaysia
from data_utils import *
import re

sgtz=pytz.timezone('Asia/Singapore')

def crawl_time_sales(session,event):
    date_=datetime.fromtimestamp(event['to']).strftime("%Y%m%d")
    URL = 'http://www.shareinvestor.com/prices/time_and_sales_f.html'
    params={'date':date_,'counter':event['counter']+'.MY','page':-1}
    params=urllib.parse.urlencode(params)
    URL=URL+'?'+params
    page = session.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    rows=soup.find('table',{'id':"sic_timeAndSalesTable"}).findAll('tr')
    lists=[]
    for i in range(2,len(rows)):
        raw_vals=rows[i].findAll('td')
        time_=raw_vals[0].text
        type_=raw_vals[1].text
        last_done_=float(raw_vals[2].text)
        price_chg_=raw_vals[3].text
        vol_chg_=int(raw_vals[4].text.replace(',',''))
        vol_total_=int(raw_vals[5].text.replace(',',''))
        row={'time':date_+' '+time_,'type':type_,'last_done':last_done_,'price_chg':price_chg_,'vol_chg':vol_chg_,'vol_total':vol_total_}
        lists.append(row)
    df=pd.DataFrame(lists).set_index('time')
    df.to_csv('test.csv')
    
# def crawl_quote_movements(session,event,live=False):
#     print(event)
#     date_=datetime.fromtimestamp(event['to'])
#     date_=date_.strftime("%Y-%m-%d")
#     empty_chars='\xa0'     
#     URL = 'http://www.shareinvestor.com/prices/quote_movements_f.html'
#     if live:
#         pageno=1
#     else:
#         pageno=-1
#     params={'date':date_,'counter':event['counter']+'.MY','page':pageno}
#     params=urllib.parse.urlencode(params)
#     URL=URL+'?'+params
#     page = session.get(URL)
#     soup = BeautifulSoup(page.content, 'html.parser')
#     rows=soup.find('table',{'id':"sic_quoteMovementTable"}).findAll('tr')
#     lists=[]
#     for i in range(2,len(rows)):
#         raw_vals=rows[i].findAll('td')
#         if(len(raw_vals)>=7):
#             time_=raw_vals[0].text
#             bq_vol_ = None if raw_vals[1].text==empty_chars else raw_vals[1].text
#             try:
#                 bq_price_=float(raw_vals[2].text)
#             except Exception as e:
#                 bq_price_=None
#             ld_vol=None if raw_vals[3].text==empty_chars else float(raw_vals[3].text.replace(',',''))
#             try:
#                 ld_price=float(raw_vals[4].text)
#             except Exception as e: 
#                 ld_price=None
#             type_=None if raw_vals[5].text==empty_chars else raw_vals[5].text
#             sq_vol_=None if raw_vals[6].text==empty_chars else raw_vals[6].text
#             try:
#                 sq_price_=float(raw_vals[7].text)
#             except Exception as e:
#                 sq_price_=None
#             row={'time':date_+' '+time_,'buy_queue_vol':bq_vol_,'buy_queue_price':bq_price_,'last_done_vol':ld_vol,'last_done_price':ld_price,'type':type_,'sell_queue_vol':sq_vol_,'sell_queue_price':sq_price_}
#             lists.append(row)
#     df=pd.DataFrame(lists).set_index('time')
#     return df


def crawl_quote_movements(session,event,live=False):
    date_=datetime.fromtimestamp(event['to'])
    date_=date_.strftime("%Y-%m-%d")    
    URL = 'http://www.shareinvestor.com/prices/quote_movements_f.html'
    if live:
        pageno=1
    else:
        pageno=-1
    params={'date':date_,'counter':event['counter']+'.MY','page':pageno}
    params=urllib.parse.urlencode(params)
    URL=URL+'?'+params
    page = session.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    table=soup.find('table',{'id':"sic_quoteMovementTable"})
    #use pandas read_html as a more straightforward to parse html table
    df = pd.read_html(str(table))[0]
    new_cols = list()
    for col in df.columns.values:
        if col[0] == col[1]: new_cols.append(col[0].lower())
        else: new_cols.append(' '.join(col).lower().replace(' ','_'))
    df.columns = new_cols
    tmp=df['buy_queue_vol'].str.replace(',','')
    tmp=tmp.str.split(' ',expand=True)
    df['buy_vol_chg']=tmp[0].str.extract("\((.*?)\)").astype(float)
    df['buy_queue_vol']=tmp[1].astype(float)
    tmp=df['sell_queue_vol'].str.replace(',','')
    tmp=tmp.str.split(' ',expand=True)
    df['sell_vol_chg']=tmp[0].str.extract("\((.*?)\)").astype(float)
    df['sell_queue_vol']=tmp[1].astype(float)
    df['time']=pd.to_datetime(df['time'])
    return df

def get_quote_movements(session,event,live=True):
    df_=crawl_quote_movements(session,event,live)
    date_=event['to']
    for i,row in df_.iterrows():
        if(row['time'].replace(tzinfo=sgtz).timestamp()<date_):
            break    
    return df_[0:i-1]

def mine_quote_movements(session,board,category,from_,to_):
    df=get_board_category_listings(board,category)
    lists_=df[['symbol','code','cat']].to_dict('records')
    events=build_event_lists(lists_=lists_,from_=from_,to_=to_)    
    for event in events:
        events_=distribute_requests(event)
        print(events_)
        for event_ in events_:
            try:
                cal = Malaysia()
                date_=datetime.fromtimestamp(event_['to'])
                if(cal.is_working_day(date(date_.year,date_.month,date_.day))):
                    date_=date_.strftime("%Y-%m-%d")
                    dir_='history/quote_movements/'
                    dir_=os.path.join(dir_,event_['category'])
                    name=event_['symbol']+'_'+event_['counter']
                    dir_=os.path.join(dir_,name)
                    if not os.path.exists(dir_): os.makedirs(dir_)
                    save_path=os.path.join(dir_,name)+'_'+date_+'.csv'
                    #if csv exists, return dataframe from existing csv
                    if os.path.exists(save_path): 
                        print('CSV exists. Not going to crawl.')
                    else:
                        df=crawl_quote_movements(session,event_)
                        df.set_index('time').to_csv(save_path)
            except Exception as e: print(e)

def split_buy_sell_queue(df_):
    def raw_queue_to_vol_chg(str_):
        found=re.findall('\((.*?)\)', str_)
        if found:
            return float(found[0])
        #else:
        #    found=re.findall('\d+', str_)
        #    return int(found[0])
    def raw_queue_to_queue_vol(str_):
        splits=str_.split()
        return float(splits[-1])
    df_['buy_queue_vol']=df_['buy_queue_vol'].str.replace(',','')
    df_['sell_queue_vol']=df_['sell_queue_vol'].str.replace(',','')
    df_['buy_vol_chg']=df_['buy_queue_vol'].dropna().astype(str).apply(raw_queue_to_vol_chg)
    df_['sell_vol_chg']=df_['sell_queue_vol'].dropna().astype(str).apply(raw_queue_to_vol_chg)
    df_['buy_queue_vol']=df_['buy_queue_vol'].dropna().astype(str).apply(raw_queue_to_queue_vol)
    df_['sell_queue_vol']=df_['sell_queue_vol'].dropna().astype(str).apply(raw_queue_to_queue_vol)
    return df_