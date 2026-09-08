
# ==========================================================
# Bot
# ==========================================================
import os
import MetaTrader5 as mt5

PRINT_CONFIRMATION_DEBUG = True
PRINT_CONFIRMATION_DEBUG2 = True
PRINT_MARKET_STATE = True

# ==========================================================
# DEBUG
# ==========================================================

PRINT_SUPPORT = True

PRINT_RESISTANCE = True

PRINT_SUPPLY = True

PRINT_DEMAND = True

PRINT_RANGE = True

PRINT_LOCATION_SCORE = True

PRINT_FINAL_SCORE = True

PRINT_STOPLOSS = False

# =====================================================
# Dynamic Lot Sizing
# =====================================================

ENABLE_DYNAMIC_LOT = True

# Final score thresholds
LOT_SCORE_LEVEL_1 = 85
LOT_SCORE_LEVEL_2 = 90
LOT_SCORE_LEVEL_3 = 95

# Multipliers
LOT_MULTIPLIER_LEVEL_1 = 1.10
LOT_MULTIPLIER_LEVEL_2 = 1.20
LOT_MULTIPLIER_LEVEL_3 = 1.30

# Optional RR requirement
ENABLE_LOT_RR_FILTER = True

LOT_MIN_RR_LEVEL_1 = 1.80
LOT_MIN_RR_LEVEL_2 = 2.00
LOT_MIN_RR_LEVEL_3 = 2.50

# Never exceed this multiplier
MAX_DYNAMIC_LOT_MULTIPLIER = 1.50
MAX_PATTERN_TRADE_AGE = 2
MAX_ENTRY_ATR_DISTANCE = 0.30

# ==========================================================
# MARKET REGIME
# ==========================================================
ENABLE_HARD_LOCATION_FILTER = False
ENABLE_MARKET_REGIME = True

STRONG_TREND_ADX = 35
WEAK_TREND_ADX = 25
RANGE_ADX = 20

EMA_STRONG_DISTANCE = 0.0030
EMA_WEAK_DISTANCE = 0.0015

ALLOW_COUNTER_TREND_IN_RANGE = True

COUNTER_TREND_MIN_SCORE = 75

MIN_REWARD_ATR = 1

# Strong Levels

STRONG_LEVEL_MIN_STRENGTH = 90
STRONG_LEVEL_BONUS = 5

# Strong Supply/Demand

STRONG_ZONE_MIN_STRENGTH = 90
STRONG_ZONE_BONUS = 5

# ==========================================================
# MARKET STATE SCORING
# ==========================================================

MARKET_STATE_SCORES = {

    "STRONG_BULL": 100,

    "WEAK_BULL": 75,

    "RANGE": 60,

    "WEAK_BEAR": 75,

    "STRONG_BEAR": 100,

}

# ==========================================================
# BREAKOUT PATTERNS
# ==========================================================

BREAKOUT_PATTERNS = {
    "Breakout Three",
    "Breakdown Three",
}

MIN_LOCATION_SCORE_FOR_NON_BREAKOUT = 20

# ==========================================================
# LIQUIDITY ZONES
# ==========================================================

ENABLE_LIQUIDITY_ZONES = True

# ==========================================================
# FAIR VALUE GAP
# ==========================================================
ENABLE_FVG = True
FVG_MIN_SIZE_ATR = 0.10
FVG_MAX_DISTANCE_ATR = 1.50
FVG_NEAR_DISTANCE_SCORE = 40.0
FVG_REQUIRE_FRESH = True
FVG_LOCATION_SCORE = 15
FVG_CONFLUENCE_BONUS = 8
PRINT_FVG = True

#liquidity timeframe

LIQUIDITY_TIMEFRAME = mt5.TIMEFRAME_M15
# ----------------------------------------------------------
# Swing detection
# ----------------------------------------------------------

LIQUIDITY_SWING_LEFT = 2
LIQUIDITY_SWING_RIGHT = 2

# Used when deciding whether a swing itself is valid.
LIQUIDITY_SWING_TOLERANCE_ATR = 0.05

# ----------------------------------------------------------
# Equal High / Equal Low clustering
# ----------------------------------------------------------

LIQUIDITY_CLUSTER_ATR = 0.12
LIQUIDITY_CLUSTER_PRICE_PERCENT = 0.00025

LIQUIDITY_MIN_TOUCHES = 2

# Width of the actual liquidity zone.
LIQUIDITY_ZONE_WIDTH_ATR = 0.08

