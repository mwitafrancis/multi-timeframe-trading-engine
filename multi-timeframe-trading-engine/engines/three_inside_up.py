"""
=========================================================
Professional Three Inside Up Strategy
=========================================================

Bullish reversal strategy.

Pattern

1. Large bearish candle
2. Small bullish candle completely inside first body
3. Strong bullish confirmation candle

=========================================================
"""

import pandas as pd

from config import (
    THREE_INSIDE_UP_WEIGHTS,
    PATTERN_LOOKBACK,
)

from engines.base_strategy import BaseStrategy

from utils.candle import (
    is_bearish,
    is_bullish,
    body_size,
    average_body,
    is_inside_body,
    short_term_downtrend,
    scan_triples,
    build_pattern,
    filter_fresh_patterns,
)


class ThreeInsideUpStrategy(BaseStrategy):

    CATEGORY = "Bullish Reversal"

    DIRECTION = "BUY"

    ENABLED = True

    PRIORITY = 92

    MIN_SCORE = 60

    REQUIRES_TREND = True

    REQUIRES_VOLUME = True

    REQUIRES_VWAP = True

    REQUIRES_ADX = True

    PATTERN_NAME = "Three Inside Up"

    # =====================================================
    # Direction
    # =====================================================

    def direction(self):

        return "BUY"

    # =====================================================
    # Strategy Weights
    # =====================================================

    def get_weights(self):

        return THREE_INSIDE_UP_WEIGHTS

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
            # Existing Downtrend
            # -------------------------------------------------

            if not short_term_downtrend(
                df,
                bars_ago=item["bars_ago"],
            ):
                continue

            # -------------------------------------------------
            # First Candle
            # -------------------------------------------------

            if not is_bearish(c1):
                continue

            avg = average_body(
                df,
                bars_ago=item["bars_ago"],
            )

            if body_size(c1) < avg:
                continue

            # -------------------------------------------------
            # Second Candle
            # -------------------------------------------------

            if not is_bullish(c2):
                continue

            if not is_inside_body(c1, c2):
                continue

            # -------------------------------------------------
            # Third Candle
            # -------------------------------------------------

            if not is_bullish(c3):
                continue

            if c3.close <= c1.open:
                continue

            # -------------------------------------------------
            # Pattern Strength
            # -------------------------------------------------

            strength = 70

            if body_size(c1) >= avg:
                strength += 5

            if is_inside_body(c1, c2):
                strength += 5

            if body_size(c3) >= avg:
                strength += 10

            if c3.close > c2.close:
                strength += 5

            if short_term_downtrend(
                df,
                bars_ago=item["bars_ago"],
            ):
                strength += 5

            strength = min(strength, 100)

            # -------------------------------------------------
            # Return Pattern
            # -------------------------------------------------

            pattern = build_pattern(

                pattern=self.PATTERN_NAME,

                engine="three_inside_up",

                direction=self.direction(),

                candle=c3,

                bars_ago=item["bars_ago"],

                strength=strength,

                confidence=None,

                entry=float(c3.close),

                stop=float(min(
                    c1.low,
                    c2.low,
                    c3.low,
                )),

                pattern_type="triple",

            )

            pattern["confirmation_close"] = float(c3.close)
            pattern["mother_body"] = float(body_size(c1))
            pattern["confirmation_body"] = float(body_size(c3))
            pattern["inside_body"] = float(body_size(c2))
            pattern["confirmation_break"] = float(c3.close - c1.open)
            pattern["average_body"] = float(avg)

            if strength < self.MIN_SCORE:
                continue

            patterns.append(pattern)
        return filter_fresh_patterns(patterns)