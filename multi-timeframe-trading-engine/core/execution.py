"""Execution engine: exposure checks, spread checks and safe order dispatch."""

from datetime import datetime, timedelta
import MetaTrader5 as mt5

from config import (
    MAX_OPEN_TRADES_PER_SYMBOL, MAX_TOTAL_OPEN_TRADES,
    STRATEGY_COOLDOWNS, ALLOW_OPPOSITE_TRADES,
    MAX_SPREAD_POINTS_DEFAULT, MAX_SPREAD_POINTS_BY_SYMBOL,
)
from core.orders import prepare_order_levels, execute_trade
from core.market import get_spread
from core.risk import risk_manager

_last_trade_time = {}


class ExecutionEngine:
    def execute(self, signal):
        if not signal.valid:
            return False
        if not self.can_execute(signal):
            return False
        if not self.check_spread(signal):
            return False

        # Rebase the signal on the actual executable market price before
        # validating RR and calculating a risk-based position size.
        levels = prepare_order_levels(signal)
        if levels is None:
            return False
        entry, stop_loss, take_profit, _ = levels
        signal.entry = entry
        signal.stop_loss = stop_loss
        signal.take_profit = take_profit
        signal.risk_reward = risk_manager.calculate_rr(signal)

        if not risk_manager.validate_trade(signal):
            print(f"{signal.pattern}: Risk validation failed.")
            return False

        signal.lot_size = risk_manager.calculate_lot_size(signal)
        if signal.lot_size <= 0:
            print(f"{signal.pattern}: invalid lot size.")
            return False

        result = execute_trade(signal)
        if result:
            _last_trade_time[(signal.pattern, signal.symbol)] = datetime.now()
        return result

    def can_execute(self, signal):
        return (
            self.check_symbol_limit(signal)
            and self.check_total_limit()
            and self.check_strategy_cooldown(signal)
            and self.check_opposite_trade(signal)
        )

    def check_spread(self, signal):
        spread = get_spread(signal.symbol)
        if spread is None:
            print(f"{signal.symbol}: spread unavailable")
            return False
        limit = MAX_SPREAD_POINTS_BY_SYMBOL.get(signal.symbol, MAX_SPREAD_POINTS_DEFAULT)
        if spread > limit:
            print(f"{signal.symbol}: spread too high ({spread:.1f} > {limit} points)")
            return False
        return True

    def check_symbol_limit(self, signal):
        positions = mt5.positions_get(symbol=signal.symbol)
        return positions is None or len(positions) < MAX_OPEN_TRADES_PER_SYMBOL

    def check_total_limit(self):
        positions = mt5.positions_get()
        return positions is None or len(positions) < MAX_TOTAL_OPEN_TRADES

    def check_strategy_cooldown(self, signal):
        minutes = STRATEGY_COOLDOWNS.get(signal.pattern, 0)
        if minutes == 0:
            return True
        key = (signal.pattern, signal.symbol)
        if key not in _last_trade_time:
            return True
        return datetime.now() - _last_trade_time[key] >= timedelta(minutes=minutes)

    def check_opposite_trade(self, signal):
        if ALLOW_OPPOSITE_TRADES:
            return True
        positions = mt5.positions_get(symbol=signal.symbol)
        if positions is None:
            return True
        for pos in positions:
            if signal.direction == "BUY" and pos.type == mt5.POSITION_TYPE_SELL:
                return False
            if signal.direction == "SELL" and pos.type == mt5.POSITION_TYPE_BUY:
                return False
        return True
