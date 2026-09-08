"""Volatility-normalised supply/demand zones.

Zones are built from a swing + base/origin + displacement rather than treating
an arbitrary whole swing candle as an institutional zone.  All input candles
are assumed to be CLOSED candles; the market-state builder enforces this for
M15 location analysis.
"""
import numpy as np
from config import *
from indicators.signals import Zone, SupplyDemandSignal


def _swing_high(df, i):
    if i < ZONE_SWING or i + ZONE_SWING >= len(df): return False
    return float(df.high.iloc[i]) > float(df.high.iloc[i-ZONE_SWING:i].max()) and float(df.high.iloc[i]) >= float(df.high.iloc[i+1:i+ZONE_SWING+1].max())


def _swing_low(df, i):
    if i < ZONE_SWING or i + ZONE_SWING >= len(df): return False
    return float(df.low.iloc[i]) < float(df.low.iloc[i-ZONE_SWING:i].min()) and float(df.low.iloc[i]) <= float(df.low.iloc[i+1:i+ZONE_SWING+1].min())


def _body(row): return abs(float(row.close) - float(row.open))


def _distinct_retests(df, high, low, start, atr):
    """Count separate visits, not every overlapping candle."""
    count = 0; last_touch = -1; inside = False
    min_pen = atr * RETEST_PENETRATION_ATR
    for i in range(max(0, start), len(df)):
        h, l = float(df.high.iloc[i]), float(df.low.iloc[i])
        penetration = min(h, high) - max(l, low)
        touched = penetration >= min_pen
        if touched and not inside:
            count += 1; last_touch = i
        inside = touched
    return count, last_touch


def _base_for_swing(df, swing_i, direction):
    # Search backwards for the last opposite/neutral candle: this is the
    # origin/base from which the displacement departed.
    end = max(0, swing_i - 1)
    start = max(0, swing_i - ZONE_BASE_LOOKBACK)
    for j in range(end, start - 1, -1):
        o, c = float(df.open.iloc[j]), float(df.close.iloc[j])
        if direction == "DEMAND" and c <= o:
            return j
        if direction == "SUPPLY" and c >= o:
            return j
    return swing_i


def _departure(df, base_i, direction, atr):
    end = min(len(df), base_i + ZONE_DEPARTURE_LOOKAHEAD + 1)
    if end <= base_i + 1: return 0.0
    if direction == "DEMAND":
        return (float(df.high.iloc[base_i+1:end].max()) - float(df.high.iloc[base_i])) / atr
    return (float(df.low.iloc[base_i]) - float(df.low.iloc[base_i+1:end].min())) / atr


def _zone_bounds(row, direction):
    o, c, h, l = map(float, (row.open, row.close, row.high, row.low))
    if direction == "DEMAND":
        # Body + lower wick: narrower than the full candle while retaining the rejection tail.
        return max(o, c), l
    return h, min(o, c)


def _invalidated(df, high, low, start, direction, atr):
    # A wick through a zone is not enough to invalidate it; require a CLOSED
    # candle to close materially beyond the origin.
    future = df.iloc[start:]
    if future.empty: return False
    if direction == "DEMAND":
        return bool((future.close < low - atr * ZONE_INVALIDATION_BUFFER_ATR).any())
    return bool((future.close > high + atr * ZONE_INVALIDATION_BUFFER_ATR).any())


def _score_zone(body_atr, departure, retests, dist_atr, width_atr, age_bars):
    body_component = min(20.0, body_atr * 12.0)
    departure_component = min(30.0, max(0.0, departure) * 8.0)
    freshness = {0: 20.0, 1: 14.0, 2: 8.0}.get(retests, 0.0)
    proximity = max(0.0, 20.0 - min(20.0, dist_atr * 20.0))
    width_penalty = max(0.0, width_atr - 0.8) * 6.0
    age_penalty = min(8.0, age_bars * 0.05)
    return max(0.0, min(100.0, body_component + departure_component + freshness + proximity - width_penalty - age_penalty))


