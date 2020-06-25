from session_handler import *
from counter import Counter
import time

def main():
    generate_session()
    harta=Counter(symbol='HARTA',counter='5168',scheduler_on=True)
    #topglov=Counter(symbol='TOPGLOV',counter='7133',scheduler_on=True)
    supermx=Counter(symbol='SUPERMX',counter='7106',scheduler_on=True)
    myeg=Counter(symbol='MYEG',counter='0138',scheduler_on=True)
    inari=Counter(symbol='INARI',counter='0166',scheduler_on=True)
    gtronic=Counter(symbol='GTRONIC',counter='7022',scheduler_on=True)
    dsonic=Counter(symbol='DSONIC',counter='5216',scheduler_on=True)
    mi=Counter(symbol='MI',counter='5286',scheduler_on=True)
    while True:
        time.sleep(1)
    
if __name__ == "__main__":
    main()