# Prevent extremely wide liquidity zones.
LIQUIDITY_MAX_ZONE_WIDTH_ATR = 0.30

# ----------------------------------------------------------
# Liquidity proximity
# ----------------------------------------------------------

LIQUIDITY_DISTANCE_ATR = 0.75

# ----------------------------------------------------------
# Liquidity sweep
# ----------------------------------------------------------

# Price must penetrate beyond the zone by this ATR amount.
LIQUIDITY_SWEEP_BUFFER_ATR = 0.02

# A sweep older than this many CLOSED candles is not considered
# current reaction evidence.
LIQUIDITY_SWEEP_MAX_AGE = 2

# ----------------------------------------------------------
# Liquidity scoring
# ----------------------------------------------------------

LIQUIDITY_BASE_SCORE = 45
LIQUIDITY_TOUCH_SCORE = 12

LIQUIDITY_PROXIMITY_SCORE = 10

# Sweep gets more weight than simple proximity.
LIQUIDITY_SWEEP_SCORE = 15

LIQUIDITY_STRONG_ZONE_STRENGTH = 75
LIQUIDITY_STRONG_ZONE_BONUS = 5

# Maximum liquidity contribution to Location Score.
LIQUIDITY_LOCATION_MAX_SCORE = 25

LIQUIDITY_LOOKBACK = 150

# ----------------------------------------------------------
# Debug
# ----------------------------------------------------------

PRINT_LIQUIDITY = True

# ==========================================================
# PATTERN-SPECIFIC CONFIRMATION FLOORS
# ==========================================================

PATTERN_CONFIRMATION_FLOORS = {

    # Strong reversal / continuation patterns
    "Morning Star": 55,
    "Evening Star": 55,

    "Bullish Engulfing": 55,
    "Bearish Engulfing": 55,

    "Hammer": 55,
    "Shooting Star": 55,

    "Inverted Hammer": 55,
    "Hanging Man": 60,

    "Three White Soldiers": 60,
    "Three Black Crows": 60,

    "Three Inside Up": 55,
    "Three Inside Down": 55,

    # Breakout patterns
    "Breakout Three": 55,
    "Breakdown Three": 55,

    # Pin bar
    "Pin Bar": 55,

    # Lower-information patterns need more confirmation
    "Doji": 65,
    "Spinning Top": 65,
}

# ==========================================================
# SUPPORT / RESISTANCE
# =========================================================

ENABLE_SUPPORT_RESISTANCE = True

SWING_RIGHT = 2

MAX_LEVELS = 15

MIN_LEVEL_TOUCHES = 2

SUP_RES_DISTANCE_ATR = 1

SUP_RES_SCORE = 12

FRESH_LEVEL_SCORE = 5
LEVEL_CLUSTER_ATR = 0.30

LEVEL_CLUSTER_PRICE_PERCENT = 0.0004


SWING_TOLERANCE_ATR = 0.10
# ==========================================================
# SUPPLY / DEMAND
# ==========================================================

SUPPLY_DEMAND_TIMEFRAME = mt5.TIMEFRAME_H1

ENABLE_SUPPLY_DEMAND = True

ZONE_LOOKBACK = 200

ZONE_SWING = 3

ZONE_MIN_BODY_ATR = 0.80

ZONE_MAX_SIZE_ATR = 3.0

ZONE_MIN_SIZE_ATR = 0.40

ZONE_DISTANCE_ATR = 1.0

MAX_RETESTS = 2

FRESH_ZONE_SCORE = 10

RETEST_ZONE_SCORE = 5

MAX_ZONES = 8

RETEST_PENETRATION_ATR = 0.25

ZONE_DEPARTURE_LOOKAHEAD = 5
MAX_DEPARTURE_SCORE = 20
DEPARTURE_SCORE_MULTIPLIER = 4

RANGE_MAX_WIDTH_ATR = 10

# ==========================================================
# Zone Scoring
# ==========================================================

ZONE_WIDTH_PENALTY = 4

ZONE_FRESH_SCORE = 25

ZONE_RETEST1_SCORE = 15

ZONE_RETEST2_SCORE = 8

ZONE_STALE_SCORE = 0

# ==========================================================
# RANGE DETECTION
# ==========================================================

RANGE_TIMEFRAME = mt5.TIMEFRAME_H1

RANGE_LOOKBACK = 80

RANGE_MIN_TOUCHES = 2

RANGE_EDGE_ATR = 0.50

NO_TRADE_MIDDLE_PERCENT = 0.40
RANGE_EDGE_SCORE = 20

