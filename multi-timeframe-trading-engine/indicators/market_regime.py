"""
============================================================
Market Regime Detection

Classifies market into

STRONG_BULL
WEAK_BULL
RANGE
WEAK_BEAR
STRONG_BEAR

============================================================
"""

from dataclasses import dataclass

import pandas as pd

from config import *

from indicators.signals import (
    MarketRegimeSignal,
    EMASignal,
    ADXSignal,
)


# ==========================================================
# Helpers
# ==========================================================

def _ema_distance(close, ema200):
    """
    Percentage distance between price and slow EMA.
    Used as a measure of trend maturity.
    """
    if ema200 == 0:
        return 0.0

    return abs(close - ema200) / abs(ema200)

def _market_structure(df):

    if len(df) < 30:
        return False, False

    recent = df.iloc[-10:]
    previous = df.iloc[-30:-10]

    bullish = (
        recent.high.max() > previous.high.max()
        and
        recent.low.min() > previous.low.min()
    )

    bearish = (
        recent.high.max() < previous.high.max()
        and
        recent.low.min() < previous.low.min()
    )

    return bullish, bearish


# ==========================================================
# Main
# ==========================================================

def market_regime(
    df: pd.DataFrame,
    ema: EMASignal,
    adx: ADXSignal,
):

    if len(df) < MARKET_REGIME_LOOKBACK:

        return MarketRegimeSignal(
            state="RANGE",
            bullish=False,
            bearish=False,
            ranging=True,
            score=0,
            adx=0,
            ema_distance=0,
        )

    adx_value = float(adx.adx)

    close = float(df.close.iloc[-1])

    distance = _ema_distance(
        close,
        ema.ema_slow,
    )

    bullish_structure, bearish_structure = _market_structure(df)

    bull_score = 0
    bear_score = 0

    # -------------------------------------------------
    # EMA Alignment
    # -------------------------------------------------

    if ema.bullish:
        bull_score += 35

    if ema.bearish:
        bear_score += 35

    # -------------------------------------------------
    # EMA Slopes
    # -------------------------------------------------

    if ema.slope_fast > 0 and ema.slope_medium > 0:
        bull_score += 20

    if ema.slope_fast < 0 and ema.slope_medium < 0:
        bear_score += 20

    # -------------------------------------------------
    # Market Structure
    # -------------------------------------------------

    if bullish_structure:
        bull_score += 25

    if bearish_structure:
        bear_score += 25

    # -------------------------------------------------
    # Strong Trend
    # -------------------------------------------------

    if adx_value >= STRONG_TREND_ADX:

        if ema.bullish:
            bull_score += 10

        if ema.bearish:
            bear_score += 10

    # -------------------------------------------------
    # EMA Separation
    # -------------------------------------------------

    if distance >= EMA_STRONG_DISTANCE:

        if ema.bullish:
            bull_score += 10

        if ema.bearish:
            bear_score += 10
        # -----------------------------------------------------
        # Debug Regime Scoring
        # -----------------------------------------------------

        if PRINT_MARKET_STATE:

            print()

            print("========== REGIME SCORE ==========")

            print("Bull Score :", bull_score)

            print("Bear Score :", bear_score)

            print("ADX        :", round(adx_value, 2))

            print("Distance   :", round(distance, 5))

            print("Bull Struct:", bullish_structure)

            print("Bear Struct:", bearish_structure)

            print("===============================")

    # -----------------------------------------------------
    # Strong Bull
    # -----------------------------------------------------

    if bull_score >= 70:

        return MarketRegimeSignal(

            state="STRONG_BULL",

            bullish=True,

            bearish=False,

            ranging=False,

            score=MARKET_STATE_SCORES["STRONG_BULL"],

            adx=adx_value,

            ema_distance=distance,

        )

    elif bull_score >= 45:

        return MarketRegimeSignal(

            state="WEAK_BULL",

            bullish=True,

            bearish=False,

            ranging=False,

            score=MARKET_STATE_SCORES["WEAK_BULL"],

            adx=adx_value,

            ema_distance=distance,

        )
    # -----------------------------------------------------
    # Strong Bear
    # -----------------------------------------------------

    if bear_score >= 70:

        return MarketRegimeSignal(

            state="STRONG_BEAR",

            bullish=False,

            bearish=True,

            ranging=False,

            score=MARKET_STATE_SCORES["STRONG_BEAR"],

            adx=adx_value,

            ema_distance=distance,

        )

    elif bear_score >= 45:

        return MarketRegimeSignal(

            state="WEAK_BEAR",

            bullish=False,

            bearish=True,

            ranging=False,

            score=MARKET_STATE_SCORES["WEAK_BEAR"],

            adx=adx_value,

            ema_distance=distance,

        )

    # -----------------------------------------------------
    # Range
    # -----------------------------------------------------

    return MarketRegimeSignal(

        state="RANGE",

        bullish=False,

        bearish=False,

        ranging=True,

        score=MARKET_STATE_SCORES["RANGE"],

        adx=adx_value,

        ema_distance=distance,
    )