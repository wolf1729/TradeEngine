# %%
from lumibot.brokers import Alpaca


# %%
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from datetime import datetime 
from alpaca_trade_api import REST 
from timedelta import Timedelta 
from filbert_utils import estimate_sentiment
import os
from dotenv import load_dotenv
load_dotenv()

# %%
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = os.getenv("BASE_URL")

ALPACA_CREDS = {
    "API_KEY": API_KEY,
    "API_SECRET": API_SECRET,
    "PAPER": True
}

class MLTrader(Strategy):
    def initialize(self,symbols=["SPY"], cash_at_risk: float=0.5): #initialize method will run once
        self.symbols = symbols
        self.sleeptime = "24H" #how frequently we are gonna trade
        self.last_trade = {symbol: None for symbol in symbols} #capture what the last trade is to undo our buys
        self.cash_at_risk = cash_at_risk
        self.api=REST(key_id=API_KEY,secret_key=API_SECRET,base_url=BASE_URL)

    def position_sizing(self,symbol):
        cash = self.get_cash()
        last_price = self.get_last_price(symbol)
        quantity = round(cash * self.cash_at_risk / last_price,0) #how much cash balance we use per trade
        return cash,last_price, quantity
    
    def get_dates(self):
        
        today = self.get_datetime()
        three_days_prior = today - Timedelta(days=3)
        return today.strftime('%Y-%m-%d'), three_days_prior.strftime('%Y-%m-%d')
    
    def get_sentiment(self):
        today,three_days_prior = self.get_dates()
        news = self.api.get_news(symbol=self.symbols[0], start=three_days_prior, end=today)    
        news=[ev.__dict__["_raw"]["headline"] for ev in news]
        probablity, sentiment = estimate_sentiment(news)
        return probablity, sentiment

    def on_trading_iteration(self): #everytime we get a new data, execute the trade
        for symbol in self.symbols:
            cash, last_price, quantity = self.position_sizing(symbol)
            probablity, sentiment = self.get_sentiment()
            
            if cash > last_price:
                if sentiment == "positive" and probablity > .999:
                    if self.last_trade[symbol] == "sell":
                        self.sell_all(symbol)
                    
                    order = self.create_order(
                        symbol,
                        quantity,
                        "buy",
                        type="bracket", 
                        take_profit_price=last_price * 1.05,
                        stop_loss_price=last_price * 0.95
                    )
                    self.submit_order(order)
                    self.last_trade[symbol] = "buy" 
                
            elif sentiment == "negative" and probablity > .999:
                if self.last_trade[symbol] == "sell":
                    self.sell_all(symbol)
                    
                order = self.create_order(
                    symbol,
                    quantity,
                    "sell",
                    type="bracket", 
                    take_profit_price=last_price * 0.8,
                    stop_loss_price=last_price * 1.05
                )
                self.submit_order(order)
                self.last_trade[symbol] = "sell"    


start_date = datetime(2023,11,15)
end_date = datetime(2023,12,31)
symbols = ["TSLA"] 

broker = Alpaca(ALPACA_CREDS)
strategy = MLTrader(name='mlstrat', broker=broker)
strategy.initialize(symbols=symbols, cash_at_risk=0.5)


strategy.backtest(
    YahooDataBacktesting,
    start_date,
    end_date,
    parameters={"symbols": symbols}
)


