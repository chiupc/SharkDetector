from session_handler import *
from datetime import time as dtime
from datetime import date,datetime,timedelta
from klse_scrapper import *
from shareinvestor_scrapper import *
import sys

#test case for mine price data
def main():
    session=read_session()
    category=sys.argv[1]
    istodaydata=sys.argv[2]
    if istodaydata=="true":
        tomorrow=date.today()+ timedelta(days=1)
        yesterday=date.today() - timedelta(days=1)
        to_=datetime.combine(tomorrow, dtime(9)).timestamp()   
        from_=datetime.combine(yesterday, dtime(9)).timestamp()
    else:
        from_=int(sys.argv[3])
        to_=int(sys.argv[4])
    mine_price_data('Main Market',category,'1m',from_,to_)
    mine_quote_movements(session=session,board='Main Market',category=category,from_=from_,to_=to_)

if __name__ == "__main__":
    main()