"""
=========================================================
Professional Base Strategy
=========================================================

Every candlestick strategy inherits this class.

Workflow

Pattern
    ↓
Market Confirmation
    ↓
Score
    ↓
TradeSignal

Author: francis
=========================================================
"""
from config import (
    TREND_WEIGHT,
    EMA_WEIGHT,
    ADX_WEIGHT,
    RSI_WEIGHT,
    VWAP_WEIGHT,
    VOLUME_WEIGHT,
    ATR_WEIGHT,
    ADX_STRONG,
    MIN_CONFIRMATION_SCORE,
    PATTERN_WEIGHT,
    CONFIRMATION_WEIGHT,
    DEFAULT_LOT_SIZE,
    DEFAULT_RISK_REWARD,
    PRINT_CONFIRMATION_DEBUG,
    PRINT_CONFIRMATION_DEBUG2,

    MAX_PATTERN_TRADE_AGE,
    MAX_ENTRY_ATR_DISTANCE,

    PATTERN_SCORE_WEIGHT,
    LOCATION_SCORE_WEIGHT,
    CONFIRMATION_SCORE_WEIGHT,
    MARKET_SCORE_WEIGHT,
    MIN_FINAL_SCORE,
    ALLOW_COUNTER_TREND_IN_WEAK_MARKETS,
    COUNTER_TREND_MIN_SCORE,
    MIN_REWARD_ATR,
    MIN_STOP_ATR,
    PATTERN_CONFIRMATION_FLOORS,
    BREAKOUT_PATTERNS,
    MIN_LOCATION_SCORE_FOR_NON_BREAKOUT,
    ALLOW_COUNTER_TREND_IN_RANGE,
    ENABLE_MULTI_TIMEFRAME,

    REQUIRE_H1_BIAS_ALIGNMENT,

    REQUIRE_M15_LOCATION,

    REQUIRE_M5_CONFIRMATION,

    # v3 quality engine
    PATTERN_SCORE_WEIGHT_V3,
    LOCATION_SCORE_WEIGHT_V3,
    CONFIRMATION_SCORE_WEIGHT_V3,
    MARKET_SCORE_WEIGHT_V3,
    LOCATION_MIN_SCORE,
    LOCATION_STRONG_SCORE,
    REQUIRE_LOCATION_TOUCH_FOR_REVERSAL,
    REQUIRE_M5_STRUCTURE_OR_SWEEP,
    BREAKOUT_MIN_CLOSE_ATR,
    BREAKOUT_MIN_BODY_ATR,
    BREAKOUT_MIN_DISPLACEMENT_ATR,
    BREAKOUT_MAX_EXTENSION_ATR,
    BREAKOUT_REQUIRE_LEVEL_BREAK,
    BREAKOUT_REQUIRE_DISPLACEMENT,
    BREAKOUT_ALLOW_RETEST_ENTRY,
    BREAKOUT_RETEST_MAX_AGE,
    BREAKOUT_LOCATION_MIN_SCORE,
    USE_ZONE_AWARE_STOP,
    ZONE_STOP_BUFFER_ATR,
    M5_STOP_BUFFER_ATR,
    M5_REACTION_MIN_SCORE,
    M5_ATR_CONTEXT_SCORE,
    M5_VOLUME_CONTEXT_SCORE,
    M5_ADX_CONTEXT_SCORE,
)
from abc import ABC, abstractmethod
import numpy as np

from core import market
from core.market_state import build_market_state

from indicators.signals import (
    TradeSignal,
)
from utils.candle import (
    pivot_low,
    pivot_high,
)

