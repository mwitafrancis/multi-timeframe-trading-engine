"""
=========================================================
Professional Trading Signal Models
=========================================================

Shared dataclasses used throughout the trading system.

Every indicator returns one of these objects.

Author: ChatGPT
=========================================================
"""
from dataclasses import dataclass, field
from typing import List, Optional, Any
import numpy as np


# =========================================================
# EMA
# =========================================================

@dataclass(slots=True)
class EMASignal:

    bullish: bool

    bearish: bool

    trend: str

    strength: float

    ema_fast: float

    ema_medium: float

    ema_slow: float

    slope_fast: float

    slope_medium: float

    slope_slow: float


# =========================================================
# ATR
# =========================================================

@dataclass(slots=True)
class ATRSignal:

    valid: bool

    atr: float

    atr_percent: float

    volatility: str

    expanding: bool

    contracting: bool

    stop_multiplier: float


# =========================================================
# Volume
# =========================================================

@dataclass(slots=True)
class VolumeSignal:

    valid: bool

    current: float

    average: float

    relative: float

    trend: str

    high_volume: bool

    low_volume: bool

    expanding: bool

    contracting: bool


# =========================================================
# Trend
# =========================================================

@dataclass(slots=True)
class TrendSignal:

    bullish: bool

    bearish: bool

    trend: str

    phase: str

    strength: float

    higher_highs: bool

    higher_lows: bool

    lower_highs: bool

    lower_lows: bool

    pullback: bool

    continuation: bool

    price_above_fast: bool

    price_above_medium: bool

    price_above_slow: bool


# =========================================================
# ADX
# =========================================================

@dataclass(slots=True)
class ADXSignal:

    valid: bool

    adx: float

    plus_di: float

    minus_di: float

    strong_trend: bool

    weak_trend: bool

    bullish: bool

    bearish: bool

    momentum: float = 0.0

    gap: float = 0.0

    expanding: bool = False

    exhausted: bool = False


# =========================================================
# RSI
# =========================================================

@dataclass(slots=True)
class RSISignal:

    valid: bool

    rsi: float

    overbought: bool

    oversold: bool

    bullish: bool

    bearish: bool

    momentum: str



# =========================================================
# Candlestick Pattern
# =========================================================

@dataclass(slots=True)
class PatternSignal:

    valid: bool

    pattern: str

    direction: str

    entry: Optional[float]

    stop: Optional[float]

    take_profit: Optional[float]

    candle_index: int

    time: Optional[object]

    strength: float = 0.0

    pattern_score: float = 0.0

    metadata: dict | None = None

    

    @classmethod
    def invalid(cls):

        return cls(

            valid=False,

            pattern="",

            direction="",

            entry=None,

            stop=None,

            take_profit=None,

            candle_index=-1,

            time=None,

            strength=0.0,

            pattern_score=0.0,

            metadata=None,

        )


# =========================================================
# Final Trading Signal
# =========================================================

@dataclass(slots=True)
class TradeSignal:

    valid: bool

    symbol: str

    direction: str

    pattern: str

    score: float

    entry: float

    stop_loss: float

    take_profit: Optional[float]

    lot_size: float

    risk_reward: float

    trend: str

    phase: str

    confirmation_score: float

    comment: str

    market: Optional["MarketState"] = None
    priority: int = 0

    @classmethod
    def invalid(cls):

        return cls(

            valid=False,

            symbol="",

            direction="",

            pattern="",

            score=0,

            entry=0,

            stop_loss=0,

            take_profit=None,

            lot_size=0,

            risk_reward=0,

            trend="",

            phase="",

            confirmation_score=0,

            comment="",

            market=None,

        )

@dataclass(slots=True, frozen=True)
class VWAPSignal:

    valid: bool

    vwap: float

    price_above: bool

    price_below: bool

    distance: float

    premium: bool

    discount: bool

    fair_value: bool

    crossed_above: bool

    crossed_below: bool

    trend_confirmation: str

    @classmethod
    def invalid(cls):
        return cls(
            valid=False,
            vwap=0.0,
            price_above=False,
            price_below=False,
            distance=0.0,
            premium=False,
            discount=False,
            fair_value=True,
            crossed_above=False,
            crossed_below=False,
            trend_confirmation="NONE",
        )
    
@dataclass(slots=True)
class MarketState:

    symbol: str

    timeframe: str
    market_state: str

    market_score: int

    ema: EMASignal

    atr: ATRSignal

    trend: TrendSignal

    adx: ADXSignal

    rsi: RSISignal

    vwap: VWAPSignal

    volume: VolumeSignal

    # ---------- Institutional confirmations ----------

    bos: object | None = None

    choch: object | None = None

    m5_structure: object | None = None

    liquidity: object | None = None

    fvg: object | None = None

    order_block: object | None = None

    breaker: object | None = None

    mitigation: object | None = None

    premium_discount: object | None = None

    # -------- Market Classification --------

    regime: "MarketRegimeSignal | None" = None

    # -------- Levels --------

    support: "SRLevel | None" = None

    resistance: "SRLevel | None" = None

    supply: "Zone | None" = None

    demand: "Zone | None" = None

    # -------- Location --------

    location: "LocationSignal | None" = None

    # -------- Range --------

    range: "RangeSignal | None" = None
    



