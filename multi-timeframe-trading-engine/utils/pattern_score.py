"""
============================================================

Professional Candlestick Pattern Scoring Engine

============================================================

Every engine imports this module.

Returns

0-100 Quality Score

Portfolio project

============================================================
"""

from utils.candle import *


# ----------------------------------------------------------
# Clamp
# ----------------------------------------------------------

def clamp(score):

    return max(0, min(100, round(score)))


# ----------------------------------------------------------
# Body Score
# ----------------------------------------------------------

def body_score(candle):

    pct = body_percentage(candle)

    if pct >= 0.90:
        return 20

    if pct >= 0.80:
        return 18

    if pct >= 0.70:
        return 16

    if pct >= 0.60:
        return 14

    if pct >= 0.50:
        return 10

    return 5


# ----------------------------------------------------------
# Wick Score
# ----------------------------------------------------------

def wick_score(candle):

    upper = upper_percentage(candle)

    lower = lower_percentage(candle)

    wick = upper + lower

    if wick < 0.10:
        return 15

    if wick < 0.20:
        return 12

    if wick < 0.30:
        return 10

    if wick < 0.40:
        return 7

    return 3


# ----------------------------------------------------------
# Trend Score
# ----------------------------------------------------------

def trend_score(direction, ema_fast, ema_slow):

    distance = abs(ema_fast - ema_slow)

    percent = distance / ema_slow

    if percent < 0.0005:
        return 8

    if direction == "BUY":
        if ema_fast > ema_slow:
            return 15
        return 3

    if ema_fast < ema_slow:
        return 15

    return 3
def freshness_score(bars_ago):

    if bars_ago == 0:
        return 15

    if bars_ago == 1:
        return 13

    if bars_ago == 2:
        return 10

    if bars_ago == 3:
        return 7

    return 0

# ----------------------------------------------------------
# Volume Score
# ----------------------------------------------------------

def volume_score(volume, average):

    if average == 0:
        return 0

    ratio = volume / average

    if ratio >= 2:
        return 15

    if ratio >= 1.5:
        return 12

    if ratio >= 1.2:
        return 10

    if ratio >= 1:
        return 8

    return 2


# ----------------------------------------------------------
# ATR Score
# ----------------------------------------------------------

def atr_score(body_size, atr):

    if atr == 0:
        return 0

    ratio = body_size / atr

    if ratio >= 2:
        return 15

    if ratio >= 1.5:
        return 12

    if ratio >= 1.2:
        return 10

    if ratio >= 1:
        return 8

    return 3

def ema_distance_score(fast, slow):

    diff = abs(fast-slow)

    if diff>0.005:
        return 15

    if diff>0.003:
        return 12

    if diff>0.001:
        return 8

    return 3

def close_strength(candle,direction):

    rng = candle.high-candle.low

    if rng==0:
        return 0

    if direction=="BUY":

        pct=(candle.close-candle.low)/rng

    else:

        pct=(candle.high-candle.close)/rng

    if pct>0.9:
        return 15

    if pct>0.8:
        return 12

    if pct>0.7:
        return 8

    return 3

def rsi_score(rsi, direction):

    if direction=="BUY":

        if rsi<30:
            return 15

        if rsi<40:
            return 10

        if rsi<60:
            return 6

        return 2

    else:

        if rsi>70:
            return 15

        if rsi>60:
            return 10

        if rsi>40:
            return 6

        return 2

# ----------------------------------------------------------
# Pattern Strength
# ----------------------------------------------------------

def pattern_strength(name):

    table = {

        # Highest probability
        "Bullish Engulfing":22,
        "Bearish Engulfing":22,

        "Morning Star":22,
        "Evening Star":22,

        "Three White Soldiers":21,
        "Three Black Crows":21,

        # Strong reversals
        "Hammer":19,
        "Shooting Star":19,
        "Hanging Man":18,
        "Inverted Hammer":18,
        "Pin Bar":18,

        # Continuations
        "Breakout Three":17,
        "Breakdown Three":17,

        # Moderate
        "Three Inside Up":16,
        "Three Inside Down":16,

        # Weak
        "Dragonfly Doji":15,
        "Gravestone Doji":15,

        "Long Legged Doji":12,
        "Doji":10,
        "Spinning Top":8,
    }

    return table.get(name,15)


# ----------------------------------------------------------
# Relative Size
# ----------------------------------------------------------

def relative_body_score(df):

    avg = average_body(df,20)

    current = body(df.iloc[-1])

    if avg == 0:
        return 0

    ratio = current / avg

    if ratio >= 2:

        return 15

    if ratio >= 1.5:

        return 12

    if ratio >= 1.2:

        return 10

    if ratio >= 1:

        return 8

    return 3

def distance_score(distance, atr):

    if atr == 0:
        return 0

    ratio = distance / atr

    if ratio <= 0.10:
        return 15

    if ratio <= 0.20:
        return 12

    if ratio <= 0.30:
        return 8

    if ratio <= 0.50:
        return 4

    return 0


# ----------------------------------------------------------
# Main Score
# ----------------------------------------------------------

def score_pattern(
    pattern,
    candle,
    df,
    ema_fast,
    ema_slow,
    atr,
    volume,
    average_volume,
    direction,
    bars_ago,
    distance_from_entry,
    rsi,
):

    score = 0

    score += pattern_strength(pattern)

    score += body_score(candle)

    score += wick_score(candle)

    score += trend_score(direction, ema_fast, ema_slow)

    score += ema_distance_score(ema_fast, ema_slow)

    score += volume_score(volume, average_volume)

    score += atr_score(body(candle), atr)

    score += relative_body_score(df)

    score += freshness_score(bars_ago)

    score += distance_score(distance_from_entry, atr)

    score += rsi_score(rsi, direction)

    score += close_strength(candle, direction)

    return clamp(score)