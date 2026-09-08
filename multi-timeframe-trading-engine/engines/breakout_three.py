"""
=========================================================
Professional Breakout Three Strategy
=========================================================

Bullish breakout strategy.

Requirements

1. Existing bullish trend
2. Three bullish candles
3. Consecutive higher closes
4. Last candle breaks previous swing high
5. ATR expansion
6. Volume expansion
7. Strong breakout body

=========================================================
"""

import pandas as pd

from config import (
    BREAKOUT_THREE_WEIGHTS,
    PATTERN_LOOKBACK,
)

from engines.base_strategy import BaseStrategy



from utils.candle import (
    consecutive_bullish,
    body_size,
    average_body,
    upper_wick,
    closes_near_high,
    scan_triples,
    build_pattern,
    filter_fresh_patterns,
)

class BreakoutThreeStrategy(BaseStrategy):

    CATEGORY = "Bullish Breakout"

    DIRECTION = "BUY"

    ENABLED = True

    PRIORITY = 94

    MIN_SCORE = 65

    REQUIRES_TREND = True

    REQUIRES_VOLUME = True

    REQUIRES_VWAP = False

    REQUIRES_ADX = True

    PATTERN_NAME = "Breakout Three"

    def direction(self):
        return "BUY"

    def get_weights(self):
        return BREAKOUT_THREE_WEIGHTS

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

            if not consecutive_bullish(

                df,

                count=3,

                bars_ago=item["bars_ago"],

            ):
                continue

            if c2.close <= c1.close:
                continue

            if c3.close <= c2.close:
                continue

            end = len(df) - item["bars_ago"] + 1

            lookback = df.iloc[
                max(0, end - 15): end - 3
            ]

            if len(lookback) == 0:
                continue

            swing_high = lookback.high.max()

            if c3.close <= swing_high:
                continue

            avg = average_body(

                df,

                bars_ago=item["bars_ago"],

            )

            if body_size(c3) < avg:
                continue

            if upper_wick(c3) > body_size(c3) * 0.40:
                continue

            if not closes_near_high(c3):
                continue

            strength = 70

            if body_size(c3) > avg * 1.5:
                strength += 10

            if closes_near_high(c3):
                strength += 10

            if c3.close > swing_high:
                strength += 10

            strength = min(strength,100)

            pattern = build_pattern(

                pattern=self.PATTERN_NAME,

                engine="breakout_three",

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

            patterns.append(pattern)
        return filter_fresh_patterns(patterns)
     