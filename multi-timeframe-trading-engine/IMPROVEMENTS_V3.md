# Candle Patterns Bot — Quality Location / Entry Upgrade v3

## Architecture

H1 bias → M15 location → M5 reaction → candle pattern → entry → zone-aware SL/TP.

## Implemented

- Supply/demand zones now use a swing + base/origin + directional displacement model.
- Zones are narrower than the previous full-candle zones and are invalidated by a CLOSED break beyond the zone, not a wick.
- Retests are counted as distinct visits rather than every overlapping candle.
- M15 location analysis uses `closed_m15 = df.iloc[:-1].copy()` and passes that closed dataset through S/R, supply/demand, liquidity, FVG and range detection.
- Detector APIs support `already_closed=True` so M15 data is not accidentally stripped twice.
- Location scoring is directional:
  - BUY: demand, support, bullish FVG, sell-side liquidity and sell-side sweep.
  - SELL: supply, resistance, bearish FVG, buy-side liquidity and buy-side sweep.
- Liquidity double-counting in the location score was removed.
- FVG detection now requires a meaningful three-candle imbalance plus displacement, respects maximum age, and uses closed candles.
- FVGs distinguish a current touch from simple proximity.
- S/R levels distinguish a current candle touch from simple proximity.
- M5 confirmation was changed from indicator-heavy confirmation to price-action reaction scoring.
- M5 now detects directional liquidity sweeps, BOS, CHOCH and displacement.
- Reversal entries require an actual directional location interaction and a recent M5 BOS/CHOCH or directional liquidity sweep.
- Breakout entries use a separate route: real level break + close beyond the level + displacement + extension control. A breakout does not need to touch a reversal zone first.
- Stop construction can use the M15 zone, M5 structure and existing swing stop with ATR buffers.
- Final score now weights pattern 30%, location 35%, M5 reaction 25%, H1 market 10%.
- The new reaction logic is intentionally soft: BOS/CHOCH, sweep and displacement contribute independently instead of requiring every component.

## Important runtime note

The project was syntax-checked with `py_compile`. A live MT5 runtime test requires the `MetaTrader5` Python package and a connected terminal/account, which are not available in this execution environment.
