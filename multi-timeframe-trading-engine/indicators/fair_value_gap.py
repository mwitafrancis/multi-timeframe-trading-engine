"""Closed-candle Fair Value Gap detector.

A valid FVG is a three-candle imbalance with directional displacement.  The
currently forming candle is never used by the M15 location engine.
"""
import numpy as np
from config import *
from indicators.signals import FairValueGap, FVGSignal


def _distance_score(distance, atr):
    if atr is None or not np.isfinite(atr) or atr <= 0: return 0.0
    ratio = max(0.0, 1.0 - distance / (atr * FVG_MAX_DISTANCE_ATR))
    return round(ratio * 100.0, 2)


def _gap_filled(df, gap, start):
    for i in range(start, len(df)):
        lo, hi = float(df.low.iloc[i]), float(df.high.iloc[i])
        if gap.direction == "BULLISH" and lo <= gap.low:
            return True
        if gap.direction == "BEARISH" and hi >= gap.high:
            return True
    return False


def _displacement_ok(df, i, direction, atr):
    # Middle candle should show actual expansion, not a tiny three-candle gap.
    c = df.iloc[i-1]
    body = abs(float(c.close) - float(c.open))
    rng = max(float(c.high) - float(c.low), 1e-12)
    if body < atr * FVG_MIN_DISPLACEMENT_ATR: return False
    if direction == "BULLISH":
        return float(c.close) > float(c.open) and (float(c.close)-float(c.low))/rng >= 0.60
    return float(c.close) < float(c.open) and (float(c.high)-float(c.close))/rng >= 0.60


def _latest_gap(df, atr, direction):
    if df is None or len(df) < 5 or atr <= 0: return None
    price = float(df.close.iloc[-1])
    best = None; best_score = -1.0
    last_i = len(df) - 1
    for i in range(last_i, 2, -1):
        # i is the third candle; all three are closed.
        first, third = i-2, i
        if direction == "BULLISH":
            lower = float(df.high.iloc[first]); upper = float(df.low.iloc[third])
        else:
            lower = float(df.high.iloc[third]); upper = float(df.low.iloc[first])
        if upper <= lower: continue
        size = upper - lower
        if size < atr * FVG_MIN_SIZE_ATR: continue
        if not _displacement_ok(df, i, direction, atr): continue
        age = last_i - i
        if age > FVG_MAX_AGE_BARS: continue
        gap = FairValueGap(
            high=upper, low=lower, midpoint=(upper+lower)/2.0,
            direction=direction, fresh=True, filled=False,
            bar_index=i, timestamp=df.time.iloc[i] if "time" in df.columns else df.index[i], size=size,
        )
        gap.filled = _gap_filled(df, gap, i+1)
        gap.fresh = not gap.filled
        if FVG_REQUIRE_FRESH and not gap.fresh: continue
        latest = df.iloc[-1]
        gap.touched = (min(float(latest.high), upper) - max(float(latest.low), lower)) >= atr * 0.02
        gap.distance = 0.0 if lower <= price <= upper else min(abs(price-lower), abs(price-upper))
        if gap.distance > atr * FVG_MAX_DISTANCE_ATR: continue
        gap.distance_score = _distance_score(gap.distance, atr)
        size_score = min(100.0, size / atr * 100.0)
        fresh_score = 100.0 if gap.fresh else 0.0
        age_score = max(0.0, 100.0 - age * (100.0 / max(1, FVG_MAX_AGE_BARS)))
        total = (gap.distance_score * FVG_SCORE_WEIGHT_DISTANCE +
                 size_score * FVG_SCORE_WEIGHT_SIZE +
                 min(fresh_score, age_score) * FVG_SCORE_WEIGHT_FRESH)
        if total > best_score:
            best_score = total; best = gap
    return best


def detect_fair_value_gap(df, atr, already_closed=False):
    if not ENABLE_FVG or df is None or atr is None or not np.isfinite(atr) or atr <= 0 or len(df) < 5:
        return FVGSignal.invalid()
    source = df.copy() if already_closed else (df.iloc[:-1].copy() if USE_CLOSED_CANDLES_ONLY and len(df) > 1 else df.copy())
    bull = _latest_gap(source, atr, "BULLISH")
    bear = _latest_gap(source, atr, "BEARISH")
    near_bull = bool(bull and bull.distance <= atr * FVG_NEAR_DISTANCE_ATR)
    near_bear = bool(bear and bear.distance <= atr * FVG_NEAR_DISTANCE_ATR)
    score = max(bull.distance_score if near_bull else 0.0, bear.distance_score if near_bear else 0.0)
    if PRINT_FVG:
        print("\n========== FVG ==========")
        print("Bullish:", bull)
        print("Bearish:", bear)
        print(f"Near Bullish={near_bull} Near Bearish={near_bear} Score={score:.1f}")
        print("==========================")
    return FVGSignal(True, bull, bear, near_bull, near_bear, score)
