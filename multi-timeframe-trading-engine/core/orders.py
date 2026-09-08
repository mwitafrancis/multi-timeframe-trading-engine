"""MT5 order execution with live-price and broker-safety validation."""

import MetaTrader5 as mt5

from config import MAGIC_NUMBER, ORDER_COMMENT
from core.market import get_ask, get_bid, get_spread


def _normalize_price(value, digits):
    return round(float(value), int(digits))


def _normalize_volume(volume, info):
    step = float(info.volume_step or info.volume_min)
    if step <= 0:
        return None
    volume = max(float(info.volume_min), min(float(volume), float(info.volume_max)))
    steps = int(volume / step)  # floor so risk is never increased by rounding up
    normalized = steps * step
    if normalized < info.volume_min:
        normalized = info.volume_min
    return round(normalized, 8)


def _filling_modes(info):
    """Try the broker's advertised mode first, then common fallbacks."""
    modes = []
    advertised = getattr(info, "filling_mode", None)
    if advertised is not None:
        modes.append(advertised)
    for mode in (
        mt5.ORDER_FILLING_IOC,
        mt5.ORDER_FILLING_RETURN,
        mt5.ORDER_FILLING_FOK,
    ):
        if mode not in modes:
            modes.append(mode)
    return modes


def prepare_order_levels(signal):
    """Rebuild entry, SL and TP from the live executable price."""
    info = mt5.symbol_info(signal.symbol)
    if info is None:
        print(f"{signal.symbol}: symbol info unavailable")
        return None

    price = get_ask(signal.symbol) if signal.direction == "BUY" else get_bid(signal.symbol)
    if price is None or price <= 0:
        print(f"{signal.symbol}: live price unavailable")
        return None

    original_risk = abs(float(signal.entry) - float(signal.stop_loss))
    if original_risk <= 0:
        print(f"{signal.pattern}: invalid original stop distance")
        return None

    original_reward = abs(float(signal.take_profit) - float(signal.entry)) if signal.take_profit else 0.0
    rr = original_reward / original_risk if original_risk > 0 else 0.0
    if rr <= 0:
        print(f"{signal.pattern}: invalid original risk/reward")
        return None

    min_distance = max(
        float(getattr(info, "trade_stops_level", 0)) * float(info.point),
        float(getattr(info, "trade_freeze_level", 0)) * float(info.point),
    )
    # Small point buffer protects against boundary rounding/requotes.
    min_distance += 2 * float(info.point)
    risk_distance = max(original_risk, min_distance)
    reward_distance = risk_distance * rr

    if signal.direction == "BUY":
        stop_loss = price - risk_distance
        take_profit = price + reward_distance
    else:
        stop_loss = price + risk_distance
        take_profit = price - reward_distance

    price = _normalize_price(price, info.digits)
    stop_loss = _normalize_price(stop_loss, info.digits)
    take_profit = _normalize_price(take_profit, info.digits)

    # Final directional validation after rounding.
    if signal.direction == "BUY":
        valid = stop_loss < price and take_profit > price
    else:
        valid = stop_loss > price and take_profit < price
    if not valid:
        print(f"{signal.pattern}: invalid order levels after normalization")
        return None

    return price, stop_loss, take_profit, info


def execute_trade(signal):
    if signal.direction not in ("BUY", "SELL"):
        return False

    levels = prepare_order_levels(signal)
    if levels is None:
        return False

    price, stop_loss, take_profit, info = levels
    volume = _normalize_volume(signal.lot_size, info)
    if volume is None or volume <= 0:
        print(f"{signal.pattern}: invalid normalized volume")
        return False

    comment = (signal.pattern.replace(" ", "_").replace("|", "").replace("/", ""))[:21]
    order_type = mt5.ORDER_TYPE_BUY if signal.direction == "BUY" else mt5.ORDER_TYPE_SELL

    print("=" * 50)
    print(signal.symbol)
    print(f"LIVE ENTRY : {price}")
    print(f"SL         : {stop_loss}")
    print(f"TP         : {take_profit}")
    print(f"VOLUME     : {volume}")
    print(f"SPREAD     : {get_spread(signal.symbol)} points")
    print("=" * 50)

    base_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": signal.symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "sl": stop_loss,
        "tp": take_profit,
        "deviation": 20,
        "magic": MAGIC_NUMBER,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
    }

    last_result = None
    for filling_mode in _filling_modes(info):
        request = dict(base_request)
        request["type_filling"] = filling_mode
        result = mt5.order_send(request)
        last_result = result
        if result is not None and result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"{signal.direction} EXECUTED {signal.symbol}")
            # Persist actual order levels so later managers use executable values.
            signal.entry = price
            signal.stop_loss = stop_loss
            signal.take_profit = take_profit
            signal.lot_size = volume
            return True
        if result is not None:
            print(f"Order attempt failed: retcode={result.retcode} comment={result.comment}")
        else:
            print(f"Order attempt failed: {mt5.last_error()}")

    print(f"{signal.direction} FAILED: {last_result}")
    return False


def buy(signal):
    signal.direction = "BUY"
    return execute_trade(signal)


def sell(signal):
    signal.direction = "SELL"
    return execute_trade(signal)
