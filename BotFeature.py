import logging
import numpy as np
import pandas as pd
from binance.um_futures import UMFutures
from binance.lib.utils import config_logging
from binance.error import ClientError
import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates

# Load API keys from config.json
import json
with open('config.json') as config_file:
    config = json.load(config_file)
    api_key = config['api_key']
    api_secret = config['api_secret']

# Configure logging
config_logging(logging, logging.DEBUG)

# Initialize the Binance Futures client
client = UMFutures(key=api_key, secret=api_secret)

# Set leverage and order parameters
symbol = "MANAUSDT"
leverage = 20  # Set leverage to 20x
risk_percent = 0.02  # Risk percentage for stop loss (2%)
reward_risk_ratio = 3  # 3:1 profit-to-loss ratio

# Fetch historical data from Binance
def fetch_historical_data(symbol, interval, limit=500):
    candles = client.klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
    df['Date'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['Date'] = df['Date'].apply(mpl_dates.date2num)
    df = df[['Date', 'open', 'high', 'low', 'close']].astype(float)
    return df

# Define the support and resistance detection functions
def isSupport(df, i):
    return df['low'][i] < df['low'][i-1] and df['low'][i] < df['low'][i+1] and df['low'][i+1] < df['low'][i+2] and df['low'][i-1] < df['low'][i-2]

def isResistance(df, i):
    return df['high'][i] > df['high'][i-1] and df['high'][i] > df['high'][i+1] and df['high'][i+1] > df['high'][i+2] and df['high'][i-1] > df['high'][i-2]

def isFarFromLevel(levels, l, s):
    return np.sum([abs(l - x) < s for x in levels]) == 0

# Detect key levels (support/resistance) in the data
def detect_key_levels(df):
    levels = []
    s = np.mean(df['high'] - df['low'])  # Average candle size as a filter for nearby levels
    
    for i in range(2, df.shape[0] - 2):
        if isSupport(df, i):
            l = df['low'][i]
            if isFarFromLevel(levels, l, s):
                levels.append((i, l))
        elif isResistance(df, i):
            l = df['high'][i]
            if isFarFromLevel(levels, l, s):
                levels.append((i, l))
    return levels

# Plot the candlestick chart with support and resistance levels using matplotlib
def plot_levels(df, levels):
    fig, ax = plt.subplots()
import logging
import numpy as np
import pandas as pd
from binance.um_futures import UMFutures
from binance.lib.utils import config_logging
from binance.error import ClientError
import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates

# Load API keys from config.json
import json
with open('config.json') as config_file:
    config = json.load(config_file)
    api_key = config['api_key']
    api_secret = config['api_secret']

# Configure logging
config_logging(logging, logging.DEBUG)

# Initialize the Binance Futures client
client = UMFutures(key=api_key, secret=api_secret)

# Set leverage and order parameters
symbol = "MANAUSDT"
leverage = 20  # Set leverage to 20x
risk_percent = 0.02  # Risk percentage for stop loss (2%)
reward_risk_ratio = 3  # 3:1 profit-to-loss ratio

# Fetch historical data from Binance
def fetch_historical_data(symbol, interval, limit=500):
    try:
        candles = client.klines(symbol=symbol, interval=interval, limit=limit)
        df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
        df['Date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['Date'] = df['Date'].apply(mpl_dates.date2num)
        df = df[['Date', 'open', 'high', 'low', 'close']].astype(float)
        return df
    except ClientError as error:
        logging.error(f"Error fetching historical data: {error}")

# Define the support and resistance detection functions
def isSupport(df, i):
    return df['low'][i] < df['low'][i-1] and df['low'][i] < df['low'][i+1] and df['low'][i+1] < df['low'][i+2] and df['low'][i-1] < df['low'][i-2]

def isResistance(df, i):
    return df['high'][i] > df['high'][i-1] and df['high'][i] > df['high'][i+1] and df['high'][i+1] > df['high'][i+2] and df['high'][i-1] > df['high'][i-2]

def isFarFromLevel(levels, l, s):
    return np.sum([abs(l - x) < s for x in levels]) == 0

# Detect key levels (support/resistance) in the data
def detect_key_levels(df):
    levels = []
    s = np.mean(df['high'] - df['low'])  # Average candle size as a filter for nearby levels
    
    for i in range(2, df.shape[0] - 2):
        if isSupport(df, i):
            l = df['low'][i]
            if isFarFromLevel(levels, l, s):
                levels.append((i, l))
        elif isResistance(df, i):
            l = df['high'][i]
            if isFarFromLevel(levels, l, s):
                levels.append((i, l))
    return levels

# Plot the candlestick chart with support and resistance levels using matplotlib
def plot_levels(df, levels):
    try:
        fig, ax = plt.subplots()

        # Plot candlesticks manually
        for idx in range(len(df)):
            color = 'green' if df['close'][idx] >= df['open'][idx] else 'red'
            ax.plot([df['Date'][idx], df['Date'][idx]], [df['low'][idx], df['high'][idx]], color=color)  # High-low line
            ax.bar(df['Date'][idx], df['close'][idx] - df['open'][idx], width=0.02, bottom=min(df['open'][idx], df['close'][idx]), color=color)

        date_format = mpl_dates.DateFormatter('%d %b %Y')
        ax.xaxis.set_major_formatter(date_format)
        fig.autofmt_xdate()
        fig.tight_layout()
        
        # Plot support and resistance levels
        for level in levels:
            plt.hlines(level[1], xmin=df['Date'].min(), xmax=df['Date'].max(), colors='blue')
        plt.show()
    except Exception as error
    # Plot candlesticks manually
    for idx in range(len(df)):
        color = 'green' if df['close'][idx] >= df['open'][idx] else 'red'
        ax.plot([df['Date'][idx], df['Date'][idx]], [df['low'][idx], df['high'][idx]], color=color)  # High-low line
        ax.bar(df['Date'][idx], df['close'][idx] - df['open'][idx], width=0.02, bottom=min(df['open'][idx], df['close'][idx]), color=color)

    date_format = mpl_dates.DateFormatter('%d %b %Y')
    ax.xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()
    fig.tight_layout()
    
    # Plot support and resistance levels
    for level in levels:
        plt.hlines(level[1], xmin=df['Date'].min(), xmax=df['Date'].max(), colors='blue')
    plt.show()

# Trading strategy based on support/resistance detection
def trading_strategy(symbol, interval, leverage, usdt_amount, risk_percent=0.02, reward_risk_ratio=3):
    df = fetch_historical_data(symbol, interval)
    
    # Detect support and resistance levels
    levels = detect_key_levels(df)
    plot_levels(df, levels)  # Optional visualization
    
    entry_price = df['close'].iloc[-1]  # Last closing price
    
    # Check if price is near support or resistance
    for level in levels:
        level_price = level[1]
        if abs(entry_price - level_price) / level_price < risk_percent:
            if level_price < entry_price:
                # Near support, place long trade
                stop_loss = round(entry_price * (1 - risk_percent), 4)
                take_profit = round(entry_price * (1 + (risk_percent * reward_risk_ratio)), 4)
                place_order(symbol, "BUY", entry_price, stop_loss, take_profit, usdt_amount, leverage)
            elif level_price > entry_price:
                # Near resistance, place short trade
                stop_loss = round(entry_price * (1 + risk_percent), 4)
                take_profit = round(entry_price * (1 - (risk_percent * reward_risk_ratio)), 4)
                place_order(symbol, "SELL", entry_price, stop_loss, take_profit, usdt_amount, leverage)

# Place order with stop loss and take profit
def place_order(symbol, side, entry_price, stop_loss, take_profit, usdt_amount, leverage):
    # Calculate the quantity based on the specified amount of USDT to spend
    notional_value = usdt_amount * leverage
    quantity = round(notional_value / entry_price, 3)  # Adjust to 3 decimal places for precision
    
    try:
        client.change_leverage(symbol=symbol, leverage=leverage)
        order = client.new_order(symbol=symbol, side=side, type="MARKET", quantity=quantity)
        logging.info(f"Market {side} order placed: {order}")
        
        if side == "BUY":
            client.new_order(symbol=symbol, side="SELL", type="STOP_MARKET", stopPrice=stop_loss, quantity=quantity)
            client.new_order(symbol=symbol, side="SELL", type="TAKE_PROFIT_MARKET", stopPrice=take_profit, quantity=quantity)
        elif side == "SELL":
            client.new_order(symbol=symbol, side="BUY", type="STOP_MARKET", stopPrice=stop_loss, quantity=quantity)
            client.new_order(symbol=symbol, side="BUY", type="TAKE_PROFIT_MARKET", stopPrice=take_profit, quantity=quantity)

        print(f"Entry Price: {entry_price}, Stop Loss: {stop_loss}, Take Profit: {take_profit}")

    except ClientError as error:
        logging.error(f"Error placing {side} order: {error}")

# Example usage
symbol = "MANAUSDT"
interval = "15m"
usdt_amount = 1# Amount of USDT to spend on each trade
trading_strategy(symbol, interval, leverage=20, usdt_amount=usdt_amount)