ENABLE_RANGE_TRADING = True


# ==========================================================
# LOCATION SCORE
# ==========================================================

SUPPLY_SCORE = 25

DEMAND_SCORE = 25

SUPPLY_RESISTANCE_SCORE = 35

DEMAND_SUPPORT_SCORE = 35


LOCATION_DEMAND_SCORE = 20

LOCATION_SUPPORT_SCORE = 12

LOCATION_RANGE_SCORE = 18

LOCATION_CONFLUENCE_BONUS = 10

LOCATION_MAX_SCORE = 100

# ==========================================================
# MARKET WEIGHTS
# ==========================================================

STRONG_BULL_WEIGHT = 35

WEAK_BULL_WEIGHT = 20

RANGE_WEIGHT = 20

WEAK_BEAR_WEIGHT = 20

STRONG_BEAR_WEIGHT = 35

# ==========================================================
# FINAL SCORE
# ==========================================================

PATTERN_SCORE_WEIGHT = 0.35

LOCATION_SCORE_WEIGHT = 0.30

CONFIRMATION_SCORE_WEIGHT = 0.20

MARKET_SCORE_WEIGHT = 0.15

# ==========================================================
# EXECUTION
# ==========================================================

DEFAULT_RISK_REWARD = 2.0

DEFAULT_LOT_SIZE = 0.03

# ==========================================================
# STOP LOSS
# ==========================================================

USE_SWING_STOP = True

SWING_LOOKBACK_BARS = 10

SL_ATR_BUFFER = 0.25

MAX_STOP_ATR = 3.00

USE_PATTERN_STOP = False


MIN_STOP_ATR = 0.5

# ==========================================================
# TAKE PROFIT
# ==========================================================

USE_DYNAMIC_TP = True

MIN_RR = 2.0

MAX_RR = 5.0

PARTIAL_CLOSE_AT_R = 1.0

MOVE_SL_TO_BREAKEVEN_AT_R = 1.0

# ==========================================================
# PATTERN FILTERS
# ==========================================================


MAX_PATTERN_LOOKBACK = 10

PATTERN_SCORE_BONUS = 5

ENABLE_PATTERN_FRESHNESS = True

# ==========================================================
# DEBUG
# ==========================================================

PRINT_LOCATION = True


PRINT_RESISTANCE = True

PRINT_SUPPLY = True

PRINT_DEMAND = True

PRINT_RANGE = True

PRINT_PATTERN_SCORE = True

PRINT_FINAL_SCORE = True

PRINT_STOPLOSS = True

# =====================================================
# Swing Stop Settings
# =====================================================

SWING_LOOKBACK = 10

SWING_LEFT = 2

ATR_STOP_BUFFER = 0.20

MIN_STOP_POINTS = {

   # "XAUUSDm":2.0,

    #"US30m":25,

    #"USTECm":20,

    #"DE30m":20,

    #"USOILm":0.15,

}

STRONG_BULL_PATTERNS = [

    "Hammer",

    "Morning Star",

    "Bullish Engulfing",

    "Three White Soldiers",

    "Three Inside Up",

    "Breakout Three",

    "Pin Bar",

]

WEAK_BULL_PATTERNS = STRONG_BULL_PATTERNS + [

    "Doji",

    "Spinning Top",

    "Inverted Hammer",

]

STRONG_BEAR_PATTERNS = [

    "Bearish Engulfing",

    "Evening Star",

    "Three Black Crows",

    "Three Inside Down",

    "Breakdown Three",

    "Hanging Man",

    "Shooting Star",

]

WEAK_BEAR_PATTERNS = STRONG_BEAR_PATTERNS + [

    "Doji",

    "Spinning Top",

]

RANGE_TOP_PATTERNS = [

    "Bearish Engulfing",

    "Evening Star",

    "Shooting Star",

    "Hanging Man",

    "Doji",

    "Spinning Top",

]

RANGE_BOTTOM_PATTERNS = [

    "Bullish Engulfing",

    "Hammer",

    "Morning Star",

    "Three White Soldiers",

    "Three Inside Up",

    "Inverted Hammer",

    "Doji",

    "Spinning Top",

]

# ==========================================================
# MARKET STATE PERMISSIONS
# ==========================================================

ALLOW_RANGE_TRADES = True

ALLOW_COUNTER_TREND_IN_WEAK_MARKETS = True

# ==========================================================
# LOCATION BONUS
# ==========================================================

BONUS_NEAR_SUPPORT = 10

