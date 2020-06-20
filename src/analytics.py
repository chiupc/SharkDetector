import pandas as pd
from messenger_handler import *

def out_of_threshold(symbol,counter,volume_threshold,buy_queue,sell_queue,last_done):
    df_=pd.DataFrame()
    buy_queue_mean=volume_threshold['buy_vol_chg_max_mean']
    buy_queue_plusonesig=volume_threshold['buy_vol_chg_max_mean']+volume_threshold['buy_vol_chg_max_std']
    buy_queue_minusonesig=volume_threshold['buy_vol_chg_max_mean']-volume_threshold['buy_vol_chg_max_std']
    buy_queue=buy_queue.dropna()
    buy_big_oot_list=buy_queue[buy_queue['buy_vol_chg']>=buy_queue_plusonesig]
    buy_normal_oot_list=buy_queue[buy_queue['buy_vol_chg']<buy_queue_plusonesig]
    buy_normal_oot_list=buy_normal_oot_list[buy_normal_oot_list['buy_vol_chg']>=buy_queue_mean]
    buy_small_oot_list=buy_queue[buy_queue['buy_vol_chg']>=buy_queue_minusonesig]
    buy_small_oot_list=buy_small_oot_list[buy_small_oot_list['buy_vol_chg']<buy_queue_mean]
    #sell_queue=sell_queue.dropna()
    #sell_queue_mean=volume_threshold['sell_vol_chg_max_mean']
    #sell_queue_plusonesig=volume_threshold['sell_vol_chg_max_mean']+volume_threshold['sell_vol_chg_max_std']
    #sell_queue_minusonesig=volume_threshold['sell_vol_chg_max_mean']-volume_threshold['sell_vol_chg_max_std']
    #sell_big_oot_list=sell_queue[sell_queue['sell_vol_chg']>=sell_queue_plusonesig]
    #sell_normal_oot_list=sell_queue[sell_queue['sell_vol_chg']<sell_queue_plusonesig]
    #sell_normal_oot_list=sell_normal_oot_list[sell_normal_oot_list['sell_vol_chg']>=sell_queue_mean]
    #sell_small_oot_list=sell_queue[sell_queue['sell_vol_chg']>=sell_queue_minusonesig]
    #sell_small_oot_list=sell_small_oot_list[sell_small_oot_list['sell_vol_chg']<sell_queue_mean]    
    #
    #add last done price & volume
    buy_big_oot_list=add_last_done(buy_big_oot_list,last_done)
    buy_normal_oot_list=add_last_done(buy_normal_oot_list,last_done)
    buy_small_oot_list=add_last_done(buy_small_oot_list,last_done)
    #
    #append buy & sell list
    df_=df_.append(buy_big_oot_list).append(buy_normal_oot_list).append(buy_small_oot_list)
    #df_=df_.append(sell_big_oot_list).append(sell_normal_oot_list).append(sell_small_oot_list)
    should_send_volume_alert(symbol,counter,'buy','Big Shark',buy_big_oot_list)
    should_send_volume_alert(symbol,counter,'buy','Normal Shark',buy_normal_oot_list)
    should_send_volume_alert(symbol,counter,'buy','Small Shark',buy_small_oot_list)
    #should_send_volume_alert(symbol,counter,'sell','Big Shark',sell_big_oot_list)
    #should_send_volume_alert(symbol,counter,'sell','Normal Shark',sell_normal_oot_list)
    #should_send_volume_alert(symbol,counter,'sell','Small Shark',sell_small_oot_list)
    return df_
    
def should_send_volume_alert(symbol,counter,queue_type_,oot_type_,oot_list_):
    if len(oot_list_)>0:
        message=build_alert_message(symbol,counter,queue_type_,oot_type_,oot_list_)
        send_volume_alert(message)

def add_last_done(oot_list_,last_done):
    oot_list_['last_done_price']=last_done.iloc[oot_list_.index.tolist()]['last_done_price']
    oot_list_['price_pct_open']=last_done.iloc[oot_list_.index.tolist()]['price_pct_open']
    oot_list_['last_done_buy_vol']=last_done.iloc[oot_list_.index.tolist()]['last_done_buy_vol']
    oot_list_['last_done_sell_vol']=last_done.iloc[oot_list_.index.tolist()]['last_done_sell_vol']
    return oot_list_
   
def build_alert_message(symbol,counter,queue_type_,oot_type_,oot_list_):
    message=oot_type_ + '\nSymbol: ' + symbol + ' (' + counter + ')\n'
    for i in range(len(oot_list_)):
        if(queue_type_=='buy'):
            #message=message+'Time: '+str(oot_list_.iloc[i]['time'])+' | '
            #message=message+'Buy Queue Price: '+str(oot_list_.iloc[i]['buy_queue_price'])+' | '
            #message=message+'Buy Queue Volume: '+str(oot_list_.iloc[i]['buy_vol_chg'])+'\n'
            #break line
            message=message+'Time: '+str(oot_list_.iloc[i]['time'])+'\n'
            message=message+'Buy Queue Price: '+str(oot_list_.iloc[i]['buy_queue_price'])+'\n'
            message=message+'Buy Queue Volume: '+str(oot_list_.iloc[i]['buy_vol_chg'])+'\n'
            message=message+'Last Done Price: '+str(oot_list_.iloc[i]['last_done_price'])+'\n'
            message=message+'Price Change Pct: '+str(oot_list_.iloc[i]['price_pct_open'])+'\n'
            message=message+'Last Done Buy Volume: '+str(oot_list_.iloc[i]['last_done_buy_vol'])+'\n'
            message=message+'Last Done Sell Volume: '+str(oot_list_.iloc[i]['last_done_sell_vol'])+'\n'
            message=message+'-----------------\n'
        elif(queue_type_=='sell'):
            #message=message+'Time: '+str(oot_list_.iloc[i]['time'])+' | '
            #message=message+'Sell Queue Price: '+str(oot_list_.iloc[i]['sell_queue_price'])+' | '
            #message=message+'Sell Queue Volume: '+str(oot_list_.iloc[i]['sell_vol_chg'])+'\n'
            #break line
            message=message+'Time: '+str(oot_list_.iloc[i]['time'])+'\n'
            message=message+'Sell Queue Price: '+str(oot_list_.iloc[i]['sell_queue_price'])+'\n'
            message=message+'Sell Queue Volume: '+str(oot_list_.iloc[i]['sell_vol_chg'])+'\n'
            message=message+'Last Done Price: '+str(oot_list_.iloc[i]['last_done_price'])+'\n'
            message=message+'Price Change Pct: '+str(oot_list_.iloc[i]['price_pct_open'])+'\n'
            message=message+'Last Done Buy Volume: '+str(oot_list_.iloc[i]['last_done_buy_vol'])+'\n'
            message=message+'Last Done Sell Volume: '+str(oot_list_.iloc[i]['last_done_sell_vol'])+'\n'
            message=message+'-----------------\n'
    return message
        
    
    

    