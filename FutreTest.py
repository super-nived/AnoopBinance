import logging
from binance.um_futures import UMFutures
from binance.lib.utils import config_logging
from binance.error import ClientError
import json

# Load API keys from config.json
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
margin_usdt = 2  # This is your margin (2 USDT)
risk_percent = 0.02  # Risk percentage for stop loss (2%)
reward_risk_ratio = 3  # 3:1 profit-to-loss ratio

def place_order(side):
    try:
        # Set leverage to 20x for the trading pair
        client.change_leverage(symbol=symbol, leverage=leverage)
        logging.info(f"Leverage set to {leverage}x for {symbol}")

        # Fetch the current price of MANAUSDT
        ticker = client.ticker_price(symbol=symbol)
        entry_price = float(ticker['price'])

        # Get the allowed quantity precision for MANAUSDT
        exchange_info = client.exchange_info()
        for symbol_info in exchange_info['symbols']:
            if symbol_info['symbol'] == symbol:
                quantity_precision = symbol_info['quantityPrecision']

        # Calculate the notional value (leveraged position) you want to control
        notional_value = margin_usdt * leverage  # With 20x leverage, 2 USDT becomes 40 USDT
        quantity = round(notional_value / entry_price, quantity_precision)  # Use the correct precision

        # Calculate stop loss and take profit based on the trade side
        if side.upper() == "BUY":
            stop_loss = round(entry_price * (1 - risk_percent), 4)
            take_profit = round(entry_price * (1 + (risk_percent * reward_risk_ratio)), 4)
        elif side.upper() == "SELL":
            stop_loss = round(entry_price * (1 + risk_percent), 4)
            take_profit = round(entry_price * (1 - (risk_percent * reward_risk_ratio)), 4)
        else:
            raise ValueError("Invalid side. Choose 'BUY' or 'SELL'.")

        # Place the market order
        order = client.new_order(
            symbol=symbol,
            side=side.upper(),
            type="MARKET",
            quantity=quantity
        )
        logging.info(f"Market {side} order placed: {order}")

        # Place Stop Loss and Take Profit orders
        if side.upper() == "BUY":
            # Stop loss for a long position
            stop_loss_order = client.new_order(
                symbol=symbol,
                side="SELL",  # To exit the long position, you need to sell
                type="STOP_MARKET",
                stopPrice=stop_loss,
                quantity=quantity
            )
            # Take profit for a long position
            take_profit_order = client.new_order(
                symbol=symbol,
                side="SELL",  # To exit the long position, you need to sell
                type="TAKE_PROFIT_MARKET",
                stopPrice=take_profit,
                quantity=quantity
            )
        elif side.upper() == "SELL":
            # Stop loss for a short position
            stop_loss_order = client.new_order(
                symbol=symbol,
                side="BUY",  # To exit the short position, you need to buy
                type="STOP_MARKET",
                stopPrice=stop_loss,
                quantity=quantity
            )
            # Take profit for a short position
            take_profit_order = client.new_order(
                symbol=symbol,
                side="BUY",  # To exit the short position, you need to buy
                type="TAKE_PROFIT_MARKET",
                stopPrice=take_profit,
                quantity=quantity
            )

        logging.info(f"Stop Loss order placed at {stop_loss}: {stop_loss_order}")
        logging.info(f"Take Profit order placed at {take_profit}: {take_profit_order}")

        # Print out the trade details
        print(f"Entry Price: {entry_price}")
        print(f"Stop Loss: {stop_loss}, Take Profit: {take_profit}")

    except ClientError as error:
        logging.error(f"Error placing {side} order: {error}")

# Test the buy order
place_order("SELL")  # Pass "BUY" for a long position or "SELL" for a short position