BONUS_NEAR_RESISTANCE = 10

BONUS_NEAR_DEMAND = 20

BONUS_NEAR_SUPPLY = 20

BONUS_RANGE_EDGE = 15

# ==========================================================
# MARKET STATE
# ==========================================================

# Higher timeframe used to determine overall market direction.
MARKET_STATE_TIMEFRAME = mt5.TIMEFRAME_H1

# Number of candles used for market regime calculation.
MARKET_STATE_BARS = 250

# Lookback used for EMA/ADX classification.
MARKET_REGIME_LOOKBACK = 100


SYMBOLS = [

    # ==========================
    # USD MAJORS
    # ==========================
    "EURUSDm",
    "GBPUSDm",
    "AUDUSDm",
    "NZDUSDm",
    "USDCADm",
    "USDCHFm",
    "USDJPYm",

    # ==========================
    # EURO CROSSES
    # ==========================
    "EURGBPm",
    "EURJPYm",
    "EURAUDm",
    "EURCADm",
    "EURNZDm",
    "EURCHFm",

    # ==========================
    # GBP CROSSES
    # ==========================
    "GBPJPYm",
    "GBPCADm",
    "GBPAUDm",
    "GBPNZDm",
    "GBPCHFm",

    # ==========================
    # JPY CROSSES
    # ==========================
    "AUDJPYm",
    "CADJPYm",
    "CHFJPYm",
    "NZDJPYm",
    # AUD Crosses
    "AUDCADm",
    "AUDCHFm",

    # NZD Crosses
    "NZDCADm",

    # ==========================
    # COMMODITIES
    # ==========================
    
    "XAUUSDm",
    #"USOILm",

    # ==========================
    # INDICES
    # ==========================
    "USTECm",
    #"US30m",
    "DE30m",
    #"BTCUSDm",
    #"XAGUSDM",
    "UK100m",
    "US500m"
 

]
# ==========================================================
# SYMBOL LOT SIZES
# ==========================================================

LOT_SIZES = {

    # ==========================
    # USD MAJORS
    # ==========================
    "EURUSDm": 0.10,
    "GBPUSDm": 0.10,
    "AUDUSDm": 0.10,
    "NZDUSDm": 0.10,
    "USDCADm": 0.10,
    "USDCHFm": 0.10,
    "USDJPYm": 0.10,

    # ==========================
    # EURO CROSSES
    # ==========================
    "EURGBPm": 0.10,
    "EURJPYm": 0.10,
    "EURAUDm": 0.10,
    "EURCADm": 0.10,
    "EURNZDm": 0.10,
    "EURCHFm": 0.10,

    # ==========================
    # GBP CROSSES
    # ==========================
    "GBPJPYm": 0.05,
    "GBPCADm": 0.05,
    "GBPAUDm": 0.05,
    "GBPNZDm": 0.05,
    "GBPCHFm": 0.05,

    # ==========================
    # JPY CROSSES
    # ==========================
    "AUDJPYm": 0.05,
    "CADJPYm": 0.05,
    "CHFJPYm": 0.05,
    "NZDJPYm": 0.05,
    "AUDCADm": 0.05,
    "AUDCHFm": 0.05,
    "NZDCADm": 0.05,

    # ==========================
    # COMMODITIES
    # ==========================
   ## "USOILm": 0.02,

    # ==========================
    # INDICES
    # ==========================
    #"USTECm": 0.05,
    #"US30m": 0.05,
    #"DE30m": 0.05,
    #"BTCUSDM": 0.01,
    "XAGUSDM": 0.01,
}

# ==========================================================
# MULTI-TIMEFRAME ARCHITECTURE
# ==========================================================

# H1 — Higher-timeframe market bias
BIAS_TIMEFRAME = mt5.TIMEFRAME_H1
BIAS_BARS = 200

# M15 — Market structure and trade location
LOCATION_TIMEFRAME = mt5.TIMEFRAME_M15
LOCATION_BARS = 300

# M5 — Candlestick confirmation and signal generation
CONFIRMATION_TIMEFRAME = mt5.TIMEFRAME_M5
CONFIRMATION_BARS = 300


# ==========================================================
# MULTI-TIMEFRAME RULES
# ==========================================================

ENABLE_MULTI_TIMEFRAME = True

# Require H1 bias to agree with trade direction
REQUIRE_H1_BIAS_ALIGNMENT = True

# Require valid M15 trade location
REQUIRE_M15_LOCATION = True

