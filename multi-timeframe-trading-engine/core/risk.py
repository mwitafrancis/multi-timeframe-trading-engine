"""
=========================================================
Professional Risk Management Engine
=========================================================

Responsibilities
----------------
✓ Position sizing
✓ Risk/Reward calculation
✓ Daily loss protection
✓ Account risk protection
✓ Breakeven calculations
✓ Trailing stop calculations

This module NEVER detects trades.
It only evaluates and manages risk.

Author: francis
=========================================================
"""

import MetaTrader5 as mt5

from config import (
    RISK_MODE,
    FIXED_LOT_SIZE,
    RISK_PERCENT,
    MAX_ACCOUNT_RISK,
    MAX_DAILY_LOSS,
    MIN_RISK_REWARD,
    ENABLE_BREAKEVEN,
    BREAKEVEN_AT_R,
    ENABLE_TRAILING_STOP,
    TRAILING_AT_R,
    ENABLE_PARTIAL_CLOSE,
    PARTIAL_CLOSE_AT_R,
    PARTIAL_CLOSE_PERCENT,
    ENABLE_DYNAMIC_LOT,
    
    LOT_SCORE_LEVEL_1,
    LOT_SCORE_LEVEL_2,
    LOT_SCORE_LEVEL_3,

    LOT_MULTIPLIER_LEVEL_1,
    LOT_MULTIPLIER_LEVEL_2,
    LOT_MULTIPLIER_LEVEL_3,

    ENABLE_LOT_RR_FILTER,

    LOT_MIN_RR_LEVEL_1,
    LOT_MIN_RR_LEVEL_2,
    LOT_MIN_RR_LEVEL_3,

    MAX_DYNAMIC_LOT_MULTIPLIER,
)