@dataclass(slots=True)
class LiquidityZone:

    high: float
    low: float
    midpoint: float
    zone_type: str
    touches: int
    strength: float
    distance: float = float("inf")
    distance_score: float = 0.0
    swept: bool = False
    sweep_index: int = -1
    bar_index: int = -1
    timestamp: Any = None


@dataclass(slots=True)
class LiquiditySignal:

    valid: bool
    buy_side: LiquidityZone | None
    sell_side: LiquidityZone | None
    near_buy_side: bool
    near_sell_side: bool
    swept_buy_side: bool
    swept_sell_side: bool
    score: float

    @classmethod
    def invalid(cls):
        return cls(
            valid=False,
            buy_side=None,
            sell_side=None,
            near_buy_side=False,
            near_sell_side=False,
            swept_buy_side=False,
            swept_sell_side=False,
            score=0.0,
        )

# ==========================================================
# Market Regime
# ==========================================================

@dataclass(slots=True)
class MarketRegimeSignal:

    state: str

    bullish: bool

    bearish: bool

    ranging: bool

    score: int

    adx: float

    ema_distance: float

    trend_strength: float = 0.0


# ==========================================================
# Location
# ==========================================================
@dataclass(slots=True)
class LocationSignal:

    score: int

    reason: List[str]

    near_support: bool

    near_resistance: bool

    near_supply: bool

    near_demand: bool

    near_range_high: bool

    near_range_low: bool

    near_buy_side_liquidity: bool = False
    near_sell_side_liquidity: bool = False
    swept_buy_side_liquidity: bool = False
    swept_sell_side_liquidity: bool = False
    liquidity_score: float = 0.0
    near_bullish_fvg: bool = False
    near_bearish_fvg: bool = False

    demand_touched: bool = False
    supply_touched: bool = False
    support_touched: bool = False
    resistance_touched: bool = False
    bullish_location_touched: bool = False
    bearish_location_touched: bool = False

    support: "SRLevel | None" = None

    resistance: "SRLevel | None" = None

    supply: "Zone | None" = None

    demand: "Zone | None" = None



# ==========================================================
# FAIR VALUE GAP
# ==========================================================

@dataclass(slots=True)
class FairValueGap:
    high: float
    low: float
    midpoint: float
    direction: str
    fresh: bool
    filled: bool
    bar_index: int = -1
    timestamp: Any = None
    distance: float = float("inf")
    distance_score: float = 0.0
    size: float = 0.0
    touched: bool = False


@dataclass(slots=True)
class FVGSignal:
    valid: bool
    bullish: FairValueGap | None
    bearish: FairValueGap | None
    near_bullish: bool
    near_bearish: bool
    score: float

    @classmethod
    def invalid(cls):
        return cls(False, None, None, False, False, 0.0)

# ==========================================================
# Swing Levels
# ==========================================================

@dataclass(slots=True)
class SwingSignal:

    swing_high: Optional[float]

    swing_low: Optional[float]

    last_high_index: int

    last_low_index: int

@dataclass(slots=True)
class RangeSignal:

    valid: bool

    high: float

    low: float

    middle: float

    width: float

    near_top: bool

    near_bottom: bool

    in_middle: bool

    touches_high: int

    touches_low: int

    score: int

@dataclass(slots=True)
class Zone:

    high: float

    low: float

    midpoint: float

    fresh: bool

    retests: int

    strength: float

    touched: bool

    zone_type: str

    distance: float = float("inf")

    bar_index: int = -1

    timestamp: Any = None

    last_touch: int = -1

    score: float = 0.0

    distance_score: float = 0.0
    origin_index: int = -1
    departure_atr: float = 0.0
    base_type: str = ""
    last_retest_index: int = -1
    


@dataclass(slots=True)
class SupplyDemandSignal:

    supply: Zone | None

    demand: Zone | None

    near_supply: bool

    near_demand: bool

    supply_distance: float

    demand_distance: float

    score: int


@dataclass(slots=True)
class SRLevel:

    price: float

    touches: int

    strength: float

    kind: str

    distance: float = float("inf")

    bar_index: int = -1

    timestamp: Any = None

    fresh: bool = True

    last_touch: int = -1

    distance_score: float = 0.0
    touched: bool = False
    origin_index: int = -1
    departure_atr: float = 0.0
    base_type: str = ""
    last_retest_index: int = -1


@dataclass(slots=True)
class SRSignal:

    support: SRLevel | None

    resistance: SRLevel | None

    near_support: bool

    near_resistance: bool


@dataclass(slots=True)
class M5StructureSignal:
    valid: bool
    bullish_bos: bool = False
    bearish_bos: bool = False
    bullish_choch: bool = False
    bearish_choch: bool = False
    swept_sell_side: bool = False
    swept_buy_side: bool = False
    displacement_bullish: bool = False
    displacement_bearish: bool = False
    score_buy: float = 0.0
    score_sell: float = 0.0
    last_event: str = "NONE"
    event_age: int = 999
    sweep_age: int = 999
    swing_high: float = np.nan
    swing_low: float = np.nan