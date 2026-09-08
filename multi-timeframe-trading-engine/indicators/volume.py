"""
=========================================================
Professional Volume Indicator
=========================================================

Features
--------
✓ Average Volume
✓ Relative Volume (RVOL)
✓ Volume Trend
✓ Volume Expansion
✓ Volume Contraction
✓ High/Low Volume Detection
✓ Signal Object

Author: ChatGPT
=========================================================
"""
import pandas as pd
from indicators.signals import VolumeSignal


# =========================================================
# Validation
# =========================================================

def validate_dataframe(df):

    candidates = [
        "tick_volume",
        "volume",
        "real_volume"
    ]

    volume_column = None

    for col in candidates:

        if col in df.columns:

            volume_column = col
            break

    if volume_column is None:

        raise ValueError(
            "No volume column found."
        )

    return volume_column


# =========================================================
# Volume Series
# =========================================================

def volume_series(df):

    column = validate_dataframe(df)

    return df[column]


# =========================================================
# Current Volume
# =========================================================

def current_volume(df):

    return float(
        volume_series(df).iloc[-1]
    )


# =========================================================
# Average Volume
# =========================================================

def average_volume(

    df,

    period=20

):

    return float(

        volume_series(df)

        .rolling(period)

        .mean()

        .iloc[-1]

    )


# =========================================================
# Relative Volume
# =========================================================

def relative_volume(

    df,

    period=20

):

    avg = average_volume(

        df,

        period

    )

    if avg == 0:

        return 0

    return (

        current_volume(df)

        / avg

    )


# =========================================================
# Expansion
# =========================================================

def volume_expanding(

    df,

    period=20

):

    return relative_volume(

        df,

        period

    ) > 1.20


# =========================================================
# Contraction
# =========================================================

def volume_contracting(

    df,

    period=20

):

    return relative_volume(

        df,

        period

    ) < 0.80


# =========================================================
# High Volume
# =========================================================

def high_volume(

    df,

    period=20,

    multiplier=1.50

):

    return (

        current_volume(df)

        >=

        average_volume(df, period)

        * multiplier

    )


# =========================================================
# Low Volume
# =========================================================

def low_volume(

    df,

    period=20,

    multiplier=0.50

):

    return (

        current_volume(df)

        <=

        average_volume(df, period)

        * multiplier

    )


# =========================================================
# Trend
# =========================================================

def volume_trend(

    df,

    period=20

):

    rvol = relative_volume(

        df,

        period

    )

    if rvol >= 1.5:

        return "STRONG"

    if rvol >= 1.2:

        return "HIGH"

    if rvol >= 0.8:

        return "NORMAL"

    return "LOW"


# =========================================================
# Signal
# =========================================================

def volume_signal(

    df,

    period=20

):

    return VolumeSignal(

        valid=True,

        current=current_volume(df),

        average=average_volume(df, period),

        relative=relative_volume(df, period),

        trend=volume_trend(df, period),

        high_volume=high_volume(df, period),

        low_volume=low_volume(df, period),

        expanding=volume_expanding(df, period),

        contracting=volume_contracting(df, period),

    )


# =========================================================
# Add Column
# =========================================================

def add_volume_columns(

    df,

    period=20

):

    df = df.copy()

    column = validate_dataframe(df)

    df["average_volume"] = (

        df[column]

        .rolling(period)

        .mean()

    )

    df["relative_volume"] = (

        df[column]

        / df["average_volume"]

    )

    return df


# =========================================================
# Filter
# =========================================================

def volume_filter(

    df,

    minimum_relative=1.0

):

    signal = volume_signal(df)

    return (

        signal.relative

        >=

        minimum_relative

    )