class RiskManager:

    def __init__(self):
        pass

    # =====================================================
    # Position Size
    # =====================================================

    def calculate_lot_size(self, signal):

        # ------------------------------------
        # Base lot
        # ------------------------------------

        if RISK_MODE.lower() == "fixed":

            lot = FIXED_LOT_SIZE

        else:

            lot = self.percent_lot_size(signal)

        # ------------------------------------
        # Dynamic lot sizing
        # ------------------------------------

        if ENABLE_DYNAMIC_LOT:

            score = getattr(signal, "score", 0)

            rr = self.calculate_rr(signal)

            multiplier = 1.0

            if score >= LOT_SCORE_LEVEL_3:

                if (
                    not ENABLE_LOT_RR_FILTER
                    or
                    rr >= LOT_MIN_RR_LEVEL_3
                ):

                    multiplier = LOT_MULTIPLIER_LEVEL_3

            elif score >= LOT_SCORE_LEVEL_2:

                if (
                    not ENABLE_LOT_RR_FILTER
                    or
                    rr >= LOT_MIN_RR_LEVEL_2
                ):

                    multiplier = LOT_MULTIPLIER_LEVEL_2

            elif score >= LOT_SCORE_LEVEL_1:

                if (
                    not ENABLE_LOT_RR_FILTER
                    or
                    rr >= LOT_MIN_RR_LEVEL_1
                ):

                    multiplier = LOT_MULTIPLIER_LEVEL_1

            multiplier = min(
                multiplier,
                MAX_DYNAMIC_LOT_MULTIPLIER,
            )

            lot *= multiplier

        # ------------------------------------
        # Broker limits
        # ------------------------------------

        info = mt5.symbol_info(signal.symbol)

        if info is not None:

            lot = min(lot, info.volume_max)

            lot = max(lot, info.volume_min)

            step = info.volume_step

            lot = round(lot / step) * step

        return round(lot, 2)

    # =====================================================
    # Percent Risk Lot Size
    # =====================================================

    def percent_lot_size(self, signal):

        account = mt5.account_info()

        if account is None:
            return FIXED_LOT_SIZE

        info = mt5.symbol_info(signal.symbol)

        if info is None:
            return FIXED_LOT_SIZE

        risk_money = account.balance * (RISK_PERCENT / 100)

        stop_distance = abs(
            signal.entry -
            signal.stop_loss
        )

        if stop_distance <= 0:
            return FIXED_LOT_SIZE

        tick_value = info.trade_tick_value
        tick_size = info.trade_tick_size

        if tick_value <= 0 or tick_size <= 0:
            return FIXED_LOT_SIZE

        value_per_price = tick_value / tick_size

        lot = risk_money / (stop_distance * value_per_price)

        lot = max(info.volume_min, lot)
        lot = min(info.volume_max, lot)

        step = info.volume_step

        lot = round(lot / step) * step

        return round(lot, 2)

    # =====================================================
    # Risk Reward
    # =====================================================

    def calculate_rr(self, signal):

        if signal.take_profit is None:
            print("No Take Profit")
            return 0

        risk = abs(signal.entry - signal.stop_loss)
        reward = abs(signal.take_profit - signal.entry)

        print(f"Risk={risk}")
        print(f"Reward={reward}")

        if risk == 0:
            return 0

        rr = reward / risk

        print(f"RR={rr}")

        return rr

    # =====================================================
    # Validate RR
    # =====================================================

    def validate_rr(self, signal):

        rr = self.calculate_rr(signal)

        return rr >= MIN_RISK_REWARD

    # =====================================================
    # Daily Loss Protection
    # =====================================================

    def validate_daily_loss(self):

        account = mt5.account_info()

        if account is None:
            return False

        balance = account.balance
        equity = account.equity

        if balance <= 0:
            return False

        drawdown = (
            (balance - equity)
            / balance
        ) * 100

        return drawdown < MAX_DAILY_LOSS

    # =====================================================
    # Account Risk
    # =====================================================

    def validate_account_risk(self):

        account = mt5.account_info()

        if account is None:
            return False

        balance = account.balance
        equity = account.equity

        if balance <= 0:
            return False

        drawdown = (
            (balance - equity)
            / balance
        ) * 100

        return drawdown < MAX_ACCOUNT_RISK

    # =====================================================
    # Validate Trade
    # =====================================================

    def validate_trade(self, signal):

        rr = self.calculate_rr(signal)
        print(f"Risk Reward: {rr:.2f} (Minimum: {MIN_RISK_REWARD})")

        if not self.validate_rr(signal):
            print("❌ BLOCKED: Risk Reward too low")
            return False

        if not self.validate_daily_loss():
            print("❌ BLOCKED: Daily loss exceeded")
            return False

        if not self.validate_account_risk():
            print("❌ BLOCKED: Account drawdown exceeded")
            return False

        print("✅ Risk validation passed")
        return True

    # =====================================================
    # Breakeven Trigger
    # =====================================================

    def should_move_to_breakeven(
        self,
        current_rr,
    ):

        if not ENABLE_BREAKEVEN:
            return False

        return current_rr >= BREAKEVEN_AT_R

    # =====================================================
    # Trailing Stop Trigger
    # =====================================================

    def should_trail(
        self,
        current_rr,
    ):

        if not ENABLE_TRAILING_STOP:
            return False

        return current_rr >= TRAILING_AT_R

    # =====================================================
    # Partial Close Trigger
    # =====================================================

    def should_partial_close(
        self,
        current_rr,
    ):

        if not ENABLE_PARTIAL_CLOSE:
            return False

        return current_rr >= PARTIAL_CLOSE_AT_R

    # =====================================================
    # Partial Close Volume
    # =====================================================

    def partial_close_volume(
        self,
        position_volume,
    ):

        volume = (
            position_volume
            * PARTIAL_CLOSE_PERCENT
            / 100
        )

        return round(volume, 2)

    # =====================================================
    # Stop Distance
    # =====================================================

    def stop_distance(self, signal):

        return abs(
            signal.entry -
            signal.stop_loss
        )

    # =====================================================
    # Reward Distance
    # =====================================================

    def reward_distance(self, signal):

        if signal.take_profit is None:
            return 0

        return abs(
            signal.take_profit -
            signal.entry
        )

    # =====================================================
    # Trade Summary
    # =====================================================

    def summary(self, signal):

        return {

            "symbol": signal.symbol,

            "direction": signal.direction,

            "lot_size": self.calculate_lot_size(signal),

            "risk_reward": self.calculate_rr(signal),

            "rr_valid": self.validate_rr(signal),

            "daily_loss_ok": self.validate_daily_loss(),

            "account_risk_ok": self.validate_account_risk(),

        }


risk_manager = RiskManager()