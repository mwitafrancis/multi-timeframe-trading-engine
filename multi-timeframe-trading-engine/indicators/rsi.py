"""
=========================================================
Professional RSI Indicator
=========================================================

Features
--------
✓ Wilder RSI
✓ Momentum Detection
✓ Overbought / Oversold
✓ Bullish / Bearish Momentum
✓ Signal Object

Author: ChatGPT
=========================================================
"""

import pandas as pd
import numpy as np

from indicators.signals import RSISignal
from config import (
    RSI_PERIOD,
    RSI_OVERBOUGHT,
    RSI_OVERSOLD,
    BULLISH_RSI,
    BEARISH_RSI,
)


# =========================================================
# Validation
# =========================================================

def validate_dataframe(df):

    if "close" not in df.columns:
        raise ValueError("Missing close column.")

    if len(df) < 30:
        raise ValueError("RSI requires at least 30 candles.")
# =========================================================
# Wilder RMA
# =========================================================

def rma(series, period):

    return series.ewm(

        alpha=1 / period,

        adjust=False

    ).mean()

# =========================================================
# RSI Series
# =========================================================

def rsi_series(

    df,

    period=RSI_PERIOD

):

    validate_dataframe(df)

    delta = df["close"].diff()

    gain = delta.clip(lower=0)

    loss = (-delta).clip(lower=0)

    avg_gain = rma(gain, period)

    avg_loss = rma(loss, period)

    rs = avg_gain / avg_loss.replace(0, np.nan)

    rsi = 100 - (100 / (1 + rs))

    return rsi.fillna(50)

# =========================================================
# Current RSI
# =========================================================

def rsi_value(

    df,

    period=RSI_PERIOD

):

    return float(

        rsi_series(

            df,

            period

        ).iloc[-1]

    )
# =========================================================
# Overbought
# =========================================================

def overbought(

    df,

    period=RSI_PERIOD,

    level=RSI_OVERBOUGHT

):

    return (

        rsi_value(

            df,

            period

        )

        >=

        level

    )
# =========================================================
# Oversold
# =========================================================

def oversold(

    df,

    period=RSI_PERIOD,

    level=RSI_OVERSOLD

):

    return (

        rsi_value(

            df,

            period

        )

        <=

        level

    )
# =========================================================
# Momentum
# =========================================================
def momentum(
    df,
    period=RSI_PERIOD
):

    value = rsi_value(df, period)

    if value >= BULLISH_RSI:
        return "BULLISH"

    if value <= BEARISH_RSI:
        return "BEARISH"

    return "NEUTRAL"
# =========================================================
# Bullish Momentum
# =========================================================

def bullish_momentum(df):

    return momentum(df) == "BULLISH"


# =========================================================
# Bearish Momentum
# =========================================================

def bearish_momentum(df):

    return momentum(df) == "BEARISH"
# =========================================================
# RSI Rising
# =========================================================

def rising_rsi(

    df,

    period=RSI_PERIOD,

    lookback=3

):

    series = rsi_series(df, period)

    return series.iloc[-1] > series.iloc[-lookback]


# =========================================================
# RSI Falling
# =========================================================

def falling_rsi(

    df,

    period=RSI_PERIOD,

    lookback=3

):

    series = rsi_series(df, period)

    return series.iloc[-1] < series.iloc[-lookback]
# =========================================================
# Momentum Strength
# =========================================================

def momentum_strength(

    df,

    period=RSI_PERIOD

):

    value = rsi_value(df, period)

    if value >= 80:

        return "EXTREME_BULLISH"

    if value >= 70:

        return "VERY_BULLISH"

    if value >= BULLISH_RSI:

        return "BULLISH"

    if value <= 20:

        return "EXTREME_BEARISH"

    if value <= 30:

        return "VERY_BEARISH"

    if value <= BEARISH_RSI:

        return "BEARISH"

    return "NEUTRAL"
# =========================================================
# RSI Signal
# =========================================================

def rsi_signal(

    df,

    period=RSI_PERIOD

):

    value = rsi_value(df, period)

    return RSISignal(

        valid=True,

        rsi=value,

        overbought=overbought(df, period),

        oversold=oversold(df, period),

        bullish=bullish_momentum(df),

        bearish=bearish_momentum(df),

        momentum=momentum_strength(df)

    )
# =========================================================
# Bullish Filter
# =========================================================

def bullish_filter(df):

    return rsi_signal(df).bullish


# =========================================================
# Bearish Filter
# =========================================================

def bearish_filter(df):

    return rsi_signal(df).bearish


# =========================================================
# Overbought Filter
# =========================================================

def overbought_filter(df):

    return rsi_signal(df).overbought


# =========================================================
# Oversold Filter
# =========================================================

def oversold_filter(df):

    return rsi_signal(df).oversold
# =========================================================
# Add RSI Column
# =========================================================

def add_rsi_column(

    df,

    period=RSI_PERIOD

):

    df = df.copy()

    df[f"rsi_{period}"] = rsi_series(

        df,

        period

    )

    return df
