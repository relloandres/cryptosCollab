### Momentum Trading Strategy

With data from the Binance Exchange from January 2018 to July 2020, developed momentum trading strategy using exponential moving averages. 
The currency used is ETH/TUSD, for detailed information go to ipynb file. 
The files are:

  1. BinanceKey.py: Fill with own Binance API key, in order to be able to pull the data from the exchanve
  
  2. MovingAverageHistorical.ipynb: Finds optimal parameters for the momemtum trading strategy, using training, validation and test set
  
  3. Helpers.py: Functions used in MovingAverageHistorical.ipynb, functions to pull the historical data from the exchange, and to fit the EMA and define the trading strategy including trading fees.
