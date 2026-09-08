"""
=========================================================
Professional Shooting Star Strategy
=========================================================

Bearish reversal strategy based on the Shooting Star
candlestick pattern.

Workflow

Pattern Detection
        ↓
BaseStrategy Confirmation
        ↓
TradeSignal

Author: francis
=========================================================
"""

import pandas as pd




from config import (
    SHOOTING_STAR_WEIGHTS,
    PATTERN_LOOKBACK,
)

from engines.base_strategy import BaseStrategy

from utils.candle import (
    body_size,
    upper_wick,
    lower_wick,
    average_body,
    is_bearish,
    short_term_uptrend,
    scan_single_meta,
    build_pattern,
    filter_fresh_patterns,
)

class ShootingStarStrategy(BaseStrategy):
    PATTERN_NAME = "Shooting Star"

    CATEGORY = "Reversal"

    DIRECTION = "SELL"

    ENABLED = True

    PATTERN_NAME = "Shooting Star"

    MIN_SCORE = 60

    PRIORITY = 90

    REQUIRES_TREND = True

    REQUIRES_VOLUME = True

    REQUIRES_VWAP = True

    REQUIRES_ADX = False


    # =====================================================
    # Direction
    # =====================================================

    def direction(self):

        return "SELL"

    # =====================================================
    # Strategy Weights
    # =====================================================

    def get_weights(self):

        return SHOOTING_STAR_WEIGHTS

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

            b = body_size(candle)

            if b <= 0:
                continue

            upper = upper_wick(candle)
            lower = lower_wick(candle)

            avg = average_body(
                df,
                bars_ago=item["bars_ago"],
            )

            if not short_term_uptrend(
                df,
                bars_ago=item["bars_ago"],
            ):
                continue

            long_upper = upper >= b * 2.5
            small_lower = lower <= b * 0.30
            body_normal = b >= avg * 0.40
            body_near_low = lower < upper * 0.25
            bearish_close = is_bearish(candle)

            valid = (
                long_upper
                and small_lower
                and body_normal
                and body_near_low
            )

            if not valid:
                continue

            strength = 70

            if long_upper:
                strength += 10

            if small_lower:
                strength += 5

            if bearish_close:
                strength += 5

            if body_near_low:
                strength += 5

            if body_normal:
                strength += 5

            if short_term_uptrend(
                df,
                bars_ago=item["bars_ago"],
            ):
                strength += 5

            strength = min(strength, 100)

            pattern = build_pattern(
                pattern=self.PATTERN_NAME,
                engine="shooting_star",
                direction=self.direction(),
                candle=candle,
                bars_ago=item["bars_ago"],
                strength=strength,
                confidence=None,
                entry=float(candle.close),
                stop=float(candle.high),
                pattern_type="single",
            )

            pattern["upper_wick"] = float(upper)
            pattern["lower_wick"] = float(lower)

            if strength < self.MIN_SCORE:
                continue

            patterns.append(pattern)

        return filter_fresh_patterns(patterns)