# M5 is where candlestick patterns are detected
REQUIRE_M5_CONFIRMATION = True

SCAN_INTERVAL = 20
# ==========================================================
# Pattern Scanner
# ==========================================================

# Number of CLOSED candles every engine should scan.
PATTERN_LOOKBACK = 10

# Never evaluate the live/forming candle.
USE_CLOSED_CANDLES_ONLY = True

# Return every detected pattern instead of stopping at the first.
RETURN_ALL_PATTERNS = True

# Maximum age (bars ago) allowed for a trade.
MAX_PATTERN_AGE = 2

# ==========================================================
# Risk
# ==========================================================

RISK_MODE = "fixed"
# fixed | percent

FIXED_LOT_SIZE = 0.05

RISK_PERCENT = 2.0

MAX_ACCOUNT_RISK = 10.0

MAX_DAILY_LOSS = 5.0

MIN_RISK_REWARD = 1.5

ENABLE_BREAKEVEN = True

BREAKEVEN_AT_R = 1.0

ENABLE_TRAILING_STOP = True

TRAILING_AT_R = 2.0

ENABLE_PARTIAL_CLOSE = True

PARTIAL_CLOSE_AT_R = 1.5

PARTIAL_CLOSE_PERCENT = 50

# ==========================================================
# Trade Defaults
# ==========================================================

# Enable dynamic lot sizing from the risk manager.
USE_DYNAMIC_LOT_SIZE = True

# Calculate take-profit automatically using DEFAULT_RISK_REWARD.
USE_DYNAMIC_TAKE_PROFIT = True

# ==========================================================
# EMA
# ==========================================================

EMA_FAST = 20
EMA_MEDIUM = 50
EMA_SLOW = 200

# ==========================================================
# ATR
# ==========================================================

ATR_PERIOD = 14

ATR_VOLATILITY_LOW = 1.0
ATR_VOLATILITY_MEDIUM = 2.0
ATR_VOLATILITY_HIGH = 3.0

# ==========================================================
# ADX
# ==========================================================

ADX_PERIOD = 14
ADX_STRONG = 25
ADX_VERY_STRONG = 40

# ==========================================================
# RSI
# ==========================================================

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
BULLISH_RSI = 50
BEARISH_RSI = 45

# ==========================================================
# VOLUME
# ==========================================================

VOLUME_PERIOD = 20
HIGH_VOLUME_MULTIPLIER = 1.5
LOW_VOLUME_MULTIPLIER = 0.5
# ==========================================================
# VWAP SETTINGS
# ========================================================
VWAP_SESSION = "daily"      # daily, weekly

PREMIUM_THRESHOLD = 0.001   # 0.1%

DISCOUNT_THRESHOLD = -0.001

TREND_WEIGHT = 20

EMA_WEIGHT = 20
ADX_WEIGHT = 15
RSI_WEIGHT = 15
VWAP_WEIGHT = 10
VOLUME_WEIGHT = 10
ATR_WEIGHT = 10

PATTERN_BASE_SCORE = 50

BODY_SCORE = 10

WICK_SCORE = 10

TREND_SCORE = 15

VOLUME_SCORE = 10

ATR_SCORE = 10

EMA_SCORE = 5

MIN_CONFIRMATION_SCORE = 60
MIN_PATTERN_STRENGTH = 70

MIN_PATTERN_CONFIDENCE = 70

IGNORE_DUPLICATE_PATTERNS = True

DUPLICATE_WINDOW = 1

PATTERN_WEIGHT = 0.60
CONFIRMATION_WEIGHT = 0.40

# ==========================================================
# PATTERN SPECIFIC WEIGHTS
# ==========================================================
PATTERN_PRIORITY = {

    "Morning Star": 100,

    "Evening Star": 100,

    "Bullish Engulfing": 95,

    "Bearish Engulfing": 95,

    "Hammer": 90,

    "Hanging Man": 90,

    "Shooting Star": 90,

    "Three White Soldiers": 95,

    "Three Black Crows": 95,

    "Doji": 60,

    "Spinning Top": 50
}
HAMMER_WEIGHTS = {
    "trend": 15,
    "ema": 15,
    "adx": 10,
    "rsi": 15,
    "vwap": 25,
    "volume": 10,
    "atr": 10,
}

# ==========================================================
# SHOOTING STAR
# ==========================================================

SHOOTING_STAR_WEIGHTS = {

    "trend": 15,

    "ema": 15,

    "adx": 10,

    "rsi": 20,

    "vwap": 20,

    "volume": 10,

    "atr": 10,

}
# ==========================================================
# BULLISH ENGULFING
# ==========================================================

