"""
=========================================================
Professional Evening Star Strategy
=========================================================

Bearish reversal strategy.

Pattern

1. Large bullish candle
2. Small indecision candle
3. Strong bearish confirmation candle

=========================================================
"""

import pandas as pd

from config import (
    EVENING_STAR_WEIGHTS,
    PATTERN_LOOKBACK,
)

from engines.base_strategy import BaseStrategy


from utils.candle import (
    body_size,
    average_body,
    midpoint,
    closes_near_low,
    is_bullish,
    is_bearish,
    short_term_uptrend,
    scan_triples,
    build_pattern,
    filter_fresh_patterns,
)


class EveningStarStrategy(BaseStrategy):
    PATTERN_NAME = "Evening Star"

    CATEGORY = "Reversal"

    DIRECTION = "SELL"

    ENABLED = True

    MIN_SCORE = 65

    PRIORITY = 95

    REQUIRES_TREND = True

    REQUIRES_VOLUME = True

    REQUIRES_VWAP = True

    REQUIRES_ADX = True


    # =====================================================
    # Direction
    # =====================================================

    def direction(self):

        return "SELL"

    # =====================================================
    # Strategy Weights
    # =====================================================

    def get_weights(self):

        return EVENING_STAR_WEIGHTS

    # =====================================================
    # Pattern Detection
    # =====================================================

    def detect(self, df: pd.DataFrame):

        if len(df) < 20:
            return []

        patterns = []

        for item in scan_triples(
            df,
            PATTERN_LOOKBACK,
        ):

            c1 = item["first"]
            c2 = item["second"]
            c3 = item["third"]

            # -------------------------------------------------
            # Existing Uptrend
            # -------------------------------------------------

            if not short_term_uptrend(
                df,
                bars_ago=item["bars_ago"],
            ):
                continue

            # -------------------------------------------------
            # First Candle
            # -------------------------------------------------

            if not is_bullish(c1):
                continue

            avg = average_body(
                df,
                bars_ago=item["bars_ago"],
            )

            if body_size(c1) < avg:
                continue

            # -------------------------------------------------
            # Middle Candle
            # -------------------------------------------------

            if body_size(c2) >= body_size(c1) * 0.50:
                continue

            # -------------------------------------------------
            # Third Candle
            # -------------------------------------------------

            if not is_bearish(c3):
                continue

            if body_size(c3) <= body_size(c2):
                continue

            if c3.close >= midpoint(c1):
                continue

            if not closes_near_low(c3):
                continue

            # -------------------------------------------------
            # Pattern Strength
            # -------------------------------------------------

            strength = 70

            if body_size(c1) >= avg:
                strength += 5

            if body_size(c3) >= avg:
                strength += 5

            if closes_near_low(c3):
                strength += 5

            if c3.close < midpoint(c1):
                strength += 5

            if body_size(c2) < avg * 0.50:
                strength += 5

            if short_term_uptrend(
                df,
                bars_ago=item["bars_ago"],
            ):
                strength += 5

            strength = min(strength, 100)

            pattern = build_pattern(

                pattern=self.PATTERN_NAME,

                engine="evening_star",

                direction=self.direction(),

                candle=c3,

                bars_ago=item["bars_ago"],

                strength=strength,

                confidence=None,

                entry=float(c3.close),

                stop=float(max(
                    c1.high,
                    c2.high,
                    c3.high,
                )),

                pattern_type="triple",

            )

            pattern["confirmation_close"] = float(c3.close)
            pattern["star_body"] = float(body_size(c2))

            if strength < self.MIN_SCORE:
                continue

            patterns.append(pattern)

        return filter_fresh_patterns(patterns)