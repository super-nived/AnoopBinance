from keys import iphone_api as api, iphone_secret as secret
from binance.um_futures import UMFutures
import pandas as pd
from time import sleep
from binance.error import ClientError

client = UMFutures(key=api, secret=secret)

# 0.012 means +1.2%, 0.009 is -0.9%
tp = 0.012
sl = 0.009
volume = 30  # volume for one order (if its 10 and leverage is 10, then you put 1 usdt to one position)
leverage = 10
type = 'ISOLATED'  # type is 'ISOLATED' or 'CROSS'
qty = 100  # Amount of concurrent opened positions

# Switch to Hedge mode (True means Hedge mode)
def set_hedge_mode():
    try:
        response = client.change_position_mode(dualSidePosition=True, recvWindow=6000)
        print("Position mode set to Hedge mode.")
        return response
    except ClientError as error:
        print(f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")

# Check current position mode (Hedge or One-way)
def check_position_mode():
    try:
        response = client.get_position_mode(recvWindow=6000)
        print("this is the check position mode result",response)
        return response['dualSidePosition']  # True = Hedge mode, False = One-way mode
    except ClientError as error:
        print(f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")

# Make sure we are in Hedge mode
if check_position_mode() is False:  # If in One-way mode
    set_hedge_mode()

# Getting your futures balance in USDT
def get_balance_usdt():
    try:
        response = client.balance(recvWindow=6000)
        for elem in response:
            if elem['asset'] == 'USDT':
                return float(elem['balance'])
    except ClientError as error:
        print(f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")

# Getting all available symbols on the Futures ('BTCUSDT', 'ETHUSDT', ....)
def get_tickers_usdt():
    tickers = []
    resp = client.ticker_price()
    for elem in resp:
        if 'USDT' in elem['symbol']:
            tickers.append(elem['symbol'])
    return tickers

# Getting candles for the needed symbol, it's a dataframe with 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'
def klines(symbol):
    try:
        resp = pd.DataFrame(client.klines(symbol, '15m'))
        resp = resp.iloc[:, :6]
        resp.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        resp = resp.set_index('Time')
        resp.index = pd.to_datetime(resp.index, unit='ms')
        resp = resp.astype(float)
        return resp
    except ClientError as error:
        print(f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")

# Set leverage for the needed symbol.
def set_leverage(symbol, level):
    try:
        response = client.change_leverage(symbol=symbol, leverage=level, recvWindow=6000)
        print("this is the set leverage responce",response)
    except ClientError as error:
        print(f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")

# Set margin type only if it's different
def set_mode(symbol, type):
    try:
        response = client.change_margin_type(symbol=symbol, marginType=type, recvWindow=6000)
        print(response)
    except ClientError as error:
        if error.error_code == -4046:  # No need to change margin type
            print(f"{symbol}: Margin type is already {type}, skipping change.")
        else:
            print(f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")

# Price precision
def get_price_precision(symbol):
    resp = client.exchange_info()['symbols']
    for elem in resp:
        if elem['symbol'] == symbol:
            return elem['pricePrecision']

# Amount precision
def get_qty_precision(symbol):
    resp = client.exchange_info()['symbols']
    for elem in resp:
        if elem['symbol'] == symbol:
            return elem['quantityPrecision']

# Open new order with the last price, and set TP and SL
def open_order(symbol, side):
    price = float(client.ticker_price(symbol)['price'])
    qty_precision = get_qty_precision(symbol)
    price_precision = get_price_precision(symbol)
    qty = round(volume / price, qty_precision)

    if side == 'buy':
        try:
            resp1 = client.new_order(symbol=symbol, side='BUY', type='LIMIT', quantity=qty, timeInForce='GTC', price=price)
            print(symbol, side, "placing order")
            print(resp1)
            sleep(2)
            # sl_price = round(price - price * sl, price_precision)
            # resp2 = client.new_order(symbol=symbol, side='SELL', type='STOP_MARKET', quantity=qty, timeInForce='GTC', stopPrice=sl_price)
            # print(resp2)
            # sleep(2)
            # tp_price = round(price + price * tp, price_precision)
            # resp3 = client.new_order(symbol=symbol, side='SELL', type='TAKE_PROFIT_MARKET', quantity=qty, timeInForce='GTC', stopPrice=tp_price)
            # print(resp3)
        except ClientError as error:
            print(f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")

    if side == 'sell':
        try:
            resp1 = client.new_order(symbol=symbol, side='SELL', type='LIMIT', quantity=qty, timeInForce='GTC', price=price)
            print(symbol, side, "placing order")
            print(resp1)
            sleep(2)
            # sl_price = round(price + price * sl, price_precision)
            # resp2 = client.new_order(symbol=symbol, side='BUY', type='STOP_MARKET', quantity=qty, timeInForce='GTC', stopPrice=sl_price)
            # print(resp2)
            # sleep(2)
            # tp_price = round(price - price * tp, price_precision)
            # resp3 = client.new_order(symbol=symbol, side='BUY', type='TAKE_PROFIT_MARKET', quantity=qty, timeInForce='GTC', stopPrice=tp_price)
            # print(resp3)
        except ClientError as error:
            print(f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")

# Your current positions (returns the symbols list)
def get_pos():
    try:
        resp = client.get_position_risk()
        pos = []
        for elem in resp:
            if float(elem['positionAmt']) != 0:
                pos.append(elem['symbol'])
        return pos
    except ClientError as error:
        print(f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")

# Checking open orders
def check_orders():
    try:
        response = client.get_orders(recvWindow=6000)
        sym = []
        for elem in response:
            sym.append(elem['symbol'])
        return sym
    except ClientError as error:
        print(f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")

# Close open orders for the needed symbol
def close_open_orders(symbol):
    try:
        response = client.cancel_open_orders(symbol=symbol, recvWindow=6000)
        print(response)
    except ClientError as error:
        print(f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")

# Support and Resistance calculation (20-period rolling high/low)
def support_resistance_levels(symbol):
    kl = klines(symbol)
    
    # Using rolling windows to find recent highs and lows (support and resistance)
    kl['Low_Roll'] = kl['Low'].rolling(window=20).min()  # Support (20-period low)
    kl['High_Roll'] = kl['High'].rolling(window=20).max()  # Resistance (20-period high)
    
    # Most recent support and resistance levels
    support = kl['Low_Roll'].iloc[-1]
    resistance = kl['High_Roll'].iloc[-1]
    
    return support, resistance

# Updated signal function based on support and resistance
def sr_signal(symbol):
    kl = klines(symbol)
    price = kl['Close'].iloc[-1]  # Current price

    # Get the support and resistance levels
    support, resistance = support_resistance_levels(symbol)
    
    # Place buy signal if price is near support (within a small margin)
    if price <= support * 1.01:  # 1% above support
        return 'up'
    
    # Place sell signal if price is near resistance (within a small margin)
    elif price >= resistance * 0.99:  # 1% below resistance
        return 'down'
    
    return 'none'

# Main strategy loop
orders = 0
symbol = ''
# getting all symbols from Binance Futures list:
symbols = get_tickers_usdt()

while True:
    balance = get_balance_usdt()
    sleep(1)
    if balance == None:
        print('Cant connect to API. Check IP, restrictions or wait some time')
    if balance != None:
        print("My balance is: ", balance, " USDT")
        pos = get_pos()
        print(f'You have {len(pos)} opened positions:\n{pos}')
        ord = check_orders()

        # removing stop orders for closed positions
        for elem in ord:
            if not elem in pos:
                close_open_orders(elem)

        if len(pos) < qty:
            for elem in symbols:
                # Updated strategy: support and resistance signals
                signal = sr_signal(elem)

                # 'up' or 'down' signal, we place orders for symbols that arent in the opened positions and orders
                if signal == 'up' and elem != 'USDCUSDT' and not elem in pos and not elem in ord and elem != symbol:
                    print('Found BUY signal for ', elem)
                    set_mode(elem, type)
                    sleep(2)
                    set_leverage(elem, leverage)
                    open_order(elem, 'buy')

                if signal == 'down' and elem != 'USDCUSDT' and not elem in pos and not elem in ord and elem != symbol:
                    print('Found SELL signal for ', elem)
                    set_mode(elem, type)
                    sleep(2)
                    set_leverage(elem, leverage)
                    open_order(elem, 'sell')
