"""
=========================================================
Professional Spinning Top Strategy
=========================================================

Professional Spinning Top Detection

Characteristics

• Small body
• Long upper wick
• Long lower wick
• Market indecision

Direction

Downtrend  -> BUY
Uptrend    -> SELL

=========================================================
"""

import pandas as pd


from config import (
    SPINNING_TOP_WEIGHTS,
    PATTERN_LOOKBACK,
)

from engines.base_strategy import BaseStrategy

from config import (
    SPINNING_TOP_WEIGHTS,
    PATTERN_LOOKBACK,
)

from engines.base_strategy import BaseStrategy

from utils.candle import (
    body_size,
    candle_range,
    upper_wick,
    lower_wick,
    average_body,
    short_term_downtrend,
    short_term_uptrend,
    scan_single_meta,
    build_pattern,
    filter_fresh_patterns,
)


class SpinningTopStrategy(BaseStrategy):

    CATEGORY = "Indecision"

    DIRECTION = "DYNAMIC"

    ENABLED = True

    PRIORITY = 60

    MIN_SCORE = 55

    REQUIRES_TREND = True

    REQUIRES_VOLUME = False

    REQUIRES_VWAP = False

    REQUIRES_ADX = False

    PATTERN_NAME = "Spinning Top"

    # =====================================================
    # Default Direction
    # =====================================================

    def direction(self):

        return "DYNAMIC"

    # =====================================================
    # Strategy Weights
    # =====================================================

    def get_weights(self):

        return SPINNING_TOP_WEIGHTS

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
            rng = candle_range(candle)

            if rng == 0:
                continue

            avg = average_body(
                df,
                bars_ago=item["bars_ago"],
            )

            upper = upper_wick(candle)
            lower = lower_wick(candle)

            if b > avg * 0.50:
                continue

            if upper < b:
                continue

            if lower < b:
                continue

            direction = None

            if short_term_downtrend(
                df,
                bars_ago=item["bars_ago"],
            ):
                direction = "BUY"

            elif short_term_uptrend(
                df,
                bars_ago=item["bars_ago"],
            ):
                direction = "SELL"

            if direction is None:
                continue

            strength = 70

            if upper >= b * 2:
                strength += 5

            if lower >= b * 2:
                strength += 5

            if b <= avg * 0.30:
                strength += 10

            if upper >= b * 3:
                strength += 5

            if lower >= b * 3:
                strength += 5

            strength = min(strength, 100)

            stop = candle.low if direction == "BUY" else candle.high

            pattern = build_pattern(
                pattern=self.PATTERN_NAME,
                engine="spinning_top",
                direction=direction,
                candle=candle,
                bars_ago=item["bars_ago"],
                strength=strength,
                confidence=None,
                entry=float(candle.close),
                stop=float(stop),
                pattern_type="single",
            )

            pattern["upper_wick"] = float(upper)
            pattern["lower_wick"] = float(lower)

            if strength < self.MIN_SCORE:
                continue

            patterns.append(pattern)

        return filter_fresh_patterns(patterns)