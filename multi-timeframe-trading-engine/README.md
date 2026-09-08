# Multi-Timeframe Algorithmic Trading & Market Analysis Engine

A modular Python research and execution framework for multi-timeframe market analysis. The project separates market-data access, technical indicators, pattern recognition, signal scoring, risk controls, and trade execution into focused modules.

> **Portfolio note:** This repository is presented as a software-engineering project. It is not financial advice and should not be used with real funds without independent testing, validation, and appropriate risk controls.

## Engineering Highlights

- **Python architecture:** separated `core`, `engines`, `indicators`, `strategy`, and `utils` modules.
- **Multi-timeframe analysis:** combines higher-timeframe bias with lower-timeframe location and confirmation data.
- **Algorithmic signal processing:** evaluates candlestick patterns, trend, volatility, volume, market regime, liquidity, support/resistance, supply/demand, VWAP and fair-value gaps.
- **Scoring and ranking:** candidates are scored and ranked before execution, with duplicate-signal protection per candle.
- **Risk management:** dedicated risk and order-management components provide account-risk and trade-validation controls.
- **External integration:** uses the MetaTrader 5 Python API for market data and execution.
- **Maintainability:** functionality is decomposed into small, domain-focused modules rather than a single monolithic script.

## Architecture

```text
main.py
   │
   ├── core/          Market data, MT5 connection, execution, orders, risk
   │
   ├── strategy/      Signal orchestration and filtering
   │
   ├── engines/       Candlestick/pattern strategy implementations
   │
   ├── indicators/    Technical and market-structure calculations
   │
   └── utils/         Candle measurements and scoring utilities
```

## Main workflow

```text
MetaTrader 5
     ↓
Market data retrieval
     ↓
Multi-timeframe analysis
     ↓
Indicators + pattern engines
     ↓
Signal scoring / filtering
     ↓
Risk validation
     ↓
Execution engine
```

## Project Structure

```text
core/
  execution.py
  logger.py
  market.py
  market_state.py
  mt5.py
  orders.py
  risk.py

engines/
  base_strategy.py
  strategy_manager.py
  ... candlestick pattern engines

indicators/
  adx.py
  atr.py
  ema.py
  fair_value_gap.py
  liquidity.py
  market_regime.py
  m5_structure.py
  rsi.py
  supply_demand.py
  support_resistance.py
  trend.py
  volume.py
  vwap.py

strategy/
  filters.py
  signal_engine.py

utils/
  candle.py
  pattern_score.py
```

## Requirements

- Python 3.10+ recommended
- MetaTrader 5 desktop terminal
- A MetaTrader 5 account for live market-data/execution integration

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Machine-specific MetaTrader 5 configuration is intentionally kept outside the repository. Set the optional `MT5_PATH` environment variable if the terminal is installed in a non-default location.

Windows PowerShell example:

```powershell
$env:MT5_PATH = 'C:\Path\To\terminal64.exe'
```

Review `config.py` before running the system. Symbols, timeframes, thresholds, risk parameters, and strategy switches are configurable there.

## Running

After MetaTrader 5 is installed, configured, and logged in:

```bash
python main.py
```

The application connects to MT5, retrieves multi-timeframe market data, evaluates signals, applies filters/risk checks, and passes valid candidates to the execution layer.

## Validation

A basic syntax validation can be performed without placing trades:

```bash
python -m compileall .
```

The project should be further tested in a demo environment before any production use.

## Design Decisions

### Separation of concerns

Market connectivity, strategy evaluation, indicators, risk controls, and order execution are kept in separate modules. This makes individual components easier to inspect, test, replace, and extend.

### Strategy extensibility

Pattern implementations are isolated under `engines/`, allowing new strategies to be added without rewriting the central execution loop.

### Risk before execution

Risk-related checks are represented in a dedicated module instead of being scattered throughout individual pattern implementations.

## Future Improvements

- Add a formal unit/integration test suite.
- Add typed interfaces/dataclasses for signal contracts across modules.
- Introduce dependency injection for the market-data and execution layers.
- Add CI for linting, tests, and static analysis.
- Add deterministic historical backtesting and performance benchmarks.
- Separate research configuration from execution configuration.

## Disclaimer

This project is for software-engineering and research purposes. Trading involves substantial risk. Past or simulated performance does not guarantee future results.
