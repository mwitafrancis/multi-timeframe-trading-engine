"""Directional M15 location scoring.

Location is contextual, not a trade trigger.  It answers two questions:
1) Is price at a meaningful area for this direction?
2) Has the area actually been touched, rather than merely being nearby?
"""
from config import *
from indicators.signals import LocationSignal


def _empty(reason):
    return LocationSignal(0, [reason], False, False, False, False, False, False,
                           False, False, False, False, 0.0, False, False)


def _touch(zone, atr):
    return bool(zone and zone.distance <= atr * 0.001)  # distance is 0 when inside zone


def calculate_location(market, sr, supply_demand, range_signal,
                        liquidity=None, fvg=None, bias_direction=None):
    if market is None: return _empty("No Market")
    if sr is None or supply_demand is None or range_signal is None: return _empty("Missing Data")

    state = "STRONG_BULL" if bias_direction == "BUY" else "STRONG_BEAR" if bias_direction == "SELL" else market.state
    buy_context = bias_direction == "BUY" or state in ("STRONG_BULL", "WEAK_BULL")
    sell_context = bias_direction == "SELL" or state in ("STRONG_BEAR", "WEAK_BEAR")

    demand = supply_demand.demand
    supply = supply_demand.supply
    support = sr.support
    resistance = sr.resistance

    # Supply/demand detector already applies the ATR proximity rule.
    near_demand = bool(supply_demand.near_demand)
    near_supply = bool(supply_demand.near_supply)
    near_support = bool(sr.near_support)
    near_resistance = bool(sr.near_resistance)

    demand_touched = bool(demand and getattr(demand, "touched", False))
    supply_touched = bool(supply and getattr(supply, "touched", False))
    support_touched = bool(support and getattr(support, "touched", False))
    resistance_touched = bool(resistance and getattr(resistance, "touched", False))

    near_range_high = bool(range_signal.valid and range_signal.near_top)
    near_range_low = bool(range_signal.valid and range_signal.near_bottom)

    near_buy_liq = bool(liquidity and liquidity.near_buy_side)
    near_sell_liq = bool(liquidity and liquidity.near_sell_side)
    swept_buy = bool(liquidity and liquidity.swept_buy_side)
    swept_sell = bool(liquidity and liquidity.swept_sell_side)
    near_bull_fvg = bool(fvg and fvg.near_bullish)
    near_bear_fvg = bool(fvg and fvg.near_bearish)

    reasons=[]; score=0.0

    # Directional scoring.  Opposite-side liquidity is deliberately ignored.
    if buy_context:
        primary = near_demand
        if primary:
            score += LOC_W_PRIMARY_ZONE * (0.75 + 0.25 * (demand.strength/100.0))
            reasons.append("Demand")
            if demand.fresh: score += LOC_W_FRESH; reasons.append("Fresh Demand")
        if near_support:
            score += LOC_W_SR * (0.75 + 0.25 * (support.strength/100.0)); reasons.append("Support")
        if near_bull_fvg:
            score += LOC_W_FVG; reasons.append("Bullish FVG")
        if near_sell_liq:
            score += LOC_W_LIQUIDITY_NEAR; reasons.append("Sell-side Liquidity")
        if swept_sell:
            score += LOC_W_LIQUIDITY_SWEEP; reasons.append("Sell-side Sweep")
        if near_range_low:
            score += LOC_W_RANGE_EDGE; reasons.append("Range Low")
        if (near_demand and near_support) or (near_demand and near_bull_fvg) or (near_support and near_bull_fvg):
            score += LOC_W_CONFLUENCE; reasons.append("Confluence")
        if demand_touched or support_touched or (fvg and fvg.bullish and getattr(fvg.bullish, "touched", False)):
            score += LOC_W_TOUCH; reasons.append("Location Touched")
    elif sell_context:
        primary = near_supply
        if primary:
            score += LOC_W_PRIMARY_ZONE * (0.75 + 0.25 * (supply.strength/100.0))
            reasons.append("Supply")
            if supply.fresh: score += LOC_W_FRESH; reasons.append("Fresh Supply")
        if near_resistance:
            score += LOC_W_SR * (0.75 + 0.25 * (resistance.strength/100.0)); reasons.append("Resistance")
        if near_bear_fvg:
            score += LOC_W_FVG; reasons.append("Bearish FVG")
        if near_buy_liq:
            score += LOC_W_LIQUIDITY_NEAR; reasons.append("Buy-side Liquidity")
        if swept_buy:
            score += LOC_W_LIQUIDITY_SWEEP; reasons.append("Buy-side Sweep")
        if near_range_high:
            score += LOC_W_RANGE_EDGE; reasons.append("Range High")
        if (near_supply and near_resistance) or (near_supply and near_bear_fvg) or (near_resistance and near_bear_fvg):
            score += LOC_W_CONFLUENCE; reasons.append("Confluence")
        if supply_touched or resistance_touched or (fvg and fvg.bearish and getattr(fvg.bearish, "touched", False)):
            score += LOC_W_TOUCH; reasons.append("Location Touched")
    else:
        # Neutral H1: retain contextual scoring but do not manufacture a trade bias.
        if near_demand and near_range_low: score += 30; reasons += ["Demand", "Range Low"]
        if near_supply and near_range_high: score += 30; reasons += ["Supply", "Range High"]

    score = min(100, round(score))
    if not reasons: reasons=["Weak Location"]

    if PRINT_LOCATION:
        print("\n========== LOCATION ==========")
        print(f"Bias={bias_direction} State={state} Score={score}")
        print(f"Demand={near_demand} touched={demand_touched} | Supply={near_supply} touched={supply_touched}")
        print(f"Support={near_support} touched={support_touched} | Resistance={near_resistance} touched={resistance_touched}")
        print(f"SellLiq={near_sell_liq} swept={swept_sell} | BuyLiq={near_buy_liq} swept={swept_buy}")
        print(f"BullFVG={near_bull_fvg} | BearFVG={near_bear_fvg}")
        print("Reasons:", ", ".join(dict.fromkeys(reasons)))
        print("==============================")

    return LocationSignal(
        score=score, reason=list(dict.fromkeys(reasons)),
        near_support=near_support, near_resistance=near_resistance,
        near_supply=near_supply, near_demand=near_demand,
        near_range_high=near_range_high, near_range_low=near_range_low,
        near_buy_side_liquidity=near_buy_liq, near_sell_side_liquidity=near_sell_liq,
        swept_buy_side_liquidity=swept_buy, swept_sell_side_liquidity=swept_sell,
        liquidity_score=min(LOC_W_LIQUIDITY_NEAR + LOC_W_LIQUIDITY_SWEEP, float(liquidity.score) if liquidity else 0.0),
        near_bullish_fvg=near_bull_fvg, near_bearish_fvg=near_bear_fvg,
        demand_touched=demand_touched, supply_touched=supply_touched,
        support_touched=support_touched, resistance_touched=resistance_touched,
        bullish_location_touched=(demand_touched or support_touched or (fvg and fvg.bullish and getattr(fvg.bullish, "touched", False))),
        bearish_location_touched=(supply_touched or resistance_touched or (fvg and fvg.bearish and getattr(fvg.bearish, "touched", False))),
        support=support, resistance=resistance, supply=supply, demand=demand,
    )
