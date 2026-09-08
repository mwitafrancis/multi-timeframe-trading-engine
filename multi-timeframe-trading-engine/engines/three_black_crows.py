"""
=========================================================
Professional Three Black Crows Strategy
=========================================================

Bearish reversal / continuation strategy.

Requirements

1. Existing uptrend
2. Three consecutive bearish candles
3. Each candle closes below previous close
4. Each candle opens inside previous body
5. Small lower wicks
6. Strong candle bodies

=========================================================
"""

import pandas as pd

from engines.base_strategy import BaseStrategy

from indicators.signals import PatternSignal

from config import (
    THREE_BLACK_CROWS_WEIGHTS,
    PATTERN_LOOKBACK,
)

from utils.candle import (
    consecutive_bearish,
    short_term_uptrend,
    body_size,
    average_body,
    lower_wick,
    scan_triples,
    build_pattern,
    filter_fresh_patterns,
)


class ThreeBlackCrowsStrategy(BaseStrategy):

    CATEGORY = "Bearish Continuation"

    DIRECTION = "SELL"

    ENABLED = True

    PRIORITY = 97

    MIN_SCORE = 80

    REQUIRES_TREND = True

    REQUIRES_VOLUME = True

    REQUIRES_VWAP = True

    REQUIRES_ADX = True

    PATTERN_NAME = "Three Black Crows"

    # =====================================================
    # Direction
    # =====================================================

    def direction(self):

        return "SELL"

    # =====================================================
    # Strategy Weights
    # =====================================================

    def get_weights(self):

        return THREE_BLACK_CROWS_WEIGHTS

    # =====================================================
    # Pattern Detection
    # =====================================================

    def detect(self, df: pd.DataFrame):

        if len(df) < 20:
            return []

        patterns = []

        for item in scan_triples(
            df,
            PATTERN_LOOKBACK,
        ):

            c1 = item["first"]
            c2 = item["second"]
            c3 = item["third"]

            # -------------------------------------------------
            # Previous Trend
            # -------------------------------------------------

            if not short_term_uptrend(
                df,
                bars_ago=item["bars_ago"],
            ):
                continue

            # -------------------------------------------------
            # Three Bearish Candles
            # -------------------------------------------------

            if not consecutive_bearish(
                df,
                count=3,
                bars_ago=item["bars_ago"],
            ):
                continue

            # -------------------------------------------------
            # Lower Closes
            # -------------------------------------------------

            closes_lower = (

                c2.close < c1.close

                and

                c3.close < c2.close

            )

            if not closes_lower:
                continue

            # -------------------------------------------------
            # Opens Inside Previous Body
            # -------------------------------------------------

            open_inside = (

                c2.open >= min(c1.open, c1.close)

                and

                c2.open <= max(c1.open, c1.close)

                and

                c3.open >= min(c2.open, c2.close)

                and

                c3.open <= max(c2.open, c2.close)

            )

            if not open_inside:
                continue

            # -------------------------------------------------
            # Strong Bodies
            # -------------------------------------------------

            avg = average_body(
                df,
                bars_ago=item["bars_ago"],
            )

            bodies = [
                body_size(c1),
                body_size(c2),
                body_size(c3),
            ]

            if min(bodies) < avg * 0.80:
                continue

            # -------------------------------------------------
            # Small Lower Wicks
            # -------------------------------------------------

            for candle in (c1, c2, c3):

                if lower_wick(candle) > body_size(candle) * 0.40:
                    break

            else:

                # -------------------------------------------------
                # Pattern Strength
                # -------------------------------------------------

                strength = 70

                if closes_lower:
                    strength += 5

                if open_inside:
                    strength += 5

                if min(bodies) >= avg:
                    strength += 5

                if max(bodies) > avg * 1.5:
                    strength += 5

                if body_size(c3) > body_size(c2):
                    strength += 3

                if body_size(c2) > body_size(c1):
                    strength += 2

                if short_term_uptrend(
                    df,
                    bars_ago=item["bars_ago"],
                ):
                    strength += 5

                strength = min(strength, 100)

                pattern = build_pattern(

                    pattern=self.PATTERN_NAME,

                    engine="three_black_crows",

                    direction=self.direction(),

                    candle=c3,

                    bars_ago=item["bars_ago"],

                    strength=strength,

                    confidence=None,

                    entry=float(c3.close),

                    stop=float(max(
                        c1.high,
                        c2.high,
                        c3.high,
                    )),

                    pattern_type="triple",

                )

                pattern["body_average"] = avg
                pattern["largest_body"] = max(bodies)

                if strength < self.MIN_SCORE:
                    continue

                patterns.append(pattern)

        return filter_fresh_patterns(patterns)