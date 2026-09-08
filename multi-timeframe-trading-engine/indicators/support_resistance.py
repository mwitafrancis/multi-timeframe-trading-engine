import numpy as np

from dataclasses import dataclass

from config import *

from indicators.signals import (
    SRLevel,
    SRSignal,
)

# ==========================================================
# SWING DETECTION
# ==========================================================


def is_swing_high(df, i, atr):

    left = SWING_LEFT
    right = SWING_RIGHT

    if i < left:
        return False

    if i > len(df) - right - 1:
        return False

    high = df.high.iloc[i]

    left_high = df.high.iloc[i-left:i]

    right_high = df.high.iloc[i+1:i+right+1]

    tolerance = atr * SWING_TOLERANCE_ATR

    body = abs(

        df.close.iloc[i]

        -

        df.open.iloc[i]

    )

    if body < atr * 0.20:

        return False

    return (
        high >= left_high.max() - tolerance
        and
        high >= right_high.max() - tolerance
    )


def is_swing_low(df, i, atr):

    left = SWING_LEFT
    right = SWING_RIGHT

    if i < left:
        return False

    if i > len(df) - right - 1:
        return False

    low = df.low.iloc[i]

    left_low = df.low.iloc[i-left:i]

    right_low = df.low.iloc[i+1:i+right+1]
    tolerance = atr * SWING_TOLERANCE_ATR

    body = abs(

        df.close.iloc[i]

        -

        df.open.iloc[i]

    )

    if body < atr * 0.20:

        return False

    return (
        low <= left_low.min() + tolerance
        and
        low <= right_low.min() + tolerance
    )


# ==========================================================
# FIND SWINGS
# ==========================================================


def find_swings(df, atr):

    highs = []

    lows = []

    for i in range(SWING_LEFT, len(df)-SWING_RIGHT):

        if is_swing_high(df, i, atr):

            highs.append(

                (
                    float(df.high.iloc[i]),
                    i,
                    df.index[i],
                )

            )

        if is_swing_low(df, i, atr):

            lows.append(

                (
                    float(df.low.iloc[i]),
                    i,
                    df.index[i],
                )

            )
    return highs, lows


# ==========================================================
# CLUSTER LEVELS
# ==========================================================


def cluster_levels(levels, atr):

    if len(levels) == 0:
        return []

    price = np.mean([x[0] for x in levels])
    # ATR handles volatility.
    # Price percentage keeps clustering working on
    # crypto, forex and indices.

    tolerance = max(
        atr * LEVEL_CLUSTER_ATR,
        price * LEVEL_CLUSTER_PRICE_PERCENT,
)

    levels = sorted(
        levels,
        key=lambda x: x[0],
    )

    clusters = []

    current = [levels[0]]

    for level in levels[1:]:

        if abs(level[0] - current[-1][0]) <= tolerance:

            current.append(level)

        else:

            clusters.append(current)

            current = [level]

    clusters.append(current)

    return clusters


# ==========================================================
# BUILD SR LEVELS
# ==========================================================


def build_levels(

    df,

    clusters,

    kind,

):

    sr = []

    for cluster in clusters:

        if len(cluster) < MIN_LEVEL_TOUCHES:
            continue

        price = np.mean(

            [x[0] for x in cluster]

        )

        touch_score = min(

            35,

            len(cluster) * 7,

        )

        last_bar = cluster[-1][1]

        bars_old = len(df) - last_bar

        freshness_score = max(

            0,

            25 - bars_old * 0.20,

        )

        reaction_score = 30

        strength = (

            touch_score

            +

            reaction_score

            +

            freshness_score

        )

        sr.append(

            SRLevel(

                price=price,

                touches=len(cluster),

                strength=strength,

                kind=kind,

                bar_index=cluster[-1][1],

                timestamp=cluster[-1][2],

            )

        )

    sr.sort(

        key=lambda x: x.strength,

        reverse=True

    )

    return sr[:MAX_LEVELS]


# ==========================================================
# FIND NEAREST LEVEL
# ==========================================================


def nearest_support(levels, price):

    below = [

        l for l in levels

        if l.price <= price

    ]

    if not below:
        return None

    return max(

        below,

        key=lambda x: x.price

    )


