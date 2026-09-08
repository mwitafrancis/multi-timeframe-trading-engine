import numpy as np

from config import *

from indicators import adx
from indicators.signals import RangeSignal
from indicators.adx import adx_signal
from indicators.ema import ema_signal


# ==========================================================
# Count touches around a level
# ==========================================================

def _count_touches(level, prices, tolerance):

    count = 0

    for p in prices:

        if abs(p - level) <= tolerance:

            count += 1

    return count


# ==========================================================
# Detect H1 Trading Range
# ==========================================================

def detect_range(df, atr):

    if not ENABLE_RANGE_TRADING:

        return RangeSignal(
            False,
            0,
            0,
            0,
            0,
            False,
            False,
            False,
            0,
            0,
            0,
        )

    lookback = min(RANGE_LOOKBACK, len(df))

    # Use full history for indicators
    indicator_data = df

    # Use recent candles only for range detection
    data = df.iloc[-lookback:]

    adx = adx_signal(indicator_data)

    ema = ema_signal(indicator_data)

    rolling_window = min(20, len(data))

    average_range = (
        data.high - data.low
    ).rolling(rolling_window).mean().iloc[-1]

    current_range = data.high.iloc[-1] - data.low.iloc[-1]

    atr_contracting = False

    if average_range > 0:

        contraction_ratio = current_range / average_range

        atr_contracting = contraction_ratio <= 0.85

    ema_compressed = False

    if ema.ema_slow != 0:

        ema_spread = abs(ema.ema_fast - ema.ema_slow)

        ema_compressed = (

            ema_spread

            <

            atr * 2.5

        )

    highs = data.high.values

    lows = data.low.values

    closes = data.close.values

    range_high = np.max(highs)

    range_low = np.min(lows)

    width = range_high - range_low

    middle = (range_high + range_low) / 2

    if width > atr * RANGE_MAX_WIDTH_ATR:

        return RangeSignal(
            False,
            range_high,
            range_low,
            middle,
            width,
            False,
            False,
            False,
            0,
            0,
            0,
        )

  

    tolerance = atr * RANGE_EDGE_ATR

    touches_high = _count_touches(

        range_high,

        highs,

        tolerance,

    )

    touches_low = _count_touches(

        range_low,

        lows,

        tolerance,

    )



    score = 0

    if touches_high >= RANGE_MIN_TOUCHES:
        score += 20

    if touches_low >= RANGE_MIN_TOUCHES:
        score += 20

    if adx.adx < STRONG_TREND_ADX:
        score += 20

    if not adx.expanding:
        score += 15

    if atr_contracting:
        score += 15

    if ema_compressed:
        score += 10

    valid = score >= 60

    

    price = closes[-1]

    near_top = False

    near_bottom = False

    in_middle = False

    if valid:

        top_distance = abs(price - range_high) / atr

        bottom_distance = abs(price - range_low) / atr

        if top_distance <= RANGE_EDGE_ATR:

            near_top = True

        elif bottom_distance <= RANGE_EDGE_ATR:

            near_bottom = True

        else:

            upper = middle + width * NO_TRADE_MIDDLE_PERCENT / 2

            lower = middle - width * NO_TRADE_MIDDLE_PERCENT / 2

            if lower <= price <= upper:

                in_middle = True

    score = 0

    if valid:

        score += 20

        if atr_contracting:

            score += 20

        if ema_compressed:

            score += 20

        if adx.adx < STRONG_TREND_ADX:

            score += 20

        if touches_high >= RANGE_MIN_TOUCHES + 1:

            score += 10

        if touches_low >= RANGE_MIN_TOUCHES + 1:

            score += 10

    if near_top:

        score += RANGE_EDGE_SCORE

    if near_bottom:

        score += RANGE_EDGE_SCORE

    score = min(score, 100)

    if PRINT_RANGE:

        print()

        print("========== RANGE ==========")

        print(f"VALID        : {valid}")

        print(f"HIGH         : {range_high:.5f}")

        print(f"LOW          : {range_low:.5f}")

        print(f"WIDTH        : {width:.5f}")

        print(f"TOUCHES HIGH : {touches_high}")

        print(f"TOUCHES LOW  : {touches_low}")

        print(f"TOP          : {near_top}")

        print(f"BOTTOM       : {near_bottom}")

        print(f"MIDDLE       : {in_middle}")
        print(f"ADX          : {adx.adx:.2f}")
        print(f"ATR Contract : {atr_contracting}")
        print(f"EMA Compact  : {ema_compressed}")
        print(f"ADX Expanding: {adx.expanding}")
        print(f"ADX Momentum : {adx.momentum:.2f}")
        print(f"Score        : {score}")

        print("===========================")

    return RangeSignal(

        valid,

        range_high,

        range_low,

        middle,

        width,

        near_top,

        near_bottom,

        in_middle,

        touches_high,

        touches_low,

        score,

    )