BULLISH_ENGULFING_WEIGHTS = {

    "trend": 25,

    "ema": 20,

    "adx": 15,

    "rsi": 10,

    "vwap": 15,

    "volume": 10,

    "atr": 5,

}
# ==========================================================
# BEARISH ENGULFING
# ==========================================================

BEARISH_ENGULFING_WEIGHTS = {

    "trend": 25,

    "ema": 20,

    "adx": 15,

    "rsi": 10,

    "vwap": 15,

    "volume": 10,

    "atr": 5,

}
# ==========================================================
# THREE WHITE SOLDIERS
# ==========================================================

THREE_WHITE_SOLDIERS_WEIGHTS = {

    "trend": 20,

    "ema": 20,

    "adx": 15,

    "rsi": 10,

    "vwap": 15,

    "volume": 15,

    "atr": 5,

}
# ==========================================================
# THREE BLACK CROWS
# ==========================================================

THREE_BLACK_CROWS_WEIGHTS = {

    "trend": 20,

    "ema": 20,

    "adx": 15,

    "rsi": 10,

    "vwap": 15,

    "volume": 15,

    "atr": 5,

}
# ==========================================================
# THREE INSIDE UP
# ==========================================================

THREE_INSIDE_UP_WEIGHTS = {

    "trend": 20,

    "ema": 20,

    "adx": 15,

    "rsi": 15,

    "vwap": 15,

    "volume": 10,

    "atr": 5,

}
# ==========================================================
# THREE INSIDE DOWN
# ==========================================================

THREE_INSIDE_DOWN_WEIGHTS = {

    "trend": 20,

    "ema": 20,

    "adx": 15,

    "rsi": 15,

    "vwap": 15,

    "volume": 10,

    "atr": 5,

}
BREAKOUT_THREE_WEIGHTS = {

    "trend":20,

    "ema":20,

    "adx":20,

    "rsi":10,

    "vwap":10,

    "volume":15,

    "atr":5,

}
# ==========================================================
# MORNING STAR
# ==========================================================

MORNING_STAR_WEIGHTS = {

    "trend": 15,

    "ema": 15,

    "adx": 10,

    "rsi": 20,

    "vwap": 20,

    "volume": 10,

    "atr": 10,

}
# ==========================================================
# EVENING STAR
# ==========================================================

EVENING_STAR_WEIGHTS = {

    "trend": 15,

    "ema": 15,

    "adx": 10,

    "rsi": 20,

    "vwap": 20,

    "volume": 10,

    "atr": 10,

}
INVERTED_HAMMER_WEIGHTS = {

    "trend":15,

    "ema":15,

    "adx":10,

    "rsi":15,

    "vwap":25,

    "volume":10,

    "atr":10,

}
# ==========================================================
# HANGING MAN
# ==========================================================

HANGING_MAN_WEIGHTS = {

    "trend":15,

    "ema":15,

    "adx":10,

    "rsi":15,

    "vwap":25,

    "volume":10,

    "atr":10,

}
# ==========================================================
# DOJI
# ==========================================================

DOJI_WEIGHTS = {

    "trend":20,

    "ema":20,

    "adx":15,

    "rsi":15,

    "vwap":15,

    "volume":10,

    "atr":5,

}
# ==========================================================
# SPINNING TOP
# ==========================================================

SPINNING_TOP_WEIGHTS = {

    "trend":20,

    "ema":20,

    "adx":15,

    "rsi":15,

    "vwap":15,

    "volume":10,

    "atr":5,

}
PIN_BAR_WEIGHTS = {
    "trend": 20,
    "ema": 20,
    "adx": 15,
    "rsi": 10,
    "vwap": 15,
    "volume": 15,
    "atr": 5,
}
# Position Management
MAX_OPEN_TRADES_PER_SYMBOL = 2
MAX_TOTAL_OPEN_TRADES = 10

# Strategy Control
STRATEGY_COOLDOWNS = {
    "Morning Star": 45,
    "Evening Star": 45,
    "Hammer": 20,
    "Hanging Man": 20,
    "Bullish Engulfing": 15,
    "Bearish Engulfing": 15,
    "Three White Soldiers": 90,
    "Three Black Crows": 90,
    "Three Inside Up": 60,
    "Three Inside Down": 60,
    "Breakout Three": 30,
    "Breakdown Three": 30,
    "Doji": 15,
    "Spinning Top": 15,
}

