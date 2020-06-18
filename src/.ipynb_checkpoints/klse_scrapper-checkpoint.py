import requests
from bs4 import BeautifulSoup
import pandas as pd


def live_price(counter):
    URL = 'https://www.klsescreener.com/v2/stocks/view/'+str(counter)
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    price=soup.find(id='price')
    return float(price.text)

def live_volume(counter):
    URL = 'https://www.klsescreener.com/v2/stocks/view/'+str(counter)
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    volume=soup.find(id='volume')
    volume=int(volume.text.replace(',',''))
    return volume

def live_bs_volume(counter):
    URL = 'https://www.klsescreener.com/v2/stocks/view/'+str(counter)
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    volume=soup.find(id='volumeBuySell')
    volumes=volume.text.split('/')
    volume_buy=int(volumes[0].replace(',',''))
    volume_sell=int(volumes[1].replace(',',''))
    return volume_buy, volume_sell

def live_volume_stats(counter):
    URL = 'https://www.klsescreener.com/v2/stocks/view/'+str(counter)
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    avg_vol=soup.find("td", text="Average Volume").find_next_sibling("td").text
    rel_vol=soup.find("td", text="Relative Volume").find_next_sibling("td").text    
    stoc=soup.find("td", text="Stochastic(14)").find_next_sibling("td").text
    rsi=soup.find("td", text="RSI(14)").find_next_sibling("td").text
    avg_vol = int(avg_vol.split()[0].replace(',',''))
    rel_vol = float(rel_vol.split()[0].replace(',',''))
    stoc = float(stoc.split()[1].replace(',',''))
    rsi = float(rsi.split()[1].replace(',',''))
    vol_stats={"rsi":rsi,"stochastic":stoc,"average_volume":avg_vol,"relative_volume":rel_vol}
    return vol_stats

def get_listings():
    URL = 'https://www.klsescreener.com/v2/screener/quote_results?getquote=1'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    lists = soup.findAll('tr', {'class': 'list'})
    co_={"title":[],"symbol":[],"code":[],"board":[],"cat":[],"capital":[],"vol":[]}
    for list_ in lists:
        first_td_=list_.find('td')
        title_=first_td_['title'] #find will return the first element in td list
        symbol_=first_td_.find('a').text
        code_=list_.find('td', {'title':'Code'}).text.strip()
        raw_cat_=list_.find('td', {'title':'Category'}).text.split(',')
        cat_=raw_cat_[0]
        if(len(raw_cat_)>1):
            board_=raw_cat_[1].strip()
        else:
            board_=''
        capital_=float(list_.find('td', {'title':'Market Capital'}).text)
        vol_=float(list_.find('td', {'title':'Volume'}).text)       
        co_["title"].append(title_)
        co_["symbol"].append(symbol_)
        co_["code"].append(code_)
        co_["board"].append(board_)
        co_["cat"].append(cat_)
        co_["capital"].append(capital_)
        co_["vol"].append(vol_)
    df = pd.DataFrame(data=co_)
    df.to_csv('klse_listings.csv',index=False)
    return df

def get_board_category_listings(board,cat):
    df = pd.read_csv('klse_listings.csv')
    df=df[df['board']==board]
    df=df[df['cat']==cat]
    return df
    