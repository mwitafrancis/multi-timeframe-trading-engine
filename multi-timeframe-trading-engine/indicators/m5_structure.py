"""M5 price-action reaction engine.

Uses CLOSED M5 candles only.  It intentionally avoids EMA/RSI/VWAP so that
structure confirmation is independent from the indicator layer.
"""
from indicators.signals import M5StructureSignal
import numpy as np

def _swing_high(df, i, left=2, right=2):
    if i < left or i + right >= len(df):
        return False
    h = float(df.high.iloc[i])
    return h > float(df.high.iloc[i-left:i].max()) and h >= float(df.high.iloc[i+1:i+right+1].max())


def _swing_low(df, i, left=2, right=2):
    if i < left or i + right >= len(df):
        return False
    l = float(df.low.iloc[i])
    return l < float(df.low.iloc[i-left:i].min()) and l <= float(df.low.iloc[i+1:i+right+1].min())


def _structure_bias(pivots):
    highs = [p for p in pivots if p[0] == "H"]
    lows = [p for p in pivots if p[0] == "L"]
    if len(highs) < 2 or len(lows) < 2:
        return "NEUTRAL"
    hh = highs[-1][1] > highs[-2][1]
    hl = lows[-1][1] > lows[-2][1]
    lh = highs[-1][1] < highs[-2][1]
    ll = lows[-1][1] < lows[-2][1]
    if hh and hl:
        return "BULLISH"
    if lh and ll:
        return "BEARISH"
    return "NEUTRAL"


def detect_m5_structure(df, atr, lookback=80, swing_left=2, swing_right=2,
                        sweep_lookback=12, sweep_max_age=2,
                        bos_score=35, choch_score=40, sweep_score=35,
                        displacement_score=15):
    if df is None or len(df) < max(20, swing_left + swing_right + 8):
        return M5StructureSignal(valid=False)
    source = df.iloc[:-1].copy() if len(df) > 1 else df.copy()
    if len(source) > lookback:
        source = source.iloc[-lookback:].copy()
    if len(source) < 15 or atr is None or not np.isfinite(atr) or atr <= 0:
        return M5StructureSignal(valid=False)

    pivots = []
    for i in range(swing_left, len(source) - swing_right):
        if _swing_high(source, i, swing_left, swing_right):
            pivots.append(("H", float(source.high.iloc[i]), i))
        if _swing_low(source, i, swing_left, swing_right):
            pivots.append(("L", float(source.low.iloc[i]), i))
    pivots.sort(key=lambda x: x[2])

    highs = [p for p in pivots if p[0] == "H"]
    lows = [p for p in pivots if p[0] == "L"]
    if not highs or not lows:
        return M5StructureSignal(valid=False)

    last_close = float(source.close.iloc[-1])
    prior_close = float(source.close.iloc[-2])
    latest_h = highs[-1]
    latest_l = lows[-1]

    bullish_bos = last_close > latest_h[1]
    bearish_bos = last_close < latest_l[1]

    prior_bias = _structure_bias(pivots[:-2] if len(pivots) > 2 else pivots)
    current_bias = _structure_bias(pivots)
    bullish_choch = bullish_bos and prior_bias == "BEARISH"
    bearish_choch = bearish_bos and prior_bias == "BULLISH"

    # Recent liquidity sweeps: break a prior swing and close back through it.
    swept_sell = swept_buy = False
    sweep_age = 999
    start = max(swing_left, len(source) - sweep_lookback)
    for i in range(start, len(source)):
        prior_lows = [p[1] for p in lows if p[2] < i]
        prior_highs = [p[1] for p in highs if p[2] < i]
        if prior_lows:
            level = max(prior_lows)
            if float(source.low.iloc[i]) < level and float(source.close.iloc[i]) > level:
                swept_sell = True
                sweep_age = len(source) - 1 - i
        if prior_highs:
            level = min(prior_highs)
            if float(source.high.iloc[i]) > level and float(source.close.iloc[i]) < level:
                swept_buy = True
                sweep_age = min(sweep_age, len(source) - 1 - i)

    # Displacement = meaningful body with directional close location.
    c = source.iloc[-1]
    body = abs(float(c.close) - float(c.open))
    rng = max(float(c.high) - float(c.low), 1e-12)
    displacement_bull = float(c.close) > float(c.open) and body >= atr * 0.75 and (c.close-c.low)/rng >= 0.65
    displacement_bear = float(c.close) < float(c.open) and body >= atr * 0.75 and (c.high-c.close)/rng >= 0.65

    buy = 0.0
    sell = 0.0
    event = "NONE"
    age = 999
    if bullish_choch:
        buy += choch_score; event = "BULLISH CHOCH"; age = 0
    elif bullish_bos:
        buy += bos_score; event = "BULLISH BOS"; age = 0
    if bearish_choch:
        sell += choch_score; event = "BEARISH CHOCH"; age = 0
    elif bearish_bos:
        sell += bos_score; event = "BEARISH BOS"; age = 0
    if swept_sell and sweep_age <= sweep_max_age:
        buy += sweep_score
        if event == "NONE": event = "SELL-SIDE SWEEP"
    if swept_buy and sweep_age <= sweep_max_age:
        sell += sweep_score
        if event == "NONE": event = "BUY-SIDE SWEEP"
    if displacement_bull:
        buy += displacement_score
    if displacement_bear:
        sell += displacement_score

    return M5StructureSignal(
        valid=True,
        bullish_bos=bullish_bos,
        bearish_bos=bearish_bos,
        bullish_choch=bullish_choch,
        bearish_choch=bearish_choch,
        swept_sell_side=swept_sell and sweep_age <= sweep_max_age,
        swept_buy_side=swept_buy and sweep_age <= sweep_max_age,
        displacement_bullish=displacement_bull,
        displacement_bearish=displacement_bear,
        score_buy=min(100.0, buy),
        score_sell=min(100.0, sell),
        last_event=event,
        event_age=age,
        sweep_age=sweep_age,
        swing_high=latest_h[1],
        swing_low=latest_l[1],
    )
