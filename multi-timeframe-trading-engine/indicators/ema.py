"""
=========================================================
Professional EMA Indicator
=========================================================

Features
--------
✓ EMA calculation
✓ Multiple EMA calculation
✓ EMA crossover detection
✓ EMA slope
✓ Trend detection
✓ Trend strength
✓ Signal object

Author: ChatGPT
=========================================================
"""

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
from indicators.signals import EMASignal


# =========================================================
# Validation
# =========================================================

def validate_dataframe(df: pd.DataFrame):

    required = ["close"]

    for col in required:

        if col not in df.columns:

            raise ValueError(f"Missing column: {col}")

    if len(df) < 200:

        raise ValueError(
            "EMA module requires at least 200 candles."
        )


# =========================================================
# EMA
# =========================================================

def ema(series: pd.Series, period: int):

    return series.ewm(
        span=period,
        adjust=False
    ).mean()


# =========================================================
# Last EMA Value
# =========================================================

def ema_value(
    df: pd.DataFrame,
    period: int
):

    validate_dataframe(df)

    return float(
        ema(df["close"], period).iloc[-1]
    )


# =========================================================
# EMA Series
# =========================================================

def ema_series(
    df: pd.DataFrame,
    period: int
):

    validate_dataframe(df)

    return ema(df["close"], period)


# =========================================================
# EMA Slope
# =========================================================

def ema_slope(
    df: pd.DataFrame,
    period: int,
    lookback: int = 5
):

    values = ema_series(df, period)

    current = values.iloc[-1]

    previous = values.iloc[-lookback]

    return float(current - previous)


# =========================================================
# Crossovers
# =========================================================

def bullish_cross(
    fast: float,
    slow: float
):

    return fast > slow


def bearish_cross(
    fast: float,
    slow: float
):

    return fast < slow


# =========================================================
# Trend Strength
# =========================================================

def trend_strength(

    ema_fast,

    ema_medium,

    ema_slow

):

    distance1 = abs(ema_fast - ema_medium)

    distance2 = abs(ema_medium - ema_slow)

    return round(distance1 + distance2, 6)


# =========================================================
# Alignment
# =========================================================

def is_bullish_alignment(

    ema_fast,

    ema_medium,

    ema_slow

):

    return (

        ema_fast >

        ema_medium >

        ema_slow

    )


def is_bearish_alignment(

    ema_fast,

    ema_medium,

    ema_slow

):

    return (

        ema_fast <

        ema_medium <

        ema_slow

    )


# =========================================================
# Main Signal
# =========================================================

def ema_signal(

    df: pd.DataFrame,

    fast: int = 20,

    medium: int = 50,

    slow: int = 200,

):

    validate_dataframe(df)

    ema_fast = ema_value(df, fast)

    ema_medium = ema_value(df, medium)

    ema_slow = ema_value(df, slow)

    slope_fast = ema_slope(df, fast)

    slope_medium = ema_slope(df, medium)

    slope_slow = ema_slope(df, slow)

    bullish = is_bullish_alignment(

        ema_fast,

        ema_medium,

        ema_slow

    )

    bearish = is_bearish_alignment(

        ema_fast,

        ema_medium,

        ema_slow

    )

    if bullish:

        trend = "BULLISH"

    elif bearish:

        trend = "BEARISH"

    else:

        trend = "SIDEWAYS"

    strength = trend_strength(

        ema_fast,

        ema_medium,

        ema_slow

    )

    return EMASignal(

        bullish=bullish,

        bearish=bearish,

        trend=trend,

        strength=strength,

        ema_fast=ema_fast,

        ema_medium=ema_medium,

        ema_slow=ema_slow,

        slope_fast=slope_fast,

        slope_medium=slope_medium,

        slope_slow=slope_slow,

    )


# =========================================================
# Add EMA Columns
# =========================================================

def add_ema_columns(

    df: pd.DataFrame,

    periods=(20, 50, 200)

):

    df = df.copy()

    for period in periods:

        df[f"ema_{period}"] = ema(

            df["close"],

            period

        )

    return df


# =========================================================
# Trend Filter
# =========================================================

def trend_filter(

    df,

    direction,

    fast=20,

    medium=50,

    slow=200

):

    signal = ema_signal(

        df,

        fast,

        medium,

        slow

    )

    if direction == "BUY":

        return signal.bullish

    if direction == "SELL":

        return signal.bearish

    return False