"""
=========================================================
Professional Hanging Man Strategy
=========================================================

Bearish reversal strategy.

Requirements

1. Existing uptrend
2. Small body
3. Long lower wick
4. Tiny upper wick
5. Bearish or neutral close
6. Close near candle low

=========================================================
"""

import pandas as pd

from config import (
    HANGING_MAN_WEIGHTS,
    PATTERN_LOOKBACK,
)

from engines.base_strategy import BaseStrategy

from utils.candle import (
    body_size,
    average_body,
    lower_wick,
    upper_wick,
    closes_near_low,
    is_bearish,
    is_neutral,
    short_term_uptrend,
    scan_single_meta,
    build_pattern,
    filter_fresh_patterns,
)


class HangingManStrategy(BaseStrategy):
    PATTERN_NAME = "Hanging Man"

    CATEGORY = "Bearish Reversal"

    DIRECTION = "SELL"

    ENABLED = True

    PRIORITY = 88

    MIN_SCORE = 72

    REQUIRES_TREND = True

    REQUIRES_VOLUME = True

    REQUIRES_VWAP = True

    REQUIRES_ADX = False

    PATTERN_NAME = "Hanging Man"

    # =====================================================
    # Direction
    # =====================================================

    def direction(self):

        return "SELL"

    # =====================================================
    # Strategy Weights
    # =====================================================

    def get_weights(self):

        return HANGING_MAN_WEIGHTS

    # =====================================================
    # Pattern Detection
    # =====================================================

    def detect(self, df: pd.DataFrame):

        if len(df) < 20:
            return []

        patterns = []

        for item in scan_single_meta(
            df,
            PATTERN_LOOKBACK,
        ):

            candle = item["candle"]

            if not short_term_uptrend(
                df,
                bars_ago=item["bars_ago"],
            ):
                continue

            if not (
                is_bearish(candle)
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

            lw = lower_wick(candle)
            uw = upper_wick(candle)

            if lw < b * 2.5:
                continue

            if uw > b * 0.30:
                continue

            if not closes_near_low(candle):
                continue

            strength = 70

            if lw >= b * 3:
                strength += 10

            if uw <= b * 0.20:
                strength += 5

            if b >= avg * 0.50:
                strength += 5

            if closes_near_low(candle):
                strength += 5

            if short_term_uptrend(
                df,
                bars_ago=item["bars_ago"],
            ):
                strength += 5

            strength = min(strength, 100)

            pattern = build_pattern(

                pattern=self.PATTERN_NAME,

                engine="hanging_man",

                direction=self.direction(),

                candle=candle,

                bars_ago=item["bars_ago"],

                strength=strength,

                confidence=None,

                entry=float(candle.close),

                stop=float(candle.high),

                pattern_type="single",

            )

            pattern["upper_wick"] = float(uw)
            pattern["lower_wick"] = float(lw)

            if strength < self.MIN_SCORE:
                continue

            patterns.append(pattern)

        return filter_fresh_patterns(patterns)