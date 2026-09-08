"""
=========================================================
Professional Trend Engine
=========================================================

Determines market trend using

✓ Market Structure
✓ EMA Alignment
✓ Pullbacks
✓ Trend Continuation
✓ Trend Strength
✓ Market Phase

Author: ChatGPT
=========================================================
"""

from typing import Tuple
import pandas as pd

from indicators.signals import TrendSignal

from indicators.ema import (
    ema_signal,
)


# =========================================================
# Validation
# =========================================================

def validate_dataframe(df: pd.DataFrame):

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

    if len(df) < 30:

        raise ValueError(
            "Trend module requires at least 30 candles."
        )


# =========================================================
# Swing High
# =========================================================

def swing_highs(

    df,

    lookback=2

):

    swings = []

    highs = df["high"].values

    for i in range(

        lookback,

        len(df)-lookback

    ):

        current = highs[i]

        left = highs[
            i-lookback:i
        ]

        right = highs[
            i+1:i+lookback+1
        ]

        if (

            current >

            left.max()

            and

            current >

            right.max()

        ):

            swings.append(

                (

                    i,

                    current

                )

            )

    return swings


# =========================================================
# Swing Low
# =========================================================

def swing_lows(

    df,

    lookback=2

):

    swings = []

    lows = df["low"].values

    for i in range(

        lookback,

        len(df)-lookback

    ):

        current = lows[i]

        left = lows[
            i-lookback:i
        ]

        right = lows[
            i+1:i+lookback+1
        ]

        if (

            current <

            left.min()

            and

            current <

            right.min()

        ):

            swings.append(

                (

                    i,

                    current

                )

            )

    return swings


# =========================================================
# Latest Swings
# =========================================================

def latest_swings(

    df,

    count=2

):

    highs = swing_highs(df)

    lows = swing_lows(df)

    if len(highs) < count:

        return None

    if len(lows) < count:

        return None

    return (

        highs[-count:],

        lows[-count:]

    )
# =========================================================
# Higher High
# =========================================================

def higher_highs(df):

    swings = latest_swings(df)

    if swings is None:

        return False

    highs, _ = swings

    return (

        highs[-1][1]

        >

        highs[-2][1]

    )
# =========================================================
# Lower High
# =========================================================

def lower_highs(df):

    swings = latest_swings(df)

    if swings is None:

        return False

    highs, _ = swings

    return (

        highs[-1][1]

        <

        highs[-2][1]

    )
# =========================================================
# Higher Low
# =========================================================

def higher_lows(df):

    swings = latest_swings(df)

    if swings is None:

        return False

    _, lows = swings

    return (

        lows[-1][1]

        >

        lows[-2][1]

    )
# =========================================================
# Lower Low
# =========================================================

def lower_lows(df):

    swings = latest_swings(df)

    if swings is None:

        return False

    _, lows = swings

    return (

        lows[-1][1]

        <

        lows[-2][1]

    )
# =========================================================
# Market Structure
# =========================================================

def market_structure(df):

    hh = higher_highs(df)

    hl = higher_lows(df)

    lh = lower_highs(df)

    ll = lower_lows(df)

    return {

        "hh": hh,

        "hl": hl,

        "lh": lh,

        "ll": ll

    }
# =========================================================
# Pullback
# =========================================================

def pullback(

    df,

    ema_period=20

):

    ema = ema_signal(

        df,

        fast=ema_period,

        medium=50,

        slow=200

    )

    close = float(

        df.close.iloc[-1]

    )

    previous = float(

        df.close.iloc[-2]

    )

    if ema.bullish:

        return (

            previous >

            ema.ema_fast

            and

            close <= ema.ema_fast

        )

    if ema.bearish:

        return (

            previous <

            ema.ema_fast

            and

            close >= ema.ema_fast

        )

    return False
# =========================================================
# EMA Alignment
# =========================================================

def ema_alignment(df):

    ema = ema_signal(df)

    return {

        "bullish": ema.bullish,

        "bearish": ema.bearish,

        "ema_fast": ema.ema_fast,

        "ema_medium": ema.ema_medium,

        "ema_slow": ema.ema_slow,

        "slope_fast": ema.slope_fast,

        "slope_medium": ema.slope_medium,

        "slope_slow": ema.slope_slow,

    }
# =========================================================
# Price Position
# =========================================================

