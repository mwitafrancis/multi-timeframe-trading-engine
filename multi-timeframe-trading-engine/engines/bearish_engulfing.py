"""
=========================================================
Professional Bearish Engulfing Strategy
=========================================================

Bearish reversal strategy based on the
Bearish Engulfing candlestick pattern.

Workflow

Pattern Detection
        ↓
BaseStrategy Confirmation
        ↓
TradeSignal

=========================================================
"""

import pandas as pd

from config import (
    BEARISH_ENGULFING_WEIGHTS,
    PATTERN_LOOKBACK,
)

from engines.base_strategy import BaseStrategy



from utils.candle import (
    bearish_engulfing,
    body_size,
    average_body,
    short_term_uptrend,
    scan_pairs,
    build_pattern,
)


class BearishEngulfingStrategy(BaseStrategy):
    PATTERN_NAME = "Bearish Engulfing"

    CATEGORY = "Bearish Reversal"

    DIRECTION = "SELL"

    ENABLED = True

    PRIORITY = 90

    MIN_SCORE = 60

    REQUIRES_TREND = True

    REQUIRES_VOLUME = True

    REQUIRES_VWAP = True

    REQUIRES_ADX = True


    # =====================================================
    # Direction
    # =====================================================

    def direction(self):

        return "SELL"

    # =====================================================
    # Strategy Weights
    # =====================================================

    def get_weights(self):

        return BEARISH_ENGULFING_WEIGHTS

    # =====================================================
    # Pattern Detection
    # =====================================================

    def detect(self, df: pd.DataFrame):

        if len(df) < 20:
               return []

        patterns = []

        for item in scan_pairs(df, PATTERN_LOOKBACK):

            previous = item["previous"]
            current = item["current"]

            # -------------------------------------------------
            # Previous Trend
            # -------------------------------------------------

            if not short_term_uptrend(
                df,
                bars_ago=item["bars_ago"],
            ):
                continue

            # -------------------------------------------------
            # Pattern
            # -------------------------------------------------

            if not bearish_engulfing(previous, current):
                continue

            # -------------------------------------------------
            # Candle Quality
            # -------------------------------------------------

            avg_body = average_body(df)

            current_body = body_size(current)
            previous_body = body_size(previous)

            body_larger = current_body > previous_body

            strong_body = current_body >= avg_body

            # -------------------------------------------------
            # Pattern Strength
            # -------------------------------------------------

            strength = 70

            if body_larger:
                strength += 10

            if strong_body:
                strength += 10

            if current_body >= previous_body * 1.2:
                strength += 10

        
            strength += 10

            strength = min(strength, 100)

            # -------------------------------------------------
            # Return Pattern
            # -------------------------------------------------
           
            pattern = build_pattern(

                pattern=self.PATTERN_NAME,

                engine="bearish_engulfing",

                direction=self.direction(),

                candle=current,

                bars_ago=item["bars_ago"],

                strength=strength,

                confidence=None,

                entry=float(current.close),

                stop=float(max(previous.high, current.high)),

                pattern_type="double",

            )

            patterns.append(

                build_pattern(

                    pattern=self.PATTERN_NAME,

                    engine="bearish_engulfing",

                    direction=self.direction(),

                    candle=current,

                    bars_ago=item["bars_ago"],

                    strength=strength,

                    confidence=None,

                    entry=float(current.close),

                    stop=float(max(previous.high, current.high)),

                    pattern_type="double",

                )

            )
        return patterns