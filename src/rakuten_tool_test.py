from autobrowser.rakuten_tool import RakutenTool

rakuten_tool = RakutenTool('chiupc94', '@ezpcFTW11967')
rakuten_tool.login()
cashbalance=rakuten_tool.get_cash_balance()
print(cashbalance)
df_orderstatus=rakuten_tool.get_orders()
print(df_orderstatus)
df_tradehistory=rakuten_tool.get_trade_history()
print(df_tradehistory)
#rakuten_tool.navigate_to_stock_page('5199', 'HIBISCS')
#rakuten_tool.buy_order(lot_qty=5, buy_price=0.60,trading_pin=387215)