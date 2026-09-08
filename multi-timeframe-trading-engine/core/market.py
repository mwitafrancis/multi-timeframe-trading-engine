"""
=========================================================
Professional Market Data
=========================================================

Downloads market data from MT5.

Responsible ONLY for retrieving prices.

Author: francis
=========================================================
"""

from datetime import datetime

import MetaTrader5 as mt5
import pandas as pd


# =========================================================
# Download OHLC
# =========================================================

def get_rates(symbol, timeframe, bars=500):
    """
    Returns a pandas DataFrame containing OHLC data.
    """

    rates = mt5.copy_rates_from_pos(
        symbol,
        timeframe,
        1,
        bars,
    )

    if rates is None:
        return pd.DataFrame()

    df = pd.DataFrame(rates)

    if df.empty:
        return df

    df["time"] = pd.to_datetime(
        df["time"],
        unit="s",
    )

    return df


# =========================================================
# Latest Candle
# =========================================================

def get_last_candle(symbol, timeframe):

    df = get_rates(symbol, timeframe, 1)

    if df.empty:
        return None

    return df.iloc[-1]


# =========================================================
# Current Tick
# =========================================================

def get_tick(symbol):

    return mt5.symbol_info_tick(symbol)


# =========================================================
# Bid
# =========================================================

def get_bid(symbol):

    tick = get_tick(symbol)

    if tick is None:
        return None

    return tick.bid


# =========================================================
# Ask
# =========================================================

def get_ask(symbol):

    tick = get_tick(symbol)

    if tick is None:
        return None

    return tick.ask


# =========================================================
# Current Price
# =========================================================

def get_price(symbol):

    tick = get_tick(symbol)

    if tick is None:
        return None

    return (tick.bid + tick.ask) / 2


# =========================================================
# Spread (points)
# =========================================================

def get_spread(symbol):

    tick = get_tick(symbol)

    info = mt5.symbol_info(symbol)

    if tick is None or info is None:
        return None

    return (tick.ask - tick.bid) / info.point


# =========================================================
# Symbol Information
# =========================================================

def get_symbol_info(symbol):

    return mt5.symbol_info(symbol)


# =========================================================
# Symbol Exists
# =========================================================

def symbol_exists(symbol):

    info = mt5.symbol_info(symbol)

    return info is not None


# =========================================================
# Ensure Symbol Selected
# =========================================================

def select_symbol(symbol):

    if not mt5.symbol_select(symbol, True):
        raise RuntimeError(
            f"Unable to select symbol: {symbol}"
        )

    return True


# =========================================================
# Market Open
# =========================================================

def market_open(symbol):

    tick = get_tick(symbol)

    return tick is not None


# =========================================================
# Server Time
# =========================================================

def server_time():

    return datetime.now()