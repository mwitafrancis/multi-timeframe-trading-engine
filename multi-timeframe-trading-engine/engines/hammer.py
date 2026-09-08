"""
=========================================================
Professional Hammer Strategy
=========================================================

Bullish reversal strategy.

Requirements

1. Existing downtrend
2. Long lower wick
3. Small upper wick
4. Bullish or neutral body
5. Strong rejection
6. Close near candle high

=========================================================
"""

import pandas as pd

from config import (
HAMMER_WEIGHTS,
PATTERN_LOOKBACK,
) 

from engines.base_strategy import BaseStrategy


from utils.candle import (
    body_size,
    average_body,
    lower_wick,
    upper_wick,
    closes_near_high,
    is_bullish,
    is_neutral,
    short_term_downtrend,
    scan_single_meta,
    build_pattern,
    filter_fresh_patterns,
)

class HammerStrategy(BaseStrategy):
    
    PATTERN_NAME = "Hammer"

    CATEGORY = "Reversal"

    DIRECTION = "BUY"

    ENABLED = True


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

        return "BUY"

    # =====================================================
    # Strategy Weights
    # =====================================================

    def get_weights(self):

        return HAMMER_WEIGHTS

    # =====================================================
    # Pattern Detection
    # =====================================================

    def detect(self, df: pd.DataFrame):

        if len(df) < 20:
            return []
        patterns = []
        for item in scan_single_meta(
            df,
            PATTERN_LOOKBACK
        ):

            candle = item["candle"]


            # -------------------------------------------------
            # Existing Downtrend
            # -------------------------------------------------

            if not short_term_downtrend(
                df,
                bars_ago=item["bars_ago"],
            ):
                continue
            # -------------------------------------------------
            # Candle Direction
            # -------------------------------------------------

            if not (is_bullish(candle) or is_neutral(candle)):
                continue

            avg = average_body(
                df,
                bars_ago=item["bars_ago"],
            )

            body = body_size(candle)

            if body <= 0:
                continue

            lw = lower_wick(candle)
            uw = upper_wick(candle)

            # -------------------------------------------------
            # Long Lower Wick
            # -------------------------------------------------

            if lw < body * 2.0:
                continue

            # -------------------------------------------------
            # Small Upper Wick
            # -------------------------------------------------

            if uw > body * 0.30:
                continue

            # -------------------------------------------------
            # Close Near High
            # -------------------------------------------------

            if not closes_near_high(candle):
                continue

            # -------------------------------------------------
            # Pattern Strength
            # -------------------------------------------------

            strength = 70

            if lw >= body * 3:
                strength += 10

            if uw <= body * 0.20:
                strength += 5

            if closes_near_high(candle):
                strength += 5

            if body >= avg * 0.50:
                strength += 5

            strength += 5

            strength = min(strength, 100)

            # -------------------------------------------------
            # Return Pattern
            # -------------------------------------------------

            pattern = build_pattern(

                pattern=self.PATTERN_NAME,

                engine="hammer",

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