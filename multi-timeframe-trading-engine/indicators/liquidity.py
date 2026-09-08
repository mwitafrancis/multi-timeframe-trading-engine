"""
=========================================================
Liquidity Zone Detection
=========================================================

Detects:
    - Buy-side liquidity: clustered swing highs / equal highs
    - Sell-side liquidity: clustered swing lows / equal lows
    - Liquidity sweeps: price trades through a liquidity zone
      and closes back through the zone.

Important:
    Only confirmed candles are used. The currently forming candle
    is excluded when possible.
=========================================================
"""

from dataclasses import dataclass
import numpy as np

from config import *
from indicators.signals import LiquidityZone, LiquiditySignal


def _swing_high(df, i, left, right, tolerance=0.0):

    if i < left or i > len(df) - right - 1:
        return False

    value = float(df.high.iloc[i])

    left_max = float(
        df.high.iloc[i - left:i].max()
    )

    right_max = float(
        df.high.iloc[i + 1:i + right + 1].max()
    )

    return (
        value >= left_max
        and
        value >= right_max
    )


def _swing_low(df, i, left, right, tolerance=0.0):

    if i < left or i > len(df) - right - 1:
        return False

    value = float(df.low.iloc[i])

    left_min = float(
        df.low.iloc[i - left:i].min()
    )

    right_min = float(
        df.low.iloc[i + 1:i + right + 1].min()
    )

    return (
        value <= left_min
        and
        value <= right_min
    )


def _cluster_levels(levels, tolerance):
    if not levels:
        return []

    levels = sorted(levels, key=lambda x: x[0])
    clusters = [[levels[0]]]

    for item in levels[1:]:
        if abs(item[0] - clusters[-1][-1][0]) <= tolerance:
            clusters[-1].append(item)
        else:
            clusters.append([item])

    return clusters


def _build_zones(df, swings, zone_type, atr):
    if not swings or atr <= 0:
        return []

    tolerance = max(
        atr * LIQUIDITY_CLUSTER_ATR,
        float(np.mean([x[0] for x in swings])) * LIQUIDITY_CLUSTER_PRICE_PERCENT,
    )

    zones = []

    for cluster in _cluster_levels(swings, tolerance):
        if len(cluster) < LIQUIDITY_MIN_TOUCHES:
            continue

        prices = [x[0] for x in cluster]
        level = float(np.mean(prices))
        raw_half_width = max(
            atr * LIQUIDITY_ZONE_WIDTH_ATR,
            (max(prices) - min(prices)) / 2.0,
        )

        max_half_width = (
            atr * LIQUIDITY_MAX_ZONE_WIDTH_ATR
        )

        half_width = min(
            raw_half_width,
            max_half_width,
        )

        low = level - half_width
        high = level + half_width
        last_index = max(x[1] for x in cluster)

        touches = len(cluster)
        strength = min(
            100.0,
            LIQUIDITY_BASE_SCORE + touches * LIQUIDITY_TOUCH_SCORE,
        )

        zones.append(
            LiquidityZone(
                high=high,
                low=low,
                midpoint=level,
                zone_type=zone_type,
                touches=touches,
                strength=strength,
                distance=float("inf"),
                distance_score=0.0,
                swept=False,
                sweep_index=-1,
                bar_index=last_index,
                timestamp=df.index[last_index],
            )
        )

    return zones


def _detect_sweep(df, zone, atr):

    """
    Detect the most recent liquidity sweep.

    A BUY_SIDE liquidity sweep:
        price trades above the zone
        then closes back below the midpoint.

    A SELL_SIDE liquidity sweep:
        price trades below the zone
        then closes back above the midpoint.

    Only recent sweeps are considered valid.
    """

    if atr <= 0:
        return False, -1

    start = max(
        zone.bar_index + 1,
        0,
    )

    end = len(df)

    buffer = (
        atr * LIQUIDITY_SWEEP_BUFFER_ATR
    )

    latest_sweep = -1

    for i in range(start, end):

        high = float(df.high.iloc[i])
        low = float(df.low.iloc[i])
        close = float(df.close.iloc[i])

        # -----------------------------------------------
        # BUY-SIDE LIQUIDITY
        # -----------------------------------------------
        if zone.zone_type == "BUY_SIDE":

            if (
                high > zone.high + buffer
                and
                close < zone.midpoint
            ):
                latest_sweep = i

        # -----------------------------------------------
        # SELL-SIDE LIQUIDITY
        # -----------------------------------------------
        else:

            if (
                low < zone.low - buffer
                and
                close > zone.midpoint
            ):
                latest_sweep = i

    if latest_sweep < 0:
        return False, -1

    latest_index = len(df) - 1

    age = latest_index - latest_sweep

    if age > LIQUIDITY_SWEEP_MAX_AGE:
        return False, -1

    zone.swept = True
    zone.sweep_index = latest_sweep

    return True, latest_sweep


