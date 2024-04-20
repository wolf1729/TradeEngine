from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from datetime import datetime

API_KEY= 'PKJHYUEHVBESQUYLQJ5Z'
API_SECRET="tukk96fcOY5cIyBdKCTTsyoA8dpR0M5DzS8WFjXF"
BASE_URL = 'https://paper-api.alpaca.markets/v2'

ALPACA_CREDS = {
    'API_KEY':API_KEY,
    'API_SECRET':API_SECRET,
    'PAPER':True
}
start_date=datetime(2023,12,15)
end_date=datetime(2023,12,31)

class MLTrader(Strategy):
    def initialize(self,symbol:str="SPY"):
        self.symbol = symbol
        self.sleeptime = '24H'
        self.last_trade = None
        pass
    def on_trading_iteration(self):
        if self.last_trade==None:
            order = self.create_order(
                self.symbol,
                10,
                'buy',
                type='market')

broker = Alpaca(ALPACA_CREDS)
strategy = MLTrader(name='mlstrat',broker=broker,parameters={'symbol':"SPY"})
strategy.backtest(
    YahooDataBacktesting,
    start_date,
    end_date,
    parameters={'symbol':"SPY"}
)
        