from config import (
    USE_SWING_STOP,
    SWING_LEFT,
    SWING_RIGHT,
    ATR_STOP_BUFFER,
)
class BaseStrategy(ABC):
  

    """
    Base class for every candlestick strategy.

    """
    PATTERN_NAME = "Base"

    CATEGORY = "Unknown"

    DIRECTION = "NONE"

    ENABLED = True

    MIN_SCORE = 70

    PRIORITY = 50

    REQUIRES_TREND = False

    REQUIRES_EMA = True

    REQUIRES_ADX = False

    REQUIRES_RSI = True

    REQUIRES_VWAP = False

    REQUIRES_VOLUME = False

    REQUIRES_ATR = True
    def __init__(

        self,

        symbol,

        timeframe,

    ):

        self.symbol = symbol

        self.timeframe = timeframe
    # =====================================================
    # Strategy Weights
    # =====================================================

    def get_weights(self):

        """
        Default weights.
        Child strategies override this method.
        """

        return {

            "trend": TREND_WEIGHT,

            "ema": EMA_WEIGHT,

            "adx": ADX_WEIGHT,

            "rsi": RSI_WEIGHT,

            "vwap": VWAP_WEIGHT,

            "volume": VOLUME_WEIGHT,

            "atr": ATR_WEIGHT,

        }
    # =====================================================
    # Pattern Detection
    # =====================================================

    @abstractmethod
    def detect(self, df):

        """
        Detect candlestick pattern.

        Returns PatternSignal
        """

        pass
     # =====================================================
    # Trade Direction
    # =====================================================

    @abstractmethod
    def direction(self):

        """
        BUY or SELL
        """

        pass
  
        # =====================================================
    # Trend
    # =====================================================

    def check_trend(

        self,

        market,

        direction,

    ):

        if direction == "BUY":

            return market.trend.bullish

        return market.trend.bearish
        # =====================================================
    # EMA
    # =====================================================

    def check_ema(

        self,

        market,

        direction,

    ):

        if direction == "BUY":

            return market.ema.bullish

        return market.ema.bearish
        # =====================================================
    # ATR
    # =====================================================

    def check_atr(

        self,

        market,

    ):

        return market.atr.valid
        # =====================================================
    # Volume
    # =====================================================

    def check_volume(

        self,

        market,

    ):

        return market.volume.high_volume
        # =====================================================
    # ADX
    # =====================================================

    def check_adx(self, market, direction):

        adx = market.adx

        if not adx.valid:
            return False

        # Directional ADX confirmation.
        # ADX strength is confirmed by DI direction.
        if adx.adx < ADX_STRONG:
            return False

        if direction == "BUY":
            return adx.bullish

        return adx.bearish
        # =====================================================
    # RSI
    # =====================================================

    def check_rsi(self, market, direction):

        if direction == "BUY":

            return market.rsi.bullish

        return market.rsi.bearish
        # =====================================================
    # VWAP
    # =====================================================

    def check_vwap(self, market, direction):

        if direction == "BUY":

            return (

                market.vwap.discount

                or

                market.vwap.price_above

            )

        return (

            market.vwap.premium

            or

            market.vwap.price_below

        )
    # =====================================================
    # Confirmation Score
    # =====================================================

    def confirmation_score(self, market, direction):
        """M5 reaction score: structure/liquidity first, indicators secondary.

        EMA/RSI/VWAP are intentionally not used here; H1 already supplies
        directional bias and the candle engine supplies the pattern score.
        """
        structure = getattr(market, "m5_structure", None)
        if structure is None or not getattr(structure, "valid", False):
            return 0.0

        score = float(structure.score_buy if direction == "BUY" else structure.score_sell)
        if getattr(market.atr, "valid", False):
            score += M5_ATR_CONTEXT_SCORE
        if getattr(market.volume, "high_volume", False):
            score += M5_VOLUME_CONTEXT_SCORE
        if getattr(market.adx, "valid", False) and getattr(market.adx, "strong_trend", False):
            score += M5_ADX_CONTEXT_SCORE

        score = min(100.0, score)
        if PRINT_CONFIRMATION_DEBUG:
            print("\n========== M5 REACTION ==========")
            print(f"Direction        : {direction}")
            print(f"BOS              : {getattr(structure, 'bullish_bos' if direction == 'BUY' else 'bearish_bos', False)}")
            print(f"CHOCH            : {getattr(structure, 'bullish_choch' if direction == 'BUY' else 'bearish_choch', False)}")
            print(f"Liquidity Sweep  : {getattr(structure, 'swept_sell_side' if direction == 'BUY' else 'swept_buy_side', False)}")
            print(f"Displacement     : {getattr(structure, 'displacement_bullish' if direction == 'BUY' else 'displacement_bearish', False)}")
            print(f"Reaction Score   : {score:.1f}")
            print("==================================")
        return score

    def confirm(self, market, direction):
        return self.confirmation_score(market, direction) >= M5_REACTION_MIN_SCORE

    # =====================================================
    # Final Professional Score
    # =====================================================

    def calculate_score(self, pattern, confirmation, bias_market, location_market):
        pattern_score = float(pattern["strength"])
        location_score = float(location_market.location.score)
        market_score = float(bias_market.market_score)
        final = (
            pattern_score * PATTERN_SCORE_WEIGHT_V3
            + location_score * LOCATION_SCORE_WEIGHT_V3
            + confirmation * CONFIRMATION_SCORE_WEIGHT_V3
            + market_score * MARKET_SCORE_WEIGHT_V3
        )
        return round(max(0.0, min(100.0, final)), 2)

    # =====================================================
    # Trade Signal
    # =====================================================
    def bias_allows_trade(

        self,

        bias_market,

        direction,

    ):

        if bias_market is None:

            return False


        if direction == "BUY":

            return (

                bias_market.trend.bullish

                and bias_market.ema.bullish

            )


        if direction == "SELL":

            return (

                bias_market.trend.bearish

                and bias_market.ema.bearish

            )


        return False


    def trade_signal(

        self,

        df,

        bias_market,

        location_market,

        confirmation_market,

    ):

        # ===========================================
        # Validate Market Snapshot
        # ===========================================

        # ===========================================
        # Validate Multi-Timeframe Market Snapshots
        # ===========================================

        if bias_market is None:

            return TradeSignal.invalid()


        if location_market is None:

            return TradeSignal.invalid()


        if confirmation_market is None:

            return TradeSignal.invalid()


        # H1 must have a valid market state
        if bias_market.market_state is None:

            return TradeSignal.invalid()


        # M15 must have a valid location object
        if location_market.location is None:

            return TradeSignal.invalid()

        patterns = self.detect(df)

        if not patterns:
            return TradeSignal.invalid()

        best_pattern = None

        best_score = float("-inf")

        best_confirmation = 0

        for pattern in patterns:
            required = (
                "direction",
                "entry",
                "strength",
                "bars_ago",
                "pattern",
            )

            if any(k not in pattern for k in required):
                continue
            direction = pattern["direction"]
            # ===========================================
            # Strategy Direction Filter
            # ===========================================

            strategy_direction = self.direction()

            if (
                strategy_direction != "DYNAMIC"
                and
                direction != strategy_direction
            ):

                continue

            # ======================================================
            # H1 BIAS ALIGNMENT
            # ======================================================

            if (

                ENABLE_MULTI_TIMEFRAME

                and

                REQUIRE_H1_BIAS_ALIGNMENT

            ):

                if not self.bias_allows_trade(

                    bias_market,

                    direction,

                ):

                    print(

                        f"[{self.PATTERN_NAME}] "

                        f"REJECTED — H1 bias does not align "

                        f"with {direction}"

                    )

                    continue
            # --------------------------------------------------
            # Market Regime Filter
            # --------------------------------------------------

            is_breakout_pattern = (
                pattern["pattern"] in BREAKOUT_PATTERNS
            )

            regime_ok = self.regime_allows_trade(

                bias_market,

                direction,

                pattern["strength"],

            )

            # M15 location route. Reversals require an actual touch;
            # breakouts use a separate level-break/displacement route.
            atr_for_context = float(getattr(confirmation_market.atr, "atr", 0.0) or 0.0)
            breakout_ok = False
            breakout_reason = ""
            if is_breakout_pattern and atr_for_context > 0:
                breakout_ok, breakout_reason = self.breakout_quality(
                    pattern, location_market, confirmation_market, direction, atr_for_context
                )

            location_ok = breakout_ok if is_breakout_pattern else self.valid_location(
                location_market, direction
            )

            if ENABLE_MULTI_TIMEFRAME and REQUIRE_M15_LOCATION and not location_ok:
                print(f"[{self.PATTERN_NAME}] REJECTED — location/reaction invalid for {direction}")
                if is_breakout_pattern:
                    print(f"Breakout reason: {breakout_reason}")
                continue

            confirmation = self.confirmation_score(
                confirmation_market,
                direction,
            )

            structure = getattr(confirmation_market, "m5_structure", None)
            if not is_breakout_pattern and REQUIRE_M5_STRUCTURE_OR_SWEEP:
                structural_reaction = bool(
                    structure and
                    (
                        getattr(structure, "bullish_bos" if direction == "BUY" else "bearish_bos", False)
                        or getattr(structure, "bullish_choch" if direction == "BUY" else "bearish_choch", False)
                        or getattr(structure, "swept_sell_side" if direction == "BUY" else "swept_buy_side", False)
                    )
                )
                if not structural_reaction:
                    print(f"{self.PATTERN_NAME}: No M5 BOS/CHOCH or directional liquidity sweep")
                    continue

            # =====================================================
            # Location Floor
            # =====================================================

            location_score = float(
                location_market.location.score
            )

            if not is_breakout_pattern and location_score < LOCATION_MIN_SCORE:
                print(f"{self.PATTERN_NAME}: Location score too weak ({location_score:.1f} < {LOCATION_MIN_SCORE})")
                continue
            if is_breakout_pattern and not breakout_ok:
                continue
            # =====================================================
            # Soft Context Evaluation
            # =====================================================
            context_bonus = 0.0
            if location_ok: context_bonus += 4.0
            if regime_ok: context_bonus += 3.0
            if location_score >= LOCATION_STRONG_SCORE: context_bonus += 3.0
            if is_breakout_pattern and pattern.get("breakout_structure", False): context_bonus += 3.0
            if structure:
                if direction == "BUY" and getattr(structure, "swept_sell_side", False): context_bonus += 3.0
                if direction == "SELL" and getattr(structure, "swept_buy_side", False): context_bonus += 3.0

            # =====================================================
            # FAIR VALUE GAP CONFLUENCE
            # =====================================================

            if (

                direction == "BUY"

                and

                getattr(

                    location_market.location,

                    "near_bullish_fvg",

                    False,

                )

            ):

                context_bonus += 3.0


            if (

                direction == "SELL"

                and

                getattr(

                    location_market.location,

                    "near_bearish_fvg",

                    False,

                )

            ):

                context_bonus += 3.0

            # One structural reaction floor replaces the old indicator-heavy
            # pattern-specific floors. Candle quality is already in pattern strength.
            required_score = M5_REACTION_MIN_SCORE


            print("\n" + "=" * 60)
            print(f"Strategy      : {self.PATTERN_NAME}")
            print(f"Direction     : {direction}")
            print("-" * 60)

            print("\n========== MULTI-TIMEFRAME ANALYSIS ==========")

            print(
                f"H1 Trend       : "
                f"{bias_market.trend.trend}"
            )

            print(
                f"H1 EMA         : "
                f"{bias_market.ema.trend}"
            )

            print(
                f"H1 Regime      : "
                f"{bias_market.market_state}"
            )

            print(
                f"M15 Location   : "
                f"{location_market.location.score:.1f}"
            )

            if location_market.fvg is not None:

                print(
                    f"M15 FVG Score  : "
                    f"{location_market.fvg.score:.1f}"
                )
            print(
                f"M15 Bull FVG   : "
                f"{getattr(location_market.location, 'near_bullish_fvg', False)}"
            )

            print(
                f"M15 Bear FVG   : "
                f"{getattr(location_market.location, 'near_bearish_fvg', False)}"
            )

            print(
                f"M5 Confirmation: "
                f"{confirmation:.1f}"
            )

            print("===============================================")
            print(
                f"H1 Market Score : "
                f"{bias_market.market_score:.1f}"
            )

            print("-" * 60)

            print(f"Pattern Score : {pattern['strength']:.1f}")
            print(f"Confirmation  : {confirmation:.1f}")

            print("-" * 60)

            print(

                "M15 Reasons   : "

                +

                (

                    ", ".join(
                        location_market.location.reason
                    )

                    if location_market.location.reason

                    else "None"

                )

            )

            print("=" * 60)

           
            print(
                f"Required Confirmation={required_score}"
            )

            print(
                f"Regime Context       = "
                f"{'ALIGNED' if regime_ok else 'COUNTER/WEAK'}"
            )

            print(
                f"Location Context     = "
                f"{'ALIGNED' if location_ok else 'NOT IDEAL'}"
            )

            print(
                f"Location Floor       = {LOCATION_MIN_SCORE}"
            )

            print(
                f"Breakout Exemption   = "
                f"{is_breakout_pattern}"
            )

            if (

                ENABLE_MULTI_TIMEFRAME

                and

                REQUIRE_M5_CONFIRMATION

            ):

                if confirmation < required_score:

                    print(

                        f"{self.PATTERN_NAME}: "

                        f"M5 confirmation below pattern floor "

                        f"({confirmation:.1f} < {required_score})"

                    )

                    continue

            score = self.calculate_score(

                pattern,

                confirmation,

                bias_market,

                location_market,

            )

            score += context_bonus
            score = max(0, min(score, 100))

            # Small bonus for perfect confluence
            if location_market.location.score >= 80:

                score += min(

                    5,

                    location_market.location.score * 0.05,

                )

            score = min(score, 100)
            if PRINT_CONFIRMATION_DEBUG:

                print("\n" + "=" * 70)
                print("FINAL TRADE EVALUATION")
                print("=" * 70)

                print(f"Pattern        : {pattern['pattern']}")
                print(f"Strategy       : {self.PATTERN_NAME}")
                print(f"Direction      : {direction}")
                print(
                    f"H1 Market State : "
                    f"{bias_market.market_state}"
                )

                print(
                    f"M15 Location    : "
                    f"{location_market.location.score:.1f}"
                )

                print(
                    f"M5 Confirmation : "
                    f"{confirmation:.1f}"
                )
                print(f"Confirmation   : {confirmation:.1f}")
                print(f"Final Score    : {score:.1f}")
                print(f"Priority       : {self.PRIORITY}")

                print("=" * 70)
            if score < MIN_FINAL_SCORE:

                print(

                    f"{self.PATTERN_NAME}: "

                    f"Final score too low "

                    f"({score:.1f})"

                )

                continue

            if score > best_score:

                best_score = score
                best_pattern = pattern
                best_confirmation = confirmation
        if best_pattern is None:

            print(
                f"[{self.PATTERN_NAME}] "
                f"No confirmed pattern."
            )

            return TradeSignal.invalid()

        pattern = best_pattern
        score = best_score
        confirmation = best_confirmation
        
        direction = pattern["direction"]
        is_breakout_pattern = (
            pattern["pattern"] in BREAKOUT_PATTERNS
        )
        # =====================================================
        # Reject old patterns
        # =====================================================

        if pattern["bars_ago"] > MAX_PATTERN_TRADE_AGE:

            print(
                f"[{pattern['pattern']}] "
                f"Rejected - Pattern is "
                f"{pattern['bars_ago']} candles old."
            )

            return TradeSignal.invalid()

        if PRINT_CONFIRMATION_DEBUG2:
            print(

                f"[{pattern.get('engine','unknown')}] "

                f"{pattern['pattern']} "

                f"{direction} "

                f"Score={score:.1f} "

                f"Confirmation={confirmation:.0f}"

            )
        entry = float(pattern["entry"])
        # =====================================================
        # Reject stale entries
        # =====================================================

        price = float(df.close.iloc[-1])


        atr_signal = confirmation_market.atr

        if atr_signal is None:

            return TradeSignal.invalid()

        if atr_signal.atr <= 0:

            return TradeSignal.invalid()

        if not atr_signal.valid:
            print(f"[{pattern['pattern']}] ATR invalid.")
            return TradeSignal.invalid()

        atr = float(atr_signal.atr)

        distance = abs(price - entry)

        allowed_distance = atr * MAX_ENTRY_ATR_DISTANCE

        # Strong patterns can tolerate a little more movement
        if pattern["strength"] >= 95:
            allowed_distance *= 1.25

        if distance > allowed_distance:

            print(
                f"[{pattern['pattern']}] "
                f"Rejected - Price moved too far."
            )

            print(
                f"Entry    : {entry:.5f}"
            )

            print(
                f"Current  : {price:.5f}"
            )

            print(
                f"Distance : {distance:.5f}"
            )

            print(f"Allowed  : {allowed_distance:.5f}")

            return TradeSignal.invalid()
        # ---------------------------------------------------
        # Build Professional Stop Loss
        # ---------------------------------------------------

        if USE_SWING_STOP:

            if direction == "BUY":

                stop = pivot_low(
                    df,
                    left=SWING_LEFT,
                    right=SWING_RIGHT,
                    bars_ago=pattern["bars_ago"],
                )

                stop -= atr * ATR_STOP_BUFFER

            else:

                stop = pivot_high(
                    df,
                    left=SWING_LEFT,
                    right=SWING_RIGHT,
                    bars_ago=pattern["bars_ago"],
                )

                stop += atr * ATR_STOP_BUFFER

        else:

            stop = float(pattern["stop"])

        # Zone-aware stop: for a reversal, protect the structural reaction
        # rather than blindly using an unrelated M5 pivot.
        if USE_ZONE_AWARE_STOP and not is_breakout_pattern:
            loc = location_market.location
            candidates = []
            if direction == "BUY":
                if getattr(loc, "demand", None): candidates.append(float(loc.demand.low) - atr * ZONE_STOP_BUFFER_ATR)
                if getattr(loc, "support", None): candidates.append(float(loc.support.price) - atr * ZONE_STOP_BUFFER_ATR)
                if structure and getattr(structure, "swing_low", np.nan) == getattr(structure, "swing_low", np.nan):
                    candidates.append(float(structure.swing_low) - atr * M5_STOP_BUFFER_ATR)
                if candidates: stop = min([stop] + candidates)
            else:
                if getattr(loc, "supply", None): candidates.append(float(loc.supply.high) + atr * ZONE_STOP_BUFFER_ATR)
                if getattr(loc, "resistance", None): candidates.append(float(loc.resistance.price) + atr * ZONE_STOP_BUFFER_ATR)
                if structure and getattr(structure, "swing_high", np.nan) == getattr(structure, "swing_high", np.nan):
                    candidates.append(float(structure.swing_high) + atr * M5_STOP_BUFFER_ATR)
                if candidates: stop = max([stop] + candidates)

        risk = abs(entry - stop)
        if risk <= 0:
            return TradeSignal.invalid()
        minimum_stop = atr * MIN_STOP_ATR

        if risk < minimum_stop:

            if direction == "BUY":
                stop = entry - minimum_stop
            else:
                stop = entry + minimum_stop

            # The stop was adjusted, so risk must be recalculated
            # before constructing the take-profit distance.
            risk = abs(entry - stop)

        reward = max(

            risk * DEFAULT_RISK_REWARD,

            atr * MIN_REWARD_ATR,

        )

        if direction == "BUY":
            take_profit = entry + reward
        else:
            take_profit = entry - reward

        print("\n========== TRADE LEVELS ==========")
        print(f"Pattern     : {pattern['pattern']}")
        print(f"Direction   : {direction}")
        print(f"Entry       : {entry:.5f}")
        print(f"Swing Stop  : {stop:.5f}")
        print(f"ATR         : {atr:.5f}")
        print(f"ATR Buffer  : {atr * ATR_STOP_BUFFER:.5f}")
        print(f"Risk        : {risk:.5f}")
        print(f"Reward      : {reward:.5f}")
        print(f"Take Profit : {take_profit:.5f}")
        print("==================================\n")
        print("=" * 60)
        print(pattern["pattern"])
        print("Direction :", direction)
        print("Entry     :", entry)
        print("Stop      :", stop)
        print("Risk      :", risk)
        print("TP        :", take_profit)
        print("=" * 60)

        return TradeSignal(

            valid=True,

            symbol=self.symbol,

            priority=self.PRIORITY,

            direction=direction,

            pattern=pattern["pattern"],

            score=score,

            entry=entry,

            stop_loss=stop,

            take_profit=take_profit,

            lot_size=DEFAULT_LOT_SIZE,

            risk_reward=DEFAULT_RISK_REWARD,

            trend=bias_market.trend.trend,

            confirmation_score=confirmation,

            phase=bias_market.trend.phase,

            comment=(

                f"{pattern['pattern']} | "

                f"H1={bias_market.market_state} | "

                f"M15_Location="
                f"{location_market.location.score:.1f} | "

                f"Liquidity="
                f"{getattr(location_market.location, 'liquidity_score', 0):.1f} | "

                f"M5_Confirmation="
                f"{confirmation:.1f} | "

                f"Final={score:.1f}"

            ),

            market=bias_market,
        )
    # =====================================================
    # Market Regime Filter
    # =====================================================

    def regime_allows_trade(
        self,
        market,
        direction,
        pattern_score,
    ):

        state = market.market_state

        # -----------------------
        # Strong Bull
        # -----------------------

        if state == "STRONG_BULL":

            return direction == "BUY"

        # -----------------------
        # Strong Bear
        # -----------------------

        if state == "STRONG_BEAR":

            return direction == "SELL"

        # -----------------------
        # Weak Bull
        # -----------------------

        if state == "WEAK_BULL":

            if direction == "BUY":
                return True

            if (
                ALLOW_COUNTER_TREND_IN_WEAK_MARKETS
                and
                pattern_score >= COUNTER_TREND_MIN_SCORE
            ):
                return True

            return False

        # -----------------------
        # Weak Bear
        # -----------------------

        if state == "WEAK_BEAR":

            if direction == "SELL":
                return True

            if (
                ALLOW_COUNTER_TREND_IN_WEAK_MARKETS
                and
                pattern_score >= COUNTER_TREND_MIN_SCORE
            ):
                return True

            return False

        # -----------------------
        # Range
        # -----------------------

        if state == "RANGE":

            # H1 only provides bias.
            # M15 valid_location() handles
            # support, resistance, range,
            # liquidity, supply/demand and FVG.

            return ALLOW_COUNTER_TREND_IN_RANGE
        return True
    
    # =====================================================
    # Location Filter
    # =====================================================

    def valid_location(self, market, direction):
        """Require a directional location AND an actual interaction.

        Merely being within an ATR of a zone is not a reaction.
        """
        if market is None or market.location is None:
            return False
        loc = market.location
        score = float(loc.score)
        if score < LOCATION_MIN_SCORE:
            return False

        if direction == "BUY":
            directional_area = (loc.near_demand or loc.near_support or loc.near_bullish_fvg or
                                loc.near_sell_side_liquidity or loc.swept_sell_side_liquidity or loc.near_range_low)
            touched = (getattr(loc, "bullish_location_touched", False) or
                       loc.swept_sell_side_liquidity or
                       (loc.near_range_low and loc.score >= LOCATION_STRONG_SCORE))
        elif direction == "SELL":
            directional_area = (loc.near_supply or loc.near_resistance or loc.near_bearish_fvg or
                                loc.near_buy_side_liquidity or loc.swept_buy_side_liquidity or loc.near_range_high)
            touched = (getattr(loc, "bearish_location_touched", False) or
                       loc.swept_buy_side_liquidity or
                       (loc.near_range_high and loc.score >= LOCATION_STRONG_SCORE))
        else:
            return False

        if not directional_area:
            return False
        if REQUIRE_LOCATION_TOUCH_FOR_REVERSAL and not touched:
            return False
        return True

    def breakout_quality(self, pattern, location_market, confirmation_market, direction, atr):
        """Separate breakout route: break a real level + displacement, without
        requiring a demand/supply touch that belongs to reversal setups."""
        if direction not in ("BUY", "SELL"):
            return False, "Invalid breakout direction"
        candle = pattern.get("candle")
        if candle is None:
            return False, "No breakout candle"
        body = abs(float(candle.close) - float(candle.open))
        if body < atr * BREAKOUT_MIN_BODY_ATR:
            return False, "Breakout body too small"

        level = None
        sr = location_market
        if direction == "BUY":
            candidates = [getattr(sr, "resistance", None), getattr(sr, "supply", None)]
            vals = []
            for x in candidates:
                if x is None: continue
                v = float(x.price if hasattr(x, "price") else x.high)
                if v <= float(candle.close) + atr * BREAKOUT_MAX_EXTENSION_ATR:
                    vals.append(v)
            if vals: level = max(vals)
            broke = level is not None and float(candle.close) > level + atr * BREAKOUT_MIN_CLOSE_ATR
            extension = 0.0 if level is None else (float(candle.close)-level)/atr
            displacement = body/atr >= BREAKOUT_MIN_DISPLACEMENT_ATR and float(candle.close) > float(candle.open)
            structure = getattr(confirmation_market, "m5_structure", None)
            struct_ok = bool(structure and (structure.bullish_bos or structure.bullish_choch))
        else:
            candidates = [getattr(sr, "support", None), getattr(sr, "demand", None)]
            vals = []
            for x in candidates:
                if x is None: continue
                v = float(x.price if hasattr(x, "price") else x.low)
                if v >= float(candle.close) - atr * BREAKOUT_MAX_EXTENSION_ATR:
                    vals.append(v)
            if vals: level = min(vals)
            broke = level is not None and float(candle.close) < level - atr * BREAKOUT_MIN_CLOSE_ATR
            extension = 0.0 if level is None else (level-float(candle.close))/atr
            displacement = body/atr >= BREAKOUT_MIN_DISPLACEMENT_ATR and float(candle.close) < float(candle.open)
            structure = getattr(confirmation_market, "m5_structure", None)
            struct_ok = bool(structure and (structure.bearish_bos or structure.bearish_choch))
        if BREAKOUT_REQUIRE_LEVEL_BREAK and not broke:
            return False, "No confirmed level break"
        if BREAKOUT_REQUIRE_DISPLACEMENT and not displacement:
            return False, "No breakout displacement"
        if extension > BREAKOUT_MAX_EXTENSION_ATR:
            return False, "Breakout over-extended"
        # Structure is a quality bonus/soft requirement: pattern already proves
        # the break, so allow valid breakouts without forcing a second identical gate.
        if struct_ok:
            pattern["breakout_structure"] = True
        pattern["breakout_level"] = level
        return True, "Breakout confirmed"

