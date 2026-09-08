"""
=========================================================
Professional Pin Bar Strategy
=========================================================

Professional Pin Bar Detection

Bullish Pin Bar
---------------
1. Existing downtrend
2. Long lower wick
3. Small body
4. Small upper wick
5. Close near high

Bearish Pin Bar
---------------
1. Existing uptrend
2. Long upper wick
3. Small body
4. Small lower wick
5. Close near low

=========================================================
"""

import pandas as pd

from config import (
    PIN_BAR_WEIGHTS,
    PATTERN_LOOKBACK,
)

from engines.base_strategy import BaseStrategy

from utils.candle import (
    body_size,
    average_body,
    upper_wick,
    lower_wick,
    closes_near_high,
    closes_near_low,
    short_term_downtrend,
    short_term_uptrend,
    scan_single_meta,
    build_pattern,
    filter_fresh_patterns,
)


class PinBarStrategy(BaseStrategy):

    PATTERN_NAME = "Pin Bar"

    CATEGORY = "Reversal"

    DIRECTION = "DYNAMIC"

    ENABLED = True

    PRIORITY = 89

    MIN_SCORE = 60

    REQUIRES_TREND = True

    REQUIRES_VOLUME = True

    REQUIRES_VWAP = True

    REQUIRES_ADX = False
    REQUIRES_RSI = True

    def direction(self):
        return "BUY"

    def get_weights(self):
        return PIN_BAR_WEIGHTS

    def detect(self, df: pd.DataFrame):

        if len(df) < 20:
            return []

        patterns = []

        for item in scan_single_meta(
            df,
            PATTERN_LOOKBACK,
        ):

            candle = item["candle"]

            avg = average_body(
                df,
                bars_ago=item["bars_ago"],
            )

            body = body_size(candle)

            if body <= 0:
                continue

            upper = upper_wick(candle)
            lower = lower_wick(candle)

            # Small body
            if body > avg * 0.60:
                continue

            # =====================================================
            # Bullish Pin Bar
            # =====================================================

            if short_term_downtrend(
                df,
                bars_ago=item["bars_ago"],
            ):

                if (
                    lower >= body * 2.5
                    and upper <= body * 0.40
                    and closes_near_high(candle)
                ):

                    strength = 70

                    if lower >= body * 3:
                        strength += 10

                    if upper <= body * 0.20:
                        strength += 5

                    if body <= avg * 0.40:
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

                        engine="pin_bar",

                        direction="BUY",

                        candle=candle,

                        bars_ago=item["bars_ago"],

                        strength=strength,

                        confidence=None,

                        entry=float(candle.close),

                        stop=float(candle.low),

                        pattern_type="single",

                    )

                    pattern["pinbar_type"] = "bullish"
                    pattern["upper_wick"] = float(upper)
                    pattern["lower_wick"] = float(lower)

                    if strength >= self.MIN_SCORE:
                        patterns.append(pattern)

            # =====================================================
            # Bearish Pin Bar
            # =====================================================

            elif short_term_uptrend(
                df,
                bars_ago=item["bars_ago"],
            ):

                if (
                    upper >= body * 2.5
                    and lower <= body * 0.40
                    and closes_near_low(candle)
                ):

                    strength = 70

                    if upper >= body * 3:
                        strength += 10

                    if lower <= body * 0.20:
                        strength += 5

                    if body <= avg * 0.40:
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

                        engine="pin_bar",

                        direction="SELL",

                        candle=candle,

                        bars_ago=item["bars_ago"],

                        strength=strength,

                        confidence=None,

                        entry=float(candle.close),

                        stop=float(candle.high),

                        pattern_type="single",

                    )

                    pattern["pinbar_type"] = "bearish"
                    pattern["upper_wick"] = float(upper)
                    pattern["lower_wick"] = float(lower)

                    if strength >= self.MIN_SCORE:
                        patterns.append(pattern)

        return filter_fresh_patterns(patterns)