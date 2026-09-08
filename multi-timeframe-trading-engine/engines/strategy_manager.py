"""
=========================================================
Professional Strategy Manager
=========================================================

Runs every candlestick strategy independently.

Workflow

OHLC Data
      │
      ▼
All Strategy Engines
      │
      ▼
TradeSignals
      │
      ▼
Remove Invalid
      │
      ▼
Sort By Priority
      │
      ▼
Sort By Confirmation
      │
      ▼
Sort By Score
      │
      ▼
Best Trade

=========================================================
"""

from indicators.signals import TradeSignal

from engines.morning_star import MorningStarStrategy
from engines.evening_star import EveningStarStrategy

from engines.hammer import HammerStrategy
from engines.inverted_hammer import InvertedHammerStrategy
from engines.hanging_man import HangingManStrategy
from engines.shooting_star import ShootingStarStrategy

from engines.bullish_engulfing import BullishEngulfingStrategy
from engines.bearish_engulfing import BearishEngulfingStrategy

from engines.three_white_soldiers import ThreeWhiteSoldiersStrategy
from engines.three_black_crows import ThreeBlackCrowsStrategy

from engines.three_inside_up import ThreeInsideUpStrategy
from engines.three_inside_down import ThreeInsideDownStrategy

from engines.breakout_three import BreakoutThreeStrategy
from engines.breakdown_three import BreakdownThreeStrategy

from engines.doji import DojiStrategy
from engines.spinning_top import SpinningTopStrategy
import traceback
from core.market_state import build_market_state
from config import CONFIRMATION_TIMEFRAME


class StrategyManager:

    def __init__(self, symbol):

        self.symbol = symbol

        strategies = [

            MorningStarStrategy(symbol, CONFIRMATION_TIMEFRAME,),

            EveningStarStrategy(symbol, CONFIRMATION_TIMEFRAME,),

            HammerStrategy(symbol, CONFIRMATION_TIMEFRAME,),

            InvertedHammerStrategy(symbol, CONFIRMATION_TIMEFRAME,),

            HangingManStrategy(symbol, CONFIRMATION_TIMEFRAME,),

            ShootingStarStrategy(symbol, CONFIRMATION_TIMEFRAME,),

            BullishEngulfingStrategy(symbol, CONFIRMATION_TIMEFRAME,),

            BearishEngulfingStrategy(symbol, CONFIRMATION_TIMEFRAME,),

            ThreeWhiteSoldiersStrategy(symbol, CONFIRMATION_TIMEFRAME,),

            ThreeBlackCrowsStrategy(symbol, CONFIRMATION_TIMEFRAME,),

            ThreeInsideUpStrategy(symbol, CONFIRMATION_TIMEFRAME,),

            ThreeInsideDownStrategy(symbol, CONFIRMATION_TIMEFRAME,),

            BreakoutThreeStrategy(symbol, CONFIRMATION_TIMEFRAME,),

            BreakdownThreeStrategy(symbol, CONFIRMATION_TIMEFRAME,),

            DojiStrategy(symbol, CONFIRMATION_TIMEFRAME,),

            SpinningTopStrategy(symbol, CONFIRMATION_TIMEFRAME,),

        ]

        self.strategies = [

            strategy

            for strategy in strategies

            if getattr(strategy, "ENABLED", True)

        ]

    # =====================================================
    # Analyze Every Strategy
    # =====================================================

    def analyze(

        self,

        df_h1,

        df_m15,

        df_m5,

    ):

        signals = []


        # ==================================================
        # H1 — MARKET BIAS
        # ==================================================

        bias_market = build_market_state(

            self.symbol,

            "H1",

            df_h1,

            mode="BIAS",

        )

        # ==================================================
        # DETERMINE H1 BIAS DIRECTION
        # ==================================================

        h1_bias_direction = None


        if (

            bias_market.trend.bullish

            and

            bias_market.ema.bullish

        ):

            h1_bias_direction = "BUY"


        elif (

            bias_market.trend.bearish

            and

            bias_market.ema.bearish

        ):

            h1_bias_direction = "SELL"


        # ==================================================
        # M15 — MARKET LOCATION
        # ==================================================

        location_market = build_market_state(

            self.symbol,

            "M15",

            df_m15,

            mode="LOCATION",

            bias_direction=h1_bias_direction,

        )


        # ==================================================
        # M5 — CONFIRMATION
        # ==================================================

        confirmation_market = build_market_state(

            self.symbol,

            "M5",

            df_m5,

            mode="CONFIRMATION",

        )


        # ==================================================
        # RUN CANDLE PATTERN STRATEGIES ON M5
        # ==================================================

        for strategy in self.strategies:

            try:

                signal = strategy.trade_signal(

                    df_m5,

                    bias_market,

                    location_market,

                    confirmation_market,

                )


                if signal is not None and signal.valid:

                    signals.append(signal)


            except Exception:

                print(
                    "\n" + "=" * 80
                )

                print(
                    f"ERROR IN STRATEGY : "
                    f"{strategy.PATTERN_NAME}"
                )

                traceback.print_exc()

                print(
                    "=" * 80 + "\n"
                )


        return signals

    # =====================================================
    # Best Signal
    # =====================================================

    def best_signal(self, df):

        signals = self.analyze(df)

        if len(signals) == 0:

            return TradeSignal.invalid()

        signals.sort(

            key=lambda s: (

                getattr(s, "priority", 0),

                getattr(s, "confirmation_score", 0),

                s.score,

                getattr(s, "time", None),

            ),

            reverse=True,

        )

        return signals[0]

    # =====================================================
    # Top Signals
    # =====================================================

    def top_signals(

        self,

        df,

        limit=5,

    ):

        signals = self.analyze(df)

        signals.sort(

            key=lambda s: (

                getattr(s, "priority", 0),

                getattr(s, "confirmation_score", 0),

                s.score,

            ),

            reverse=True,

        )

        return signals[:limit]

    # =====================================================
    # BUY Signals
    # =====================================================

    def buy_signals(self, df):

        return [

            signal

            for signal in self.analyze(df)

            if signal.direction == "BUY"

        ]

    # =====================================================
    # SELL Signals
    # =====================================================

    def sell_signals(self, df):

        return [

            signal

            for signal in self.analyze(df)

            if signal.direction == "SELL"

        ]

    # =====================================================
    # Count Signals
    # =====================================================

    def signal_count(self, df):

        return len(

            self.analyze(df)

        )

    # =====================================================
    # Print Ranking
    # =====================================================

    def print_ranking(self, df):

        signals = self.top_signals(df, 100)

        print()

        print("=" * 70)

        print("STRATEGY RANKING")

        print("=" * 70)

        for signal in signals:

            print(

                f"{signal.pattern:25}"

                f"{signal.direction:6}"

                f"Priority={getattr(signal,'priority',0):3}"

                f"  "

                f"Confirmation={getattr(signal,'confirmation_score',0):5.1f}"

                f"  "

                f"Score={signal.score:5.1f}"

                f" "

                f"{getattr(signal,'engine',''):20}"

            )

        print("=" * 70)