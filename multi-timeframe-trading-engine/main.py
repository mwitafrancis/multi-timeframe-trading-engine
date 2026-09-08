"""
=========================================================
Professional Institutional Candlestick Trading Bot
=========================================================

Main application entry point.

Workflow

Connect MT5
      ↓
Loop Symbols
      ↓
Download OHLC
      ↓
Run Signal Engine
      ↓
Execute Valid Trades
      ↓
Repeat

Portfolio project
=========================================================
"""

import time
from datetime import datetime

from config import (
    SYMBOLS,

    BIAS_TIMEFRAME,
    BIAS_BARS,

    LOCATION_TIMEFRAME,
    LOCATION_BARS,

    CONFIRMATION_TIMEFRAME,
    CONFIRMATION_BARS,

    SCAN_INTERVAL,
    ONE_SIGNAL_PER_SYMBOL_PER_CANDLE,
)

from core.mt5 import (
    connect,
    disconnect,
)

from core.market import (
    get_rates,
)

from strategy.signal_engine import SignalEngine

from core.execution import ExecutionEngine


# ==========================================================
# Trading Bot
# ==========================================================

class TradingBot:

    def __init__(self):

        self.execution = ExecutionEngine()
        self._last_signal_candle = {}

    # ======================================================
    # Scan One Symbol
    # ======================================================

    def scan_symbol(self, symbol):

        print(f"\nScanning {symbol}")

        # ======================================================
        # H1 — MARKET BIAS DATA
        # ======================================================

        df_h1 = get_rates(
            symbol,
            BIAS_TIMEFRAME,
            BIAS_BARS,
        )


        # ======================================================
        # M15 — MARKET LOCATION DATA
        # ======================================================

        df_m15 = get_rates(
            symbol,
            LOCATION_TIMEFRAME,
            LOCATION_BARS,
        )


        # ======================================================
        # M5 — TRADE CONFIRMATION DATA
        # ======================================================

        df_m5 = get_rates(
            symbol,
            CONFIRMATION_TIMEFRAME,
            CONFIRMATION_BARS,
        )


        # ======================================================
        # Validate Data
        # ======================================================

        if df_h1.empty:

            print(f"{symbol}: No H1 market data.")
            return


        if df_m15.empty:

            print(f"{symbol}: No M15 market data.")
            return


        if df_m5.empty:

            print(f"{symbol}: No M5 market data.")
            return


        # ======================================================
        # Multi-Timeframe Signal Engine
        # ======================================================

        engine = SignalEngine(symbol)


        signals = engine.analyze(

            df_h1=df_h1,

            df_m15=df_m15,

            df_m5=df_m5,

        )

        if not signals:

            print("No signals.")
            return

        # Rank every valid candidate once, then execute only the best signal.
        signals.sort(
            key=lambda signal: (
                getattr(signal, "priority", 0),
                getattr(signal, "confirmation_score", 0),
                signal.score,
            ),
            reverse=True,
        )

        # M5 is the execution/confirmation timeframe.
        # Prevent duplicate processing of the same M5 candle.

        candle_time = df_m5.iloc[-1]["time"]
        if ONE_SIGNAL_PER_SYMBOL_PER_CANDLE:
            if self._last_signal_candle.get(symbol) == candle_time:
                print(f"{symbol}: signal candle already processed.")
                return
            self._last_signal_candle[symbol] = candle_time
            signals = signals[:1]

        for signal in signals:
            print(
                f"BEST SIGNAL → {signal.pattern:<25}"
                f"{signal.direction:<5} "
                f"Score={signal.score:.1f} "
                f"Confirmation={getattr(signal, 'confirmation_score', 0):.1f}"
            )
            self.execution.execute(signal)

    # ======================================================
    # Main Loop
    # ======================================================

    def run(self):

        connect()

        print("\nTrading Bot Started\n")

        try:

            while True:

                print(
                    "\n========================================"
                )

                print(
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )

                print(
                    "========================================"
                )

                for symbol in SYMBOLS:

                    self.scan_symbol(symbol)

                print(

                    f"\nSleeping {SCAN_INTERVAL} seconds..."

                )

                time.sleep(SCAN_INTERVAL)

        except KeyboardInterrupt:

            print("\nStopping Bot...")

        finally:

            disconnect()

            print("Disconnected from MT5.")


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":

    bot = TradingBot()

    bot.run()