SIDEWAYS_PATTERNS = {

    "Hammer",

    "Shooting Star",

    "Bullish Engulfing",

    "Bearish Engulfing",

    "Morning Star",

    "Evening Star",

    "Doji",

    "Dragonfly Doji",

    "Gravestone Doji",

    "Pin Bar",

}

# Direction Control
ALLOW_OPPOSITE_TRADES = False
#mt5

MT5_PATH = os.getenv("MT5_PATH", "")

MT5_TIMEOUT = 60000

MT5_PORTABLE = False

# ==========================================================
# Orders
# ==========================================================

MAGIC_NUMBER = 20260719

ORDER_COMMENT = "Candle pattern Bot"

ORDER_FILLING = "IOC"
STRATEGY_PRIORITIES = {

    "Morning Star":100,

    "Evening Star":100,

    "Bullish Engulfing":95,

    "Bearish Engulfing":95,

    "Hammer":90,

    "Hanging Man":90,

    "Inverted Hammer":85,

    "Shooting Star":85,

    "Three White Soldiers":95,

    "Three Black Crows":95,

    "Three Inside Up":80,

    "Three Inside Down":80,

    "Doji":60,

    "Spinning Top":50,

}
ENABLED_STRATEGIES = {

    "Morning Star":True,

    "Evening Star":True,

    "Hammer":True,

    "Inverted Hammer":True,

    "Hanging Man":True,

    "Bullish Engulfing":True,

    "Bearish Engulfing":True,

    "Three White Soldiers":True,

    "Three Black Crows":True,

    "Three Inside Up":True,

    "Three Inside Down":True,

    "Breakout Three":True,

    "Breakdown Three":True,

    "Doji":True,

    "Spinning Top":True,

}

MIN_PATTERN_SCORE = 75

MIN_FINAL_SCORE = 70

ALLOW_MULTIPLE_STRATEGIES = True
MAX_BUY_TRADES = 5

MAX_SELL_TRADES = 5
RECONNECT_DELAY = 5

MAX_RECONNECT_ATTEMPTS = 10
ENABLE_LOGGING = True

LOG_LEVEL = "INFO"

LOG_FILE = "logs/trading.log"
ALLOW_DUPLICATE_ENTRIES = False

MIN_PRICE_DISTANCE = 0.5
# ==========================================================
# BREAKDOWN THREE
# ==========================================================

BREAKDOWN_THREE_WEIGHTS = {

    "trend": 20,

    "ema": 20,

    "adx": 20,

    "rsi": 10,

    "vwap": 10,

    "volume": 15,

    "atr": 5,

}
# ==========================================================
# PATTERN GROUPS
# ==========================================================

BULLISH_PATTERNS = {

    "Bullish Engulfing",

    "Hammer",

    "Morning Star",

    "Three White Soldiers",

    "Three Inside Up",

    "Breakout Three",

    "Pin Bar",

    "Inverted Hammer",

}

BEARISH_PATTERNS = {

    "Bearish Engulfing",

    "Shooting Star",

    "Hanging Man",

    "Evening Star",

    "Three Black Crows",

    "Three Inside Down",

    "Breakdown Three",

}

NEUTRAL_PATTERNS = {

    "Doji",

    "Spinning Top",

}

# ==========================================================
# Execution Safety
# ==========================================================

# Maximum allowed spread in MT5 points immediately before an order.
# Symbols not listed use MAX_SPREAD_POINTS_DEFAULT.
MAX_SPREAD_POINTS_DEFAULT = 100

MAX_SPREAD_POINTS_BY_SYMBOL = {
    # Forex majors / crosses
    "EURUSDm": 40, "GBPUSDm": 50, "AUDUSDm": 40,
    "NZDUSDm": 50, "USDCADm": 50, "USDCHFm": 50,
    "USDJPYm": 50,
    "EURGBPm": 50, "EURJPYm": 60, "EURAUDm": 70,
    "EURCADm": 70, "EURNZDm": 90, "EURCHFm": 70,
    "GBPJPYm": 80, "GBPCADm": 80, "GBPAUDm": 100,
    "GBPNZDm": 120, "GBPCHFm": 100,
    "AUDJPYm": 70, "CADJPYm": 70, "CHFJPYm": 80,
    "NZDJPYm": 80, "AUDCADm": 70, "AUDCHFm": 70,
    "NZDCADm": 80,

    # Indices: tune these to the broker's normal spread if required.
    "USTECm": 150, "DE30m": 200, "UK100m": 200, "US500m": 150,
}