def nearest_resistance(levels, price):

    above = [

        l for l in levels

        if l.price >= price

    ]

    if not above:
        return None

    return min(

        above,

        key=lambda x: x.price

    )


# ==========================================================
# MAIN
# ==========================================================


def support_resistance_signal(

    df,

    atr,

    adx,

):

    highs, lows = find_swings(df, atr)

    resistance = build_levels(

        df,

        cluster_levels(highs, atr),

        "resistance",

    )
    support = build_levels(

        df,

        cluster_levels(lows, atr),

        "support"

    )

    price = df.close.iloc[-1]

    nearest_sup = nearest_support(
        

        support,

        price

    )
    if (

        nearest_sup

        and

        nearest_sup.strength < 45

    ):

        nearest_sup = None

    if nearest_sup:

        distance = abs(

            price -

            nearest_sup.price

        ) / atr

        strength = nearest_sup.strength

        strength -= distance * 4

        if (

            adx.bullish

            and

            adx.expanding

        ):

            strength += 10

        elif (

            adx.bullish

            and

            adx.strong_trend

        ):

            strength += 5

        nearest_sup.strength = min(

            100,

            max(

                0,

                strength,

            ),

        )
    nearest_res = nearest_resistance(

        resistance,

        price

    )
    if (

        nearest_res

        and

        nearest_res.strength < 45

    ):

        nearest_res = None
    if nearest_res:

        distance = abs(

            price -

            nearest_res.price

        ) / atr

        strength = nearest_res.strength

        strength -= distance * 4

        if (

            adx.bearish

            and

            adx.expanding

        ):

            strength += 10

        elif (

            adx.bearish

            and

            adx.strong_trend

        ):

            strength += 5

        nearest_res.strength = min(

            100,

            max(

                0,

                strength,

            ),

        )

    near_support = False

    near_resistance = False

    if nearest_sup:

        if price < nearest_sup.price - atr:

            nearest_sup = None

        else:
            support_distance_atr = abs(price - nearest_sup.price) / atr

            support_score = max(
                0,
                100 - support_distance_atr * 25
            )

            nearest_sup.distance_score = support_score
            nearest_sup.distance = abs(price - nearest_sup.price)
            last = df.iloc[-1]
            nearest_sup.touched = float(last.low) <= nearest_sup.price + atr * 0.05 and float(last.high) >= nearest_sup.price - atr * 0.05

            near_support = (

                abs(

                    price -

                    nearest_sup.price

                )

                <=

                atr * SUP_RES_DISTANCE_ATR

            )

    if nearest_res:

        if price > nearest_res.price + atr:

            nearest_res = None

        else:
            resistance_distance_atr = abs(price - nearest_res.price) / atr

            resistance_score = max(
                0,
                100 - resistance_distance_atr * 25
            )

            nearest_res.distance_score = resistance_score
            nearest_res.distance = abs(price - nearest_res.price)
            last = df.iloc[-1]
            nearest_res.touched = float(last.low) <= nearest_res.price + atr * 0.05 and float(last.high) >= nearest_res.price - atr * 0.05

            near_resistance = (

                abs(

                    price -

                    nearest_res.price

                )

                <=

                atr * SUP_RES_DISTANCE_ATR

            )
    if PRINT_SUPPORT:

        print()

        print("========== SUPPORT ==========")

        if nearest_sup:

            print(f"Price      : {nearest_sup.price:.5f}")

            print(f"Touches    : {nearest_sup.touches}")

            print(f"Strength   : {nearest_sup.strength:.1f}")

            print(

                f"DistanceATR: {abs(price-nearest_sup.price)/atr:.2f}"

            )

            print(f"Near       : {near_support}")

        else:

            print("None")

    if PRINT_RESISTANCE:

        print()

        print("========== RESISTANCE ==========")

        if nearest_res:

            print(f"Price      : {nearest_res.price:.5f}")

            print(f"Touches    : {nearest_res.touches}")

            print(f"Strength   : {nearest_res.strength:.1f}")

            print(

                f"DistanceATR: {abs(price-nearest_res.price)/atr:.2f}"

            )

            print(f"Near       : {near_resistance}")

        else:

            print("None")

    return SRSignal(

        support=nearest_sup,

        resistance=nearest_res,

        near_support=near_support,

        near_resistance=near_resistance

    )