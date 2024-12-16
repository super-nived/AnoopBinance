import ccxt
import os

# Initialize Binance API
api_key = ''
api_secret = ''

binance = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,  # Enables rate limiting
    'options': {
        'defaultType': 'future',  # Set to future for futures trading
    },
    # Use testnet if you're testing futures trades. Set this to False for live trades.
    'test': True
})

# Function to set leverage on a futures pair
def set_leverage(symbol, leverage):
    try:
        response = binance.fapiPrivate_post_leverage({
            'symbol': symbol.replace('/', ''),  # Binance Futures expects no slashes in symbols
            'leverage': leverage
        })
        return response
    except Exception as e:
        raise Exception(f"Failed to set leverage for {symbol}: {str(e)}")

# Function to get the current price of a futures symbol (e.g., MANA/USDT)
def get_current_price(symbol):
    try:
        ticker = binance.fetch_ticker(symbol)
        return ticker['last']  # Return the last traded price
    except Exception as e:
        raise Exception(f"Failed to fetch current price for {symbol}: {str(e)}")

# Function to fetch the minimum notional value for a futures trading pair (e.g., MANA/USDT)
def get_minimum_notional(symbol):
    try:
        # Load market details for the specific symbol
        markets = binance.load_markets()
        market_info = markets[symbol]
        return float(market_info['limits']['cost']['min'])  # Minimum notional value in USDT
    except Exception as e:
        raise Exception(f"Failed to fetch market data for {symbol}: {str(e)}")

# Function to place a leveraged buy order
def place_leveraged_buy(symbol='MANA/USDT', usdt_amount=6, leverage=5):
    try:
        # Set the leverage for the symbol
        set_leverage(symbol, leverage)

        # Fetch the current price of the futures pair
        current_price = get_current_price(symbol)
        
        # Calculate the amount of MANA to buy for the given USDT amount
        mana_amount = usdt_amount / current_price
        
        # Fetch the minimum notional value for the symbol
        minimum_notional = get_minimum_notional(symbol)
        
        # Check if the order meets the minimum notional value
        if usdt_amount >= minimum_notional:
            # Place a leveraged market buy order for the calculated amount of MANA
            order = binance.create_market_buy_order(symbol, mana_amount)
            return order  # Return order details if successful
        else:
            return f"Order value {usdt_amount} USDT is below the minimum notional value of {minimum_notional} USDT."
    
    except Exception as e:
        raise Exception(f"Failed to place leveraged buy order: {str(e)}")

# Example usage
if __name__ == '__main__':
    try:
        # Attempt to place a leveraged buy order with 5x leverage
        order = place_leveraged_buy(symbol='MANA/USDT', usdt_amount=6, leverage=5)
        print(f"Leveraged order placed: {order}")
    except Exception as e:
        print(f"An error occurred: {e}")
