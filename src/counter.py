import pandas as pd
from klse_scrapper import *
from shareinvestor_scrapper import *
from utils import *
from datetime import datetime,time,date,timedelta
from session_handler import *
from analytics import *
from apscheduler.schedulers.background import BackgroundScheduler

class Counter:
    def __init__(self, symbol, counter,scheduler_on):
        self.session=read_session()
        self.symbol = symbol
        self.counter = counter
        self.category = get_counter_category(counter)
        print(self.category)
        self.volume_threshold=self.get_volume_threshold()
        self.price=live_price(self.counter)
        #self.last_updated_time=1592381303
        self.last_updated_time=datetime.combine(date.today()-timedelta(days=3), time(17)).timestamp()
        self.event={'symbol':self.symbol,'counter':self.counter,'category':self.category,'to':self.last_updated_time}
        #self.today_open=pd.read_csv(build_price_history_csv(self.event)).iloc[-1]['Close']
        create_csv_dir(self.event) #Create directory for price, quotes_movements and calculated_data
        self.buffer=pd.DataFrame() #Buffer for raw quote movements data
        self.buffer_temp=pd.DataFrame()
        self.is_repeated=True
        self.last_done=pd.DataFrame()
        self.last_done_sell=0
        self.last_done_buy=0
        self.sell_queue=pd.DataFrame()
        self.buy_queue=pd.DataFrame()
        self.sharks=pd.DataFrame()
        self.shark_count={'buy_shark':0,'sell_shark':0}
        self.endtime=datetime.combine(date.today(), time(18)).timestamp()
        if scheduler_on:
            self.sched = BackgroundScheduler()
            self.sched.add_job(self.update_counter, 'interval', seconds=10,max_instances=3)
            self.sched.add_job(self.flush_buffer, 'interval', minutes=30,max_instances=3)
            self.sched.start()
        
    def update_last_updated_timestamp(self):
        self.last_updated_time=datetime.now().timestamp()
        self.event['to']=self.last_updated_time
        
    def set_timestamp(self,timestamp):
        self.last_updated_time=timestamp
        self.event['to']=self.last_updated_time
    
    def refresh_price(self):
        self.price=live_price(self.counter)
    
    def get_volume(self,live):
        if not live:
            csvpath=build_quote_movements_csv(self.event)
            if os.path.exists(csvpath):
                df_=pd.read_csv(csvpath,parse_dates=['time'])
            else:
                df_=get_quote_movements(self.session,self.event,live=live)
        else:
            df_=get_quote_movements(self.session,self.event,live=False)
        df_=df_.iloc[::-1].reset_index().drop(columns=['index'])
        self.is_repeated=self.buffer_temp.equals(df_)
        print(self.is_repeated)
        if not self.is_repeated:
            #clear temp buffer
            self.buffer=self.buffer.append(self.buffer_temp.copy())
            self.buffer_temp=pd.DataFrame()
            self.buffer_temp=df_.copy()
            df_=split_buy_sell_queue(df_)
            self.sell_queue=df_[['time','sell_vol_chg','sell_queue_price']]
            self.buy_queue=df_[['time','buy_vol_chg','buy_queue_price']]
            last_done_df=df_[['time','last_done_vol','last_done_price','type']]
            self.last_done['last_done_price']=last_done_df['last_done_price'].fillna(method='ffill').fillna(self.today_open)
            self.last_done['price_pct_open']=self.last_done['last_done_price'].transform(lambda x: round((x-self.today_open)/self.today_open*100,2))
            self.last_done['last_done_sell_vol']=last_done_df[last_done_df['type']=='Sell Down'].last_done_vol.cumsum()
            self.last_done['last_done_sell_vol']=self.last_done['last_done_sell_vol'].fillna(method='ffill').fillna(0)
            self.last_done['last_done_sell_vol']=self.last_done['last_done_sell_vol']+self.last_done_sell
            self.last_done['last_done_buy_vol']=last_done_df[last_done_df['type']=='Buy Up'].last_done_vol.cumsum()
            self.last_done['last_done_buy_vol']=self.last_done['last_done_buy_vol'].fillna(method='ffill').fillna(0)
            self.last_done['last_done_buy_vol']=self.last_done['last_done_buy_vol']+self.last_done_sell
            self.last_done_sell=self.last_done.iloc[-1]['last_done_sell_vol']
            self.last_done_buy=self.last_done.iloc[-1]['last_done_buy_vol']
            
        
    def get_day_volume(self):
        self.get_volume(False)
        
    def refresh_volume(self):
        self.get_volume(True)    
        
    def update_counter(self):
        try:
            self.update_last_updated_timestamp()
            self.refresh_price()       
            self.refresh_volume()
            if not self.is_repeated:
                self.detect_shark()
        except Exception as e:
            print(e)
        if(self.last_updated_time>self.endtime):
            self.sched.shutdown()
        
    def get_volume_threshold(self):
        df_=pd.read_feather(build_force_filename(self.category))
        df_['counter']=df_['counter'].astype(str)
        df_['counter']=df_['counter'].str.zfill(4)
        volume_threshold=df_[df_['counter']==self.counter].iloc[-1].to_dict()
        return volume_threshold
    
    def detect_shark(self):
        df_,shark_count=out_of_threshold(self.symbol,self.counter,self.volume_threshold,self.buy_queue,self.sell_queue,self.last_done,self.shark_count)
        self.sharks=self.sharks.append(df_)
        self.shark_count=shark_count
                
    def flush_buffer(self):
        csv_name=build_quote_movements_csv(self.event)
        if not os.path.exists(csv_name):
            self.buffer.to_csv(csv_name,index=False)
        else:
            self.buffer.to_csv(csv_name, mode='a', header=False,index=False)
        self.buffer=pd.DataFrame()