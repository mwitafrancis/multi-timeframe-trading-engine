"""
=========================================================
Professional Bullish Engulfing Strategy
=========================================================

Bullish reversal strategy based on the
Bullish Engulfing candlestick pattern.

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
    BULLISH_ENGULFING_WEIGHTS,
    PATTERN_LOOKBACK,
)

from engines.base_strategy import BaseStrategy

from utils.candle import (
    bullish_engulfing,
    body_size,
    average_body,
    short_term_downtrend,
    scan_pairs,         
    build_pattern,
    filter_fresh_patterns,
)


class BullishEngulfingStrategy(BaseStrategy):
    PATTERN_NAME = "Bullish Engulfing"

    CATEGORY = "Bullish Reversal"

    DIRECTION = "BUY"

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

        return "BUY"

    # =====================================================
    # Strategy Weights
    # =====================================================

    def get_weights(self):

        return BULLISH_ENGULFING_WEIGHTS

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

            # ----------------------------------------------
            # Previous Trend
            # ----------------------------------------------

            if not short_term_downtrend(
                df,
                bars_ago=item["bars_ago"],
            ):
                continue

            # ----------------------------------------------
            # Pattern
            # ----------------------------------------------

            if not bullish_engulfing(previous, current):
                continue

            # ----------------------------------------------
            # Candle Quality
            # ----------------------------------------------

            avg_body = average_body(df)

            current_body = body_size(current)
            previous_body = body_size(previous)

            body_larger = current_body > previous_body
            strong_body = current_body >= avg_body

            # ----------------------------------------------
            # Pattern Strength
            # ----------------------------------------------

            strength = 70

            if body_larger:
                strength += 10

            if strong_body:
                strength += 10

            strength += 10

            strength = min(strength, 100)

            # ----------------------------------------------
            # Return Pattern
            # ----------------------------------------------
            pattern = build_pattern(
                pattern=self.PATTERN_NAME,
                engine="bullish_engulfing",
                direction=self.direction(),
                candle=current,
                bars_ago=item["bars_ago"],
                strength=strength,
                confidence=None,
                entry=float(current.close),
                stop=float(min(previous.low, current.low)),
                pattern_type="double",
            )
            

            patterns.append(

                build_pattern(

                    pattern=self.PATTERN_NAME,

                    engine="bullish_engulfing",

                    direction=self.direction(),

                    candle=current,

                    bars_ago=item["bars_ago"],

                    strength=strength,

                    confidence=None,

                    entry=float(current.close),

                    stop=float(min(previous.low, current.low)),

                    pattern_type="double",

                )

            )
        return filter_fresh_patterns(patterns)