"""
=========================================================
Professional ADX Indicator
=========================================================

Features
--------
✓ +DI
✓ -DI
✓ ADX
✓ Trend Strength
✓ Bullish Confirmation
✓ Bearish Confirmation
✓ Trend Expansion
✓ Signal Object

Author: ChatGPT
=========================================================
"""

import pandas as pd
import numpy as np

from indicators.signals import ADXSignal


# =========================================================
# Validation
# =========================================================

def validate_dataframe(df):

    required = [

        "high",

        "low",

        "close"

    ]

    for col in required:

        if col not in df.columns:

            raise ValueError(f"Missing column: {col}")

    if len(df) < 50:

        raise ValueError("ADX requires at least 50 candles.")
    
# =========================================================
# True Range
# =========================================================

def true_range(df):

    previous_close = df["close"].shift(1)

    tr = pd.concat([

        df["high"] - df["low"],

        (df["high"] - previous_close).abs(),

        (df["low"] - previous_close).abs()

    ], axis=1).max(axis=1)

    return tr
# =========================================================
# Directional Movement
# =========================================================

def directional_movement(df):

    up_move = df["high"].diff()

    down_move = -df["low"].diff()

    plus_dm = np.where(

        (up_move > down_move) & (up_move > 0),

        up_move,

        0.0

    )

    minus_dm = np.where(

        (down_move > up_move) & (down_move > 0),

        down_move,

        0.0

    )

    return (

        pd.Series(plus_dm, index=df.index),

        pd.Series(minus_dm, index=df.index)

    )
# =========================================================
# Wilder RMA
# =========================================================

def rma(series, period):

    return series.ewm(

        alpha=1/period,

        adjust=False

    ).mean()
# =========================================================
# ATR
# =========================================================

def atr(df, period=14):

    tr = true_range(df)

    return rma(tr, period)
# =========================================================
# +DI / -DI
# =========================================================

def directional_indicators(

    df,

    period=14

):

    plus_dm, minus_dm = directional_movement(df)

    atr_values = atr(df, period)

    plus_di = (

        100 *

        rma(plus_dm, period)

        /

        atr_values

    )

    minus_di = (

        100 *

        rma(minus_dm, period)

        /

        atr_values

    )

    return (

        plus_di,

        minus_di

    )
# =========================================================
# DX
# =========================================================

def dx(df, period=14):

    plus_di, minus_di = directional_indicators(

        df,

        period

    )

    return (

        (

            plus_di -

            minus_di

        ).abs()

        /

        (

            plus_di +

            minus_di

        )

    ) * 100
# =========================================================
# ADX Series
# =========================================================

def adx_series(

    df,

    period=14

):

    validate_dataframe(df)

    return rma(

        dx(df, period),

        period

    )
# =========================================================
# ADX Value
# =========================================================

def adx_value(df, period=14):
    return float(adx_series(df, period).iloc[-1])

# =========================================================
# ADX Momentum
# =========================================================

def adx_momentum(df, period=14, lookback=5):

    series = adx_series(df, period)

    if len(series) <= lookback:
        return 0.0

    return float(
        series.iloc[-1] -
        series.iloc[-lookback]
    )
# =========================================================
# DI Separation
# =========================================================

def di_gap(

    plus_di,

    minus_di,

):

    return abs(

        plus_di -

        minus_di

    )
# =========================================================
# Trend Expansion
# =========================================================

def trend_expanding(

    adx,

    momentum,

    gap,

):

    return (

        adx >= 20

        and

        momentum > 1.0

        and

        gap >= 10

    )
# =========================================================
# Trend Exhaustion
# =========================================================

def trend_exhausted(

    adx,

    momentum,

):

    return (

        adx >= 35

        and

        momentum < -1

    )


# =========================================================
# ADX Signal
# =========================================================

def adx_signal(df, period=14):
    
    validate_dataframe(df)

    plus_di_series, minus_di_series = directional_indicators(df, period)
    adx_values = adx_series(df, period)

    plus_di = float(plus_di_series.iloc[-1])
    minus_di = float(minus_di_series.iloc[-1])
    adx = float(adx_values.iloc[-1])
    momentum = adx_momentum(

        df,

        period,

    )

    gap = di_gap(

        plus_di,

        minus_di,

    )

    expanding = trend_expanding(

        adx,

        momentum,

        gap,

    )

    exhausted = trend_exhausted(

        adx,

        momentum,

    )

    strong_trend = (

        adx >= 25

        and

        expanding

    )

    weak_trend = adx < 20

    bullish = plus_di > minus_di
    bearish = minus_di > plus_di

    return ADXSignal(
        valid=True,
        adx=adx,
        plus_di=plus_di,
        minus_di=minus_di,
        strong_trend=strong_trend,
        weak_trend=weak_trend,
        bullish=bullish,
        bearish=bearish,
        momentum=momentum,

        gap=gap,

        expanding=expanding,

        exhausted=exhausted,
    )
# =========================================================
# ADX Trend Classification
# =========================================================

def adx_trend_classification(adx):
    
    if adx < 20:
        return "RANGE"
    if adx < 25:
        return "WEAK_TREND"
    if adx < 40:
        return "STRONG_TREND"
    return "VERY_STRONG_TREND"
# =========================================================
# Directional Confirmation
# =========================================================

def bullish_adx(df, period=14):
    signal = adx_signal(df, period)
    return signal.strong_trend and signal.bullish


def bearish_adx(df, period=14):
    signal = adx_signal(df, period)
    return signal.strong_trend and signal.bearish


def adx_filter(df, minimum_adx=20, period=14):
    signal = adx_signal(df, period)
    return signal.adx >= minimum_adx