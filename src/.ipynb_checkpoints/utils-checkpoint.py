def distribute_requests(event):
    #split query time if longer than 1 day
    events=[]
    if(event['resolution']=='1m'):
        diff=event['to']-event['from']
        if(diff>86400):
            while(event['to']>event['from']):                
                event_copy=event.copy()
                event_copy['from']=event_copy['to']-86400
                event['to']=event['to']-86400
                events.append(event_copy)
    return events

def build_event_lists(lists_,from_,to_,resolution_='1m',csv_=1):
    events=[]
    for list_ in lists_:
        event={"category":list_['cat'],"symbol":list_['symbol'],"counter":list_['code'],"resolution":resolution_, "from":from_,"to":to_, "write_csv":csv_}
        events.append(event)
    return events