def _nearest_zone(zones, price, atr):
    if not zones or atr <= 0:
        return None

    for zone in zones:
        zone.distance = abs(price - zone.midpoint)
        zone.distance_score = max(
            0.0,
            100.0 - (zone.distance / atr) * 25.0,
        )

    return min(zones, key=lambda z: z.distance)


def detect_liquidity(df, atr, already_closed=False):
    if df is None or len(df) < 10 or atr is None or atr <= 0:
        return LiquiditySignal.invalid()

    # Do not use the currently forming candle.
    if USE_CLOSED_CANDLES_ONLY and len(df) > 1 and not already_closed:

        source = df.iloc[:-1].copy()

    else:

        source = df.copy()
    if len(source) > LIQUIDITY_LOOKBACK:
        source = source.iloc[-LIQUIDITY_LOOKBACK:].copy()

    if len(source) < LIQUIDITY_SWING_LEFT + LIQUIDITY_SWING_RIGHT + 3:
        return LiquiditySignal.invalid()

    tolerance = 0.0
    highs = []
    lows = []

    for i in range(
        LIQUIDITY_SWING_LEFT,
        len(source) - LIQUIDITY_SWING_RIGHT,
    ):
        if _swing_high(
            source,
            i,
            LIQUIDITY_SWING_LEFT,
            LIQUIDITY_SWING_RIGHT,
            tolerance,
        ):
            highs.append((float(source.high.iloc[i]), i, source.index[i]))

        if _swing_low(
            source,
            i,
            LIQUIDITY_SWING_LEFT,
            LIQUIDITY_SWING_RIGHT,
            tolerance,
        ):
            lows.append((float(source.low.iloc[i]), i, source.index[i]))

    buy_zones = _build_zones(source, highs, "BUY_SIDE", atr)
    sell_zones = _build_zones(source, lows, "SELL_SIDE", atr)

    # Sweep detection uses only candles available in source.
    for zone in buy_zones:
        _detect_sweep(source, zone, atr)

    for zone in sell_zones:
        _detect_sweep(source, zone, atr)

    price = float(source.close.iloc[-1])

    buy_side = _nearest_zone(buy_zones, price, atr)
    sell_side = _nearest_zone(sell_zones, price, atr)

    near_buy = bool(
        buy_side and buy_side.distance <= atr * LIQUIDITY_DISTANCE_ATR
    )
    near_sell = bool(
        sell_side and sell_side.distance <= atr * LIQUIDITY_DISTANCE_ATR
    )

    swept_buy = bool(buy_side and buy_side.swept)
    swept_sell = bool(sell_side and sell_side.swept)

    score = 0.0

    # Liquidity is a location component, not a standalone trade trigger.
    if near_buy or near_sell:
        score += LIQUIDITY_PROXIMITY_SCORE

    if swept_buy or swept_sell:
        score += LIQUIDITY_SWEEP_SCORE

    if buy_side and buy_side.strength >= LIQUIDITY_STRONG_ZONE_STRENGTH:
        score += LIQUIDITY_STRONG_ZONE_BONUS

    if sell_side and sell_side.strength >= LIQUIDITY_STRONG_ZONE_STRENGTH:
        score += LIQUIDITY_STRONG_ZONE_BONUS

    score = min(100.0, score)

    if PRINT_LIQUIDITY:
        print("\n========== LIQUIDITY ==========")
        print(f"Price             : {price:.5f}")
        print(
            f"Buy-side          : "
            f"{buy_side.midpoint:.5f}"
            if buy_side else "Buy-side          : None"
        )
        print(
            f"Sell-side         : "
            f"{sell_side.midpoint:.5f}"
            if sell_side else "Sell-side         : None"
        )
        print(f"Near Buy-side     : {near_buy}")
        print(f"Near Sell-side    : {near_sell}")
        print(f"Buy-side Swept    : {swept_buy}")
        print(f"Sell-side Swept   : {swept_sell}")
        print(f"Liquidity Score   : {score:.1f}")
        print("================================")

    return LiquiditySignal(
        valid=True,
        buy_side=buy_side,
        sell_side=sell_side,
        near_buy_side=near_buy,
        near_sell_side=near_sell,
        swept_buy_side=swept_buy,
        swept_sell_side=swept_sell,
        score=score,
    )
