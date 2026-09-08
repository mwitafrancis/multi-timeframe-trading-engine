"""
=========================================================
Professional Inverted Hammer Strategy
=========================================================

Bullish reversal strategy.

Requirements

1. Existing downtrend
2. Small body
3. Long upper wick
4. Tiny lower wick
5. Bullish or neutral close

=========================================================
"""

import pandas as pd

from config import (
    INVERTED_HAMMER_WEIGHTS,
    PATTERN_LOOKBACK,
)

from engines.base_strategy import BaseStrategy

from utils.candle import (
    body_size,
    average_body,
    upper_wick,
    lower_wick,
    closes_near_high,
    is_bullish,
    is_neutral,
    short_term_downtrend,
    scan_single_meta,
    build_pattern,
    filter_fresh_patterns,
)


class InvertedHammerStrategy(BaseStrategy):
    PATTERN_NAME = "Inverted Hammer"

    CATEGORY = "Bullish Reversal"

    DIRECTION = "BUY"

    ENABLED = True

    PRIORITY = 88

    MIN_SCORE = 60

    REQUIRES_TREND = True

    REQUIRES_VOLUME = True

    REQUIRES_VWAP = True

    REQUIRES_ADX = False

    

    def direction(self):
        return "BUY"

    def get_weights(self):
        return INVERTED_HAMMER_WEIGHTS

    def detect(self, df: pd.DataFrame):

        if len(df) < 20:
            return []

        patterns = []

        for item in scan_single_meta(
            df,
            PATTERN_LOOKBACK,
        ):

            candle = item["candle"]

            if not short_term_downtrend(
                df,
                bars_ago=item["bars_ago"],
            ):
                continue

            if not (
                is_bullish(candle)
                or is_neutral(candle)
            ):
                continue

            avg = average_body(
                df,
                bars_ago=item["bars_ago"],
            )

            b = body_size(candle)

            if b <= 0:
                continue

            uw = upper_wick(candle)
            lw = lower_wick(candle)

            if uw < b * 2.5:
                continue

            if lw > b * 0.30:
                continue

            if not closes_near_high(candle):
                continue

            strength = 70

            if uw >= b * 3:
                strength += 10

            if lw <= b * 0.20:
                strength += 5

            if b >= avg * 0.50:
                strength += 5

            if closes_near_high(candle):
                strength += 5

            if short_term_downtrend(
                df,
                bars_ago=item["bars_ago"],
            ):
                strength += 5

            strength = min(strength, 100)

            pattern = build_pattern(

                pattern=self.PATTERN_NAME,

                engine="inverted_hammer",

                direction=self.direction(),

                candle=candle,

                bars_ago=item["bars_ago"],

                strength=strength,

                confidence=None,

                entry=float(candle.close),

                stop=float(candle.low),

                pattern_type="single",

            )

            pattern["upper_wick"] = float(uw)
            pattern["lower_wick"] = float(lw)

            if strength < self.MIN_SCORE:
                continue

            patterns.append(pattern)

        return filter_fresh_patterns(patterns)