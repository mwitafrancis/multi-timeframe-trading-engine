"""
=========================================================
Professional Breakdown Three Strategy
=========================================================

Bearish breakout strategy.

Requirements

1. Existing bearish momentum
2. Three consecutive bearish candles
3. Consecutive lower closes
4. Last candle breaks previous swing low
5. Strong bearish body
6. Close near candle low

=========================================================
"""

import pandas as pd

from config import (
    BREAKDOWN_THREE_WEIGHTS,
    PATTERN_LOOKBACK,
)

from engines.base_strategy import BaseStrategy

from utils.candle import (

    consecutive_bearish,

    body_size,

    average_body,

    lower_wick,

    closes_near_low,

    scan_triples,

    build_pattern,

    filter_fresh_patterns,

)

class BreakdownThreeStrategy(BaseStrategy):

    CATEGORY = "Bearish Breakout"

    DIRECTION = "SELL"

    ENABLED = True

    PRIORITY = 94

    MIN_SCORE = 65

    REQUIRES_TREND = True

    REQUIRES_VOLUME = True

    REQUIRES_VWAP = False

    REQUIRES_ADX = True

    PATTERN_NAME = "Breakdown Three"

    # =====================================================
    # Direction
    # =====================================================

    def direction(self):

        return "SELL"

    # =====================================================
    # Strategy Weights
    # =====================================================

    def get_weights(self):

        return BREAKDOWN_THREE_WEIGHTS

    # =====================================================
    # Pattern Detection
    # =====================================================

    def detect(self, df: pd.DataFrame):

        if len(df) < 30:
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
            # Three bearish candles
            # -------------------------------------------------

            if not consecutive_bearish(

                df,

                count=3,

                bars_ago=item["bars_ago"],

            ):
                continue

            # -------------------------------------------------
            # Lower closes
            # -------------------------------------------------

            if c2.close >= c1.close:
                continue

            if c3.close >= c2.close:
                continue

            # -------------------------------------------------
            # Break previous swing low
            # -------------------------------------------------

            end = len(df) - item["bars_ago"] + 1

            lookback = df.iloc[
                max(0, end - 15): end - 3
            ]

            if len(lookback) == 0:
                continue

            swing_low = lookback.low.min()

            if c3.close >= swing_low:
                continue

            # -------------------------------------------------
            # Strong breakout candle
            # -------------------------------------------------

            avg = average_body(

                df,

                bars_ago=item["bars_ago"],

            )

            if body_size(c3) < avg:
                continue

            # -------------------------------------------------
            # Small lower wick
            # -------------------------------------------------

            if lower_wick(c3) > body_size(c3) * 0.40:
                continue

            # -------------------------------------------------
            # Close near low
            # -------------------------------------------------

            if not closes_near_low(c3):
                continue

            # -------------------------------------------------
            # Pattern Strength
            # -------------------------------------------------

            strength = 70

            if body_size(c3) > avg * 1.5:
                strength += 10

            if closes_near_low(c3):
                strength += 10

            if c3.close < swing_low:
                strength += 10

            strength = min(strength, 100)

            # -------------------------------------------------
            # Return Pattern
            # -------------------------------------------------

            pattern = build_pattern(

                pattern=self.PATTERN_NAME,

                engine="breakdown_three",

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

            patterns.append(pattern)
        return filter_fresh_patterns(patterns)
