"""
=========================================================
Professional ATR Indicator
=========================================================

Features

✓ ATR Calculation

✓ ATR Percentage

✓ Volatility Classification

✓ ATR Expansion

✓ ATR Contraction

✓ Suggested Stop Multiplier

Author : ChatGPT
=========================================================
"""

import numpy as np
import pandas as pd
from indicators.signals import ATRSignal




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

    if len(df) < 20:

        raise ValueError(

            "ATR requires at least 20 candles."

        )


# =========================================================
# True Range
# =========================================================

def true_range(df):

    previous_close = df["close"].shift(1)

    tr = pd.concat(

        [

            df["high"] - df["low"],

            (df["high"] - previous_close).abs(),

            (df["low"] - previous_close).abs(),

        ],

        axis=1

    ).max(axis=1)

    return tr


# =========================================================
# ATR Series
# =========================================================

def atr_series(

    df,

    period=14

):

    validate_dataframe(df)

    tr = true_range(df)

    return tr.ewm(alpha=1/period, adjust=False).mean()


# =========================================================
# ATR Value
# =========================================================

def atr_value(

    df,

    period=14

):

    return float(

        atr_series(

            df,

            period

        ).iloc[-1]

    )


# =========================================================
# ATR Percentage
# =========================================================

def atr_percent(

    df,

    period=14

):

    atr = atr_value(

        df,

        period

    )

    close = float(

        df["close"].iloc[-1]

    )

    if close == 0:

        return 0.0

    return (

        atr / close

    ) * 100


# =========================================================
# Expansion
# =========================================================

def atr_expanding(

    df,

    period=14,

    lookback=5

):

    values = atr_series(

        df,

        period

    )

    return (

        values.iloc[-1]

        >

        values.iloc[-lookback]

    )


# =========================================================
# Contraction
# =========================================================

def atr_contracting(

    df,

    period=14,

    lookback=5

):

    values = atr_series(

        df,

        period

    )

    return (

        values.iloc[-1]

        <

        values.iloc[-lookback]

    )


# =========================================================
# Volatility Classification
# =========================================================

def volatility_class(

    percent

):

    if percent >= 3:

        return "EXTREME"

    if percent >= 2:

        return "HIGH"

    if percent >= 1:

        return "MEDIUM"

    return "LOW"


# =========================================================
# Suggested Stop
# =========================================================

def stop_multiplier(

    volatility

):

    table = {

        "LOW":1.0,

        "MEDIUM":1.5,

        "HIGH":2.0,

        "EXTREME":2.5

    }

    return table.get(

        volatility,

        1.5

    )


# =========================================================
# Main Signal
# =========================================================

def atr_signal(

    df,

    period=14

):

    validate_dataframe(df)

    atr = atr_value(

        df,

        period

    )

    percent = atr_percent(

        df,

        period

    )

    volatility = volatility_class(

        percent

    )

    expanding = atr_expanding(

        df,

        period

    )

    contracting = atr_contracting(

        df,

        period

    )

    return ATRSignal(

        valid=True,

        atr=atr,

        atr_percent=percent,

        volatility=volatility,

        expanding=expanding,

        contracting=contracting,

        stop_multiplier=stop_multiplier(

            volatility

        )

    )


# =========================================================
# Add ATR Column
# =========================================================

def add_atr_column(

    df,

    period=14

):

    df = df.copy()

    df[f"atr_{period}"] = atr_series(

        df,

        period

    )

    return df


# =========================================================
# Volatility Filter
# =========================================================

def volatility_filter(

    df,

    minimum_percent=1.0

):

    signal = atr_signal(df)

    return (

        signal.atr_percent

        >=

        minimum_percent

    )