def price_position(df):

    ema = ema_signal(df)

    close = float(df.close.iloc[-1])

    return {

        "above_fast": close > ema.ema_fast,

        "above_medium": close > ema.ema_medium,

        "above_slow": close > ema.ema_slow,

    }
# =========================================================
# Continuation
# =========================================================

def continuation(df):

    structure = market_structure(df)

    ema = ema_signal(df)

    if ema.bullish:

        return (

            structure["hh"]

            and

            structure["hl"]

        )

    if ema.bearish:

        return (

            structure["lh"]

            and

            structure["ll"]

        )

    return False
# =========================================================
# Trend Strength
# =========================================================

def trend_strength(df):

    score = 0

    structure = market_structure(df)

    ema = ema_signal(df)

    price = price_position(df)

    # EMA alignment

    if ema.bullish or ema.bearish:

        score += 30

    # Market structure

    # =========================================================
    # Market Structure Score
    # Only reward structure that matches the EMA trend
    # =========================================================

    if ema.bullish:

        if structure["hh"]:
            score += 10

        if structure["hl"]:
            score += 10

    elif ema.bearish:

        if structure["lh"]:
            score += 10

        if structure["ll"]:
            score += 10

    # Price above / below EMAs

    # =========================================================
    # Price Position
    # =========================================================

    close = float(df.close.iloc[-1])

    if ema.bullish:

        if close > ema.ema_fast:
            score += 5

        if close > ema.ema_medium:
            score += 5

        if close > ema.ema_slow:
            score += 5

    elif ema.bearish:

        if close < ema.ema_fast:
            score += 5

        if close < ema.ema_medium:
            score += 5

        if close < ema.ema_slow:
            score += 5

    # EMA slope

    # =========================================================
    # EMA Slope
    # =========================================================

    if ema.bullish:

        if ema.slope_fast > 0:
            score += 5

        if ema.slope_medium > 0:
            score += 5

        if ema.slope_slow > 0:
            score += 5

    elif ema.bearish:

        if ema.slope_fast < 0:
            score += 5

        if ema.slope_medium < 0:
            score += 5

        if ema.slope_slow < 0:
            score += 5

    return min(score, 100)
# =========================================================
# Market Phase
# =========================================================

def market_phase(df):

    ema = ema_signal(df)

    pb = pullback(df)

    cont = continuation(df)

    structure = market_structure(df)

    if ema.bullish:

        if pb:

            return "PULLBACK"

        if cont:

            return "UPTREND"

    if ema.bearish:

        if pb:

            return "PULLBACK"

        if cont:

            return "DOWNTREND"

    if (

        not structure["hh"]

        and

        not structure["ll"]

    ):

        return "RANGE"

    if (

        structure["hh"]

        and

        structure["ll"]

    ):

        return "REVERSAL"

    return "UNKNOWN"
# =========================================================
# Trend Direction
# =========================================================

def trend_direction(df):

    ema = ema_signal(df)

    if ema.bullish:

        return "BULLISH"

    if ema.bearish:

        return "BEARISH"

    return "SIDEWAYS"
# =========================================================
# Main Trend Signal
# =========================================================

def trend_signal(df):

    validate_dataframe(df)

    ema = ema_signal(df)

    structure = market_structure(df)

    position = price_position(df)

    phase = market_phase(df)

    strength = trend_strength(df)

    pb = pullback(df)

    cont = continuation(df)

    return TrendSignal(

        bullish=ema.bullish,

        bearish=ema.bearish,

        trend=trend_direction(df),

        phase=phase,

        strength=strength,

        higher_highs=structure["hh"],

        higher_lows=structure["hl"],

        lower_highs=structure["lh"],

        lower_lows=structure["ll"],

        pullback=pb,

        continuation=cont,

        price_above_fast=position["above_fast"],

        price_above_medium=position["above_medium"],

        price_above_slow=position["above_slow"],

    )
# =========================================================
# BUY Trend Filter
# =========================================================

def bullish_trend(df):

    return trend_signal(df).bullish


# =========================================================
# SELL Trend Filter
# =========================================================

def bearish_trend(df):

    return trend_signal(df).bearish


# =========================================================
# Pullback Filter
# =========================================================

def pullback_filter(df):

    return trend_signal(df).pullback


# =========================================================
# Continuation Filter
# =========================================================

def continuation_filter(df):

    return trend_signal(df).continuation


# =========================================================
# Strong Trend Filter
# =========================================================

def strong_trend(

    df,

    minimum_strength=70

):

    signal = trend_signal(df)

    return signal.strength >= minimum_strength
