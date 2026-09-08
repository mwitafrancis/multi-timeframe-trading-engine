"""
=========================================================
Professional Doji Strategy
=========================================================

Professional Doji Detection

Supported

• Standard Doji
• Long Legged Doji
• Dragonfly Doji
• Gravestone Doji

=========================================================
"""

import pandas as pd

from config import (
    DOJI_WEIGHTS,
    PATTERN_LOOKBACK,
)

from engines.base_strategy import BaseStrategy

from utils.candle import (
    candle_range,
    upper_wick,
    lower_wick,
    is_doji,
    short_term_downtrend,
    short_term_uptrend,
    scan_single_meta,
    build_pattern,
    filter_fresh_patterns,
)


class DojiStrategy(BaseStrategy):

    CATEGORY = "Indecision"

    DIRECTION = "DYNAMIC"

    ENABLED = True

    PRIORITY = 60

    MIN_SCORE = 55

    REQUIRES_TREND = True

    REQUIRES_VOLUME = False

    REQUIRES_VWAP = True

    REQUIRES_ADX = True

    PATTERN_NAME = "Doji"

    # =====================================================
    # Direction
    # =====================================================

    def direction(self):

        """
        Direction depends on trend.

        Downtrend -> BUY

        Uptrend -> SELL
        """

        return "DYNAMIC"

    # =====================================================
    # Weights
    # =====================================================

    def get_weights(self):

        return DOJI_WEIGHTS

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

            if not is_doji(candle):
                continue

            rng = candle_range(candle)

            if rng == 0:
                continue

            upper = upper_wick(candle)
            lower = lower_wick(candle)

            pattern_name = "Standard Doji"

            direction = None

            strength = 70

            if lower >= rng * 0.60 and upper <= rng * 0.10:

                pattern_name = "Dragonfly Doji"

                direction = "BUY"

                strength = 90

            elif upper >= rng * 0.60 and lower <= rng * 0.10:

                pattern_name = "Gravestone Doji"

                direction = "SELL"

                strength = 90

            elif upper >= rng * 0.35 and lower >= rng * 0.35:

                pattern_name = "Long Legged Doji"

                strength = 80

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

            else:

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

            stop = candle.low if direction == "BUY" else candle.high

            pattern = build_pattern(

                pattern=pattern_name,

                engine="doji",

                direction=direction,

                candle=candle,

                bars_ago=item["bars_ago"],

                strength=strength,

                confidence=None,

                entry=float(candle.close),

                stop=float(stop),

                pattern_type="single",

            )

            pattern["doji_type"] = pattern_name
            pattern["upper_wick"] = float(upper)
            pattern["lower_wick"] = float(lower)

            if strength < self.MIN_SCORE:
                continue

            patterns.append(pattern)

        return filter_fresh_patterns(patterns)