# A signal is re-ranked/executed only once per symbol candle.
ONE_SIGNAL_PER_SYMBOL_PER_CANDLE = True

# ==========================================================
# QUALITY LOCATION / PRICE-ACTION ENGINE (v3)
# ==========================================================
# These settings intentionally use soft scoring rather than requiring every
# condition.  This keeps the bot active while preventing weak middle-of-range
# entries from looking as attractive as true reactions.

ZONE_BASE_LOOKBACK = 3
ZONE_MIN_DEPARTURE_ATR = 1.20
ZONE_DISPLACEMENT_BUFFER_ATR = 0.05
ZONE_NEAR_DISTANCE_ATR = 0.65

# M15 location interaction
LOCATION_TOUCH_MAX_AGE_BARS = 2
LOCATION_REACTION_MIN_SCORE = 45
LOCATION_MIN_SCORE = 38
LOCATION_STRONG_SCORE = 70
LOCATION_EXCELLENT_SCORE = 82

# Directional location weights
LOC_W_PRIMARY_ZONE = 30
LOC_W_SR = 16
LOC_W_FVG = 14
LOC_W_LIQUIDITY_NEAR = 10
LOC_W_LIQUIDITY_SWEEP = 20
LOC_W_RANGE_EDGE = 10
LOC_W_FRESH = 8
LOC_W_CONFLUENCE = 10
LOC_W_TOUCH = 8

# FVG v3
FVG_MAX_AGE_BARS = 40
FVG_FILL_MODE = "WICK"       # WICK = filled on first full penetration
FVG_MIN_DISPLACEMENT_ATR = 0.60
FVG_NEAR_DISTANCE_ATR = 0.65
FVG_MIN_SIZE_ATR = 0.08
FVG_SCORE_WEIGHT_DISTANCE = 0.55
FVG_SCORE_WEIGHT_SIZE = 0.20
FVG_SCORE_WEIGHT_FRESH = 0.25

# M5 price-action confirmation.  No EMA/RSI/VWAP duplication here.
M5_STRUCTURE_LOOKBACK = 80
M5_SWING_LEFT = 2
M5_SWING_RIGHT = 2
M5_SWEEP_LOOKBACK = 12
M5_SWEEP_MAX_AGE = 2
M5_BOS_SCORE = 35
M5_CHOCH_SCORE = 40
M5_SWEEP_SCORE = 35
M5_DISPLACEMENT_SCORE = 15
M5_REACTION_MIN_SCORE = 45
M5_REACTION_STRONG_SCORE = 65

# A reversal entry needs a real location interaction plus either a sweep or
# structure shift.  Breakouts use their own route below.
REQUIRE_LOCATION_TOUCH_FOR_REVERSAL = True
REQUIRE_M5_STRUCTURE_OR_SWEEP = True
ALLOW_PATTERN_ONLY_IF_TOUCH = False

# Breakout quality model
BREAKOUT_MIN_CLOSE_ATR = 0.05
BREAKOUT_MIN_BODY_ATR = 0.60
BREAKOUT_MIN_DISPLACEMENT_ATR = 0.75
BREAKOUT_MAX_EXTENSION_ATR = 0.80
BREAKOUT_REQUIRE_LEVEL_BREAK = True
BREAKOUT_REQUIRE_DISPLACEMENT = True
BREAKOUT_ALLOW_RETEST_ENTRY = True
BREAKOUT_RETEST_MAX_AGE = 3
BREAKOUT_LOCATION_MIN_SCORE = 35

# Zone-aware stops
USE_ZONE_AWARE_STOP = True
ZONE_STOP_BUFFER_ATR = 0.12
M5_STOP_BUFFER_ATR = 0.10

# Final scoring: reduce indicator duplication and give structure/location more
# influence.  Pattern strength remains important but cannot rescue a poor
# location.
PATTERN_SCORE_WEIGHT_V3 = 0.30
LOCATION_SCORE_WEIGHT_V3 = 0.35
CONFIRMATION_SCORE_WEIGHT_V3 = 0.25
MARKET_SCORE_WEIGHT_V3 = 0.10

# M5 indicator context is now secondary.  These are used only as small quality
# bonuses, not as mandatory gates.
M5_ATR_CONTEXT_SCORE = 5
M5_VOLUME_CONTEXT_SCORE = 5
M5_ADX_CONTEXT_SCORE = 5
ZONE_INVALIDATION_BUFFER_ATR = 0.05
