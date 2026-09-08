"""
=========================================================
Professional Three Inside Down Strategy
=========================================================

Bearish reversal strategy.

Pattern

1. Large bullish candle
2. Small bearish candle completely inside first body
3. Strong bearish confirmation candle

=========================================================
"""

import pandas as pd

from config import (
    THREE_INSIDE_DOWN_WEIGHTS,
    PATTERN_LOOKBACK,
)

from engines.base_strategy import BaseStrategy


from utils.candle import (
    is_bullish,
    is_bearish,
    body_size,
    average_body,
    is_inside_body,
    short_term_uptrend,
    scan_triples,
    build_pattern,
    filter_fresh_patterns,
)


class ThreeInsideDownStrategy(BaseStrategy):

    CATEGORY = "Bearish Reversal"

    DIRECTION = "SELL"

    ENABLED = True

    PRIORITY = 92

    MIN_SCORE = 60

    REQUIRES_TREND = True

    REQUIRES_VOLUME = True

    REQUIRES_VWAP = True

    REQUIRES_ADX = True

    PATTERN_NAME = "Three Inside Down"

    # =====================================================
    # Direction
    # =====================================================

    def direction(self):

        return "SELL"

    # =====================================================
    # Strategy Weights
    # =====================================================

    def get_weights(self):

        return THREE_INSIDE_DOWN_WEIGHTS

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

            trend = short_term_uptrend(
                df,
                bars_ago=item["bars_ago"],
            )

            if not trend:
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
            # Second Candle
            # -------------------------------------------------

            if not is_bearish(c2):
                continue

            if not is_inside_body(c1, c2):
                continue

            # -------------------------------------------------
            # Third Candle
            # -------------------------------------------------

            if not is_bearish(c3):
                continue

            if c3.close >= c1.open:
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

            if body_size(c3) >= avg * 1.5:
                strength += 5

            if c3.close < c2.close:
                strength += 5

            if trend:
                strength += 5

            strength = min(strength, 100)

            # -------------------------------------------------
            # Return Pattern
            # -------------------------------------------------

            pattern = build_pattern(

                pattern=self.PATTERN_NAME,

                engine="three_inside_down",

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

            pattern["confirmation_body"] = float(body_size(c3))

            pattern["mother_body"] = float(body_size(c1))

            pattern["inside_body"] = float(body_size(c2))

            pattern["confirmation_break"] = float(c1.open - c3.close)

            pattern["average_body"] = float(avg)
            patterns.append(pattern)
        return filter_fresh_patterns(patterns)