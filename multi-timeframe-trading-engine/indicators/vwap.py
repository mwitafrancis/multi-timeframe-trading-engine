"""
=========================================================
Professional VWAP Indicator
=========================================================

Features

✓ VWAP

✓ Premium

✓ Discount

✓ Distance

✓ Cross Detection

✓ Trend Confirmation

Author : ChatGPT
=========================================================
"""

import numpy as np
import pandas as pd

from config import *

from indicators.signals import VWAPSignal
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

            raise ValueError(

                f"Missing column: {col}"

            )

    if (

        "tick_volume" not in df.columns

        and

        "volume" not in df.columns

        and

        "real_volume" not in df.columns

    ):

        raise ValueError(

            "No volume column found."

        )
# =========================================================
# Volume Column
# =========================================================

def volume_column(df):

    if "tick_volume" in df.columns:

        return "tick_volume"

    if "volume" in df.columns:

        return "volume"

    return "real_volume"
# =========================================================
# Typical Price
# =========================================================

def typical_price(df):

    return (

        df["high"]

        +

        df["low"]

        +

        df["close"]

    ) / 3
# =========================================================
# VWAP Series
# =========================================================

# =========================================================
# Session VWAP
# =========================================================

def vwap_series(df):

    validate_dataframe(df)

    df = df.copy()

    volume = df[volume_column(df)]

    tp = typical_price(df)

    # -----------------------------------------
    # Daily VWAP
    # -----------------------------------------

    if VWAP_SESSION == "daily":

        session = pd.to_datetime(df["time"]).dt.date

    # -----------------------------------------
    # Weekly VWAP
    # -----------------------------------------

    elif VWAP_SESSION == "weekly":

        session = pd.to_datetime(df["time"]).dt.to_period("W")

    else:

        raise ValueError("Unsupported VWAP_SESSION")

    df["session"] = session

    df["tpv"] = tp * volume

    df["cum_tpv"] = df.groupby("session")["tpv"].cumsum()

    df["cum_volume"] = df.groupby("session")[volume.name].cumsum()

    df["vwap"] = df["cum_tpv"] / df["cum_volume"]

    return df["vwap"]
# =========================================================
# VWAP Value
# =========================================================

def vwap_value(df):

    return float(

        vwap_series(df)

        .iloc[-1]

    )
# =========================================================
# Distance
# =========================================================

def distance_from_vwap(df):

    close = float(

        df.close.iloc[-1]

    )

    return close - vwap_value(df)
# =========================================================
# Above VWAP
# =========================================================

def above_vwap(df):

    return (

        distance_from_vwap(df)

        > 0

    )
# =========================================================
# Below VWAP
# =========================================================

def below_vwap(df):

    return (

        distance_from_vwap(df)

        < 0

    )
# =========================================================
# Premium
# =========================================================

def premium(df):

    price = float(df.close.iloc[-1])

    vwap = vwap_value(df)

    premium_percent = (price - vwap) / vwap

    return premium_percent >= PREMIUM_THRESHOLD
# =========================================================
# Discount
# =========================================================

def discount(df):

    price = float(df.close.iloc[-1])

    vwap = vwap_value(df)

    discount_percent = (price - vwap) / vwap

    return discount_percent <= DISCOUNT_THRESHOLD
# =========================================================
# Fair Value
# =========================================================

def fair_value(df):

    return not premium(df) and not discount(df)
# =========================================================
# Cross Above VWAP
# =========================================================

def crossed_above(df):

    series = vwap_series(df)

    previous_close = float(df.close.iloc[-2])

    current_close = float(df.close.iloc[-1])

    previous_vwap = float(series.iloc[-2])

    current_vwap = float(series.iloc[-1])

    return (

        previous_close <= previous_vwap

        and

        current_close > current_vwap

    )
# =========================================================
# Cross Below VWAP
# =========================================================

def crossed_below(df):

    series = vwap_series(df)

    previous_close = float(df.close.iloc[-2])

    current_close = float(df.close.iloc[-1])

    previous_vwap = float(series.iloc[-2])

    current_vwap = float(series.iloc[-1])

    return (

        previous_close >= previous_vwap

        and

        current_close < current_vwap

    )
# =========================================================
# Trend Confirmation
# =========================================================

def trend_confirmation(df):

    if above_vwap(df):

        return "BULLISH"

    if below_vwap(df):

        return "BEARISH"

    return "NEUTRAL"
# =========================================================
# VWAP Signal
# =========================================================

def vwap_signal(df):

    value = vwap_value(df)

    return VWAPSignal(

        valid=True,

        vwap=value,

        price_above=above_vwap(df),

        price_below=below_vwap(df),

        distance=distance_from_vwap(df),

        premium=premium(df),

        discount=discount(df),

        fair_value=fair_value(df),

        crossed_above=crossed_above(df),

        crossed_below=crossed_below(df),

        trend_confirmation=trend_confirmation(df),

    )
# =========================================================
# Premium Filter
# =========================================================

def premium_filter(df):

    return premium(df)


# =========================================================
# Discount Filter
# =========================================================

def discount_filter(df):

    return discount(df)


# =========================================================
# Above VWAP Filter
# =========================================================

def bullish_filter(df):

    return above_vwap(df)


# =========================================================
# Below VWAP Filter
# =========================================================

def bearish_filter(df):

    return below_vwap(df)
# =========================================================
# Add VWAP Column
# =========================================================

def add_vwap_column(df):

    df = df.copy()

    df["vwap"] = vwap_series(df)

    return df