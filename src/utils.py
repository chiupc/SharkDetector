from datetime import datetime
import pandas as pd
import os

def distribute_requests(event):
    #split query time if longer than 1 day
    events=[]
    if(event['resolution']=='1'):
        diff=event['to']-event['from']
        if(diff>86400):
            while(event['to']>event['from']):                
                event_copy=event.copy()
                event_copy['from']=event_copy['to']-86400
                event['to']=event['to']-86400
                events.append(event_copy)
    else:
        events.append(event)
    return events

def build_event_lists(lists_,from_,to_,resolution_='1',csv_=1):
    events=[]
    for list_ in lists_:
        event={"category":list_['cat'],"symbol":list_['symbol'],"counter":list_['code'],"resolution":resolution_, "from":from_,"to":to_, "write_csv":csv_}
        events.append(event)
    return events

def build_quote_movements_csv(event):
    name_=event['symbol']+'_'+event['counter']
    date_=datetime.fromtimestamp(event['to']).strftime("%Y-%m-%d")
    csv = './history/quote_movements/'+ event['category'] +'/'+name_+'/'+name_ + '_' + date_ + '.csv'
    return csv
    
def build_price_history_csv(event):
    name_=event['symbol']+'_'+event['counter']
    date_=datetime.fromtimestamp(event['to']).strftime("%Y-%m-%d")
    csv = './history/price/'+ event['category'] +'/'+name_+'/'+name_ + '_' + date_ + '.csv'
    return csv

def build_force_dir(category):
    dir_='./history/calculated_data/'+ category +'/force/'
    return dir_
    
def build_force_filename(category):
    dir_=build_force_dir(category)
    filename=category.replace('&','').replace(' ','').lower()+'_force'
    return dir_+filename

def build_force_csv(category):
    dir_=build_force_dir(category)
    filename=category.replace('&','').replace(' ','').lower()+'_force.csv'
    return dir_+filename
    
def create_csv_dir(event):
    date_=datetime.fromtimestamp(event['to']).strftime("%Y-%m-%d")
    name_=event['symbol']+'_'+event['counter']
    data_list=['quote_movements','price','calculated_data']
    for data_item in data_list:
        dir_=os.path.join('history',data_item)
        dir_=os.path.join(dir_,event['category'])
        dir_=os.path.join(dir_,name_)
        if not os.path.exists(dir_): os.makedirs(dir_)

def get_counter_category(counter):
    listings=pd.read_csv('klse_listings.csv')
    return listings[listings['code']==counter]['cat'].values[0]
    