def _best_zone(df, atr, direction):
    price = float(df.close.iloc[-1])
    best = None; best_score = -1
    for i in range(ZONE_SWING, len(df) - ZONE_SWING):
        if direction == "DEMAND" and not _swing_low(df, i): continue
        if direction == "SUPPLY" and not _swing_high(df, i): continue
        base_i = _base_for_swing(df, i, direction)
        row = df.iloc[base_i]
        body_atr = _body(row) / atr
        high, low = _zone_bounds(row, direction)
        width_atr = (high - low) / atr
        if width_atr < ZONE_MIN_SIZE_ATR * 0.5 or width_atr > ZONE_MAX_SIZE_ATR: continue
        dep = _departure(df, base_i, direction, atr)
        if dep < ZONE_MIN_DEPARTURE_ATR: continue
        # A displacement candle should actually leave the base.
        end = min(len(df), base_i + ZONE_DEPARTURE_LOOKAHEAD + 1)
        if direction == "DEMAND":
            displacement = float(df.high.iloc[base_i+1:end].max()) > high + atr * ZONE_DISPLACEMENT_BUFFER_ATR
        else:
            displacement = float(df.low.iloc[base_i+1:end].min()) < low - atr * ZONE_DISPLACEMENT_BUFFER_ATR
        if not displacement: continue
        if _invalidated(df, high, low, base_i + 1, direction, atr): continue
        retest_count, last_touch = _distinct_retests(df, high, low, base_i + 1, atr)
        current = df.iloc[-1]
        current_penetration = min(float(current.high), high) - max(float(current.low), low)
        current_touched = current_penetration >= atr * RETEST_PENETRATION_ATR
        # The current candle is an interaction, not an already-consumed retest.
        prior_retests = max(0, retest_count - (1 if current_touched and last_touch == len(df)-1 else 0))
        if prior_retests > MAX_RETESTS: continue
        retest_count = prior_retests
        dist = 0.0 if low <= price <= high else min(abs(price-low), abs(price-high))
        dist_atr = dist / atr
        if dist_atr > ZONE_DISTANCE_ATR: continue
        score = _score_zone(body_atr, dep, retest_count, dist_atr, width_atr, len(df)-base_i)
        if score > best_score:
            best_score = score
            best = Zone(high=high, low=low, midpoint=(high+low)/2.0,
                        fresh=retest_count == 0, retests=retest_count,
                        strength=int(round(score)), touched=current_touched,
                        zone_type=direction, distance=dist, bar_index=base_i,
                        timestamp=df.index[base_i], last_touch=last_touch,
                        score=score, distance_score=max(0.0, 100.0-dist_atr*100.0),
                        origin_index=base_i, departure_atr=dep, base_type="BASE",
                        last_retest_index=last_touch)
    return best


def detect_supply_demand(df, atr, already_closed=False):
    if df is None or len(df) < 30 or atr is None or not np.isfinite(atr) or atr <= 0:
        return SupplyDemandSignal(None, None, False, False, float("inf"), float("inf"), 0)
    source = df.copy() if already_closed else (df.iloc[:-1].copy() if USE_CLOSED_CANDLES_ONLY and len(df) > 1 else df.copy())
    if len(source) > ZONE_LOOKBACK: source = source.iloc[-ZONE_LOOKBACK:].copy()
    demand = _best_zone(source, atr, "DEMAND")
    supply = _best_zone(source, atr, "SUPPLY")
    price = float(source.close.iloc[-1])
    dd = float("inf") if demand is None else demand.distance
    sd = float("inf") if supply is None else supply.distance
    near_demand = bool(demand and dd <= atr * ZONE_NEAR_DISTANCE_ATR)
    near_supply = bool(supply and sd <= atr * ZONE_NEAR_DISTANCE_ATR)
    score = max((demand.strength if near_demand else 0), (supply.strength if near_supply else 0))
    if PRINT_SUPPLY or PRINT_DEMAND:
        if PRINT_DEMAND:
            print(f"Demand: {demand}")
        if PRINT_SUPPLY:
            print(f"Supply: {supply}")
    return SupplyDemandSignal(supply, demand, near_supply, near_demand, sd, dd, int(score))
