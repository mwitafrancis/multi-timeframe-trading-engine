

from typing import Optional
from config import (
    PATTERN_LOOKBACK,
    USE_CLOSED_CANDLES_ONLY,
    PATTERN_PRIORITY,
)
from config import MAX_PATTERN_AGE


# =========================================================
# Basic Candle Measurements
# =========================================================

def body(candle) -> float:
    """Absolute candle body."""
    return abs(candle.close - candle.open)


def candle_range(candle) -> float:
    """Entire candle range."""
    return candle.high - candle.low


def upper_wick(candle) -> float:
    """Upper wick length."""
    return candle.high - max(candle.open, candle.close)


def lower_wick(candle) -> float:
    """Lower wick length."""
    return min(candle.open, candle.close) - candle.low


def midpoint(candle) -> float:
    """Body midpoint."""
    return (candle.open + candle.close) / 2.0


# =========================================================
# Candle Direction
# =========================================================

def is_bullish(candle) -> bool:
    return candle.close > candle.open


def is_bearish(candle) -> bool:
    return candle.close < candle.open


def is_neutral(candle) -> bool:
    return candle.close == candle.open


# =========================================================
# Candle Quality
# =========================================================

def body_percentage(candle) -> float:

    r = candle_range(candle)

    if r == 0:
        return 0.0

    return body(candle) / r


def upper_percentage(candle) -> float:

    r = candle_range(candle)

    if r == 0:
        return 0.0

    return upper_wick(candle) / r


def lower_percentage(candle) -> float:

    r = candle_range(candle)

    if r == 0:
        return 0.0

    return lower_wick(candle) / r


# =========================================================
# Doji
# =========================================================

def is_doji(
    candle,
    threshold: float = 0.10
) -> bool:
    """
    Body <=10% of total range
    """

    return body_percentage(candle) <= threshold


# =========================================================
# Marubozu
# =========================================================

def is_bullish_marubozu(
    candle,
    wick_threshold: float = 0.05
) -> bool:

    if not is_bullish(candle):
        return False

    return (
        upper_percentage(candle) <= wick_threshold
        and
        lower_percentage(candle) <= wick_threshold
    )


def is_bearish_marubozu(
    candle,
    wick_threshold: float = 0.05
) -> bool:

    if not is_bearish(candle):
        return False

    return (
        upper_percentage(candle) <= wick_threshold
        and
        lower_percentage(candle) <= wick_threshold
    )


# =========================================================
# Hammer
# =========================================================

def is_hammer(
    candle,
    wick_ratio: float = 2.0
) -> bool:

    b = body(candle)

    if b == 0:
        return False

    return (

        lower_wick(candle) >= b * wick_ratio

        and

        upper_wick(candle) <= b * 0.30

    )


# =========================================================
# Shooting Star
# =========================================================

def is_shooting_star(
    candle,
    wick_ratio: float = 2.0
) -> bool:

    b = body(candle)

    if b == 0:
        return False

    return (

        upper_wick(candle) >= b * wick_ratio

        and

        lower_wick(candle) <= b * 0.30

    )


# =========================================================
# Engulfing
# =========================================================

def bullish_engulfing(prev, curr) -> bool:

    return (

        is_bearish(prev)

        and

        is_bullish(curr)

        and

        curr.open <= prev.close

        and

        curr.close >= prev.open

        and

        body(curr) > body(prev)

    )


def bearish_engulfing(prev, curr) -> bool:

    return (

        is_bullish(prev)

        and

        is_bearish(curr)

        and

        curr.open >= prev.close

        and

        curr.close <= prev.open

        and

        body(curr) > body(prev)

    )


# =========================================================
# Candle Strength
# =========================================================

def is_strong_bullish(
    candle,
    minimum_body: float = 0.60
) -> bool:

    return (

        is_bullish(candle)

        and

        body_percentage(candle) >= minimum_body

    )


def is_strong_bearish(
    candle,
    minimum_body: float = 0.60
) -> bool:

    return (

        is_bearish(candle)

        and

        body_percentage(candle) >= minimum_body

    )


# =========================================================
# Higher High
# =========================================================

def higher_high(current, previous) -> bool:
    return current.high > previous.high


def higher_low(current, previous) -> bool:
    return current.low > previous.low


def lower_high(current, previous) -> bool:
    return current.high < previous.high


def lower_low(current, previous) -> bool:
    return current.low < previous.low


# =========================================================
# Gap Detection
# =========================================================

def gap_up(prev, curr) -> bool:
    return curr.low > prev.high


def gap_down(prev, curr) -> bool:
    return curr.high < prev.low


# =========================================================
# Inside / Outside Bars
# =========================================================

def inside_bar(prev, curr) -> bool:

    return (

        curr.high <= prev.high

        and

        curr.low >= prev.low

    )


def outside_bar(prev, curr) -> bool:

    return (

        curr.high >= prev.high

        and

        curr.low <= prev.low

    )


# =========================================================
# Price Position
# =========================================================

def closes_above(prev, curr) -> bool:
    return curr.close > prev.high


def closes_below(prev, curr) -> bool:
    return curr.close < prev.low


# =========================================================
# Average Body Size
# =========================================================

def average_body(df, period=20,  bars_ago=2,):

    end = len(df) - bars_ago + 1

    start = max(0, end - period)

    bodies = [
        body(c)
        for c in df.iloc[start:end].itertuples()
    ]

    if not bodies:
        return 0

    return sum(bodies) / len(bodies)

# =========================================================
# Average Range
# =========================================================

def average_range(df, period = 20, bars_ago=2,):

    end = len(df) - bars_ago + 1
    
    start = max(0, end - period)

    bodies = [
        body(c)
        for c in df.iloc[start:end].itertuples()
    ]

    if not bodies:
        return 0

    return sum(bodies) / len(bodies)


# =========================================================
# Large Candle
# =========================================================

def is_large_body(
    candle,
    df,
    multiplier: float = 1.5,
    period: int = 20
) -> bool:

    avg = average_body(df, period)

    if avg == 0:
        return False

    return body(candle) >= avg * multiplier


# =========================================================
# Small Candle
# =========================================================

def is_small_body(
    candle,
    df,
    multiplier: float = 0.5,
    period: int = 20
) -> bool:

    avg = average_body(df, period)

    if avg == 0:
        return False

    return body(candle) <= avg * multiplier


# =========================================================
# Long Wick Detection
# =========================================================

def long_upper_wick(candle, ratio: float = 2.0) -> bool:

    b = body(candle)

    if b == 0:
        return False

    return upper_wick(candle) >= b * ratio


def long_lower_wick(candle, ratio: float = 2.0) -> bool:

    b = body(candle)

    if b == 0:
        return False

    return lower_wick(candle) >= b * ratio


# =========================================================
# Utility
# =========================================================

def price_distance(price1: float, price2: float) -> float:
    return abs(price1 - price2)


def percent_change(a: float, b: float) -> float:

    if a == 0:
        return 0

    return ((b - a) / a) * 100.0


def candle_color(candle) -> str:

    if is_bullish(candle):
        return "bullish"

    if is_bearish(candle):
        return "bearish"

    return "neutral"
# =========================================================
# Body Relationship
# =========================================================

def is_inside_body(parent, child) -> bool:
    """
    Returns True if the child's body is completely
    inside the parent's body.
    """

    parent_top = max(parent.open, parent.close)
    parent_bottom = min(parent.open, parent.close)

    child_top = max(child.open, child.close)
    child_bottom = min(child.open, child.close)

    return (
        child_top <= parent_top
        and
        child_bottom >= parent_bottom
    )
# =========================================================
# Relative Body Size
# =========================================================

def is_large_body_relative(
    candle,
    df,
    multiplier: float = 1.5,
    period: int = 20
) -> bool:
    """
    True if candle body is larger than the
    average body by multiplier.
    """

    avg = average_body(df, period)

    if avg == 0:
        return False

    return body(candle) >= avg * multiplier
# =========================================================
# Gap Detection
# =========================================================

def is_gap_up(
    previous,
    current,
    minimum_gap: float = 0.0
) -> bool:
    """
    Current candle opens above previous high.
    """

    return current.low > previous.high + minimum_gap

def is_gap_down(
    previous,
    current,
    minimum_gap: float = 0.0
) -> bool:
    """
    Current candle opens below previous low.
    """

    return current.high < previous.low - minimum_gap
# =========================================================
# Consecutive Bullish Candles
# =========================================================

def consecutive_bullish(
    df,
    count=3,
    bars_ago=2,
):

    end = len(df) - bars_ago + 1
    start = end - count

    if start < 0:
        return False

    candles = df.iloc[start:end]

    if len(candles) != count:
        return False

    return all(
        is_bullish(c)
        for c in candles.itertuples()
    )
# =========================================================
# Consecutive Bearish Candles
# =========================================================

def consecutive_bearish(
    df,
    count=3,
    bars_ago=2,
):
    """
    Historical consecutive bearish candles.
    """

    end = len(df) - bars_ago + 1
    start = end - count

    if start < 0:
        return False

    candles = df.iloc[start:end]

    if len(candles) != count:
        return False

    return all(
        is_bearish(candle)
        for candle in candles.itertuples()
    )


def closes_near_high(
    candle,
    threshold: float = 0.80
):
    """
    Close is in the top X% of the candle range.
    """

    rng = candle_range(candle)

    if rng == 0:
        return False

    position = (candle.close - candle.low) / rng

    return position >= threshold

def closes_near_low(
    candle,
    threshold: float = 0.20
):
    """
    Close is in the bottom X% of the candle range.
    """

    rng = candle_range(candle)

    if rng == 0:
        return False

    position = (candle.close - candle.low) / rng

    return position <= threshold


def equal_high(
    a,
    b,
    tolerance
):
    return abs(a.high - b.high) <= tolerance

def equal_low(
    a,
    b,
    tolerance
):
    return abs(a.low - b.low) <= tolerance

def is_expansion_candle(
    candle,
    df,
    multiplier: float = 2.0,
    period: int = 20
):
    """
    True if the candle body is significantly larger than the recent average.
    """

    avg = average_body(df, period)

    if avg == 0:
        return False

    return body(candle) >= avg * multiplier

# =========================================================
# Body Size Alias
# =========================================================

def body_size(candle):
    """
    Alias for body().
    Keeps compatibility across all engines.
    """
    return body(candle)
def average_upper_wick(
    df,
    period=20,
    bars_ago=2,
):

    if len(df) == 0:
        return 0.0

    end = len(df) - bars_ago + 1
    start = max(0, end - period)

    candles = df.iloc[start:end]

    if len(candles) == 0:
        return 0.0

    return float(
        candles.apply(
            upper_wick,
            axis=1,
        ).mean()
    )

def average_lower_wick(
    df,
    period=20,
    bars_ago=2,
):

    if len(df) == 0:
        return 0.0

    end = len(df) - bars_ago + 1
    start = max(0, end - period)

    candles = df.iloc[start:end]

    if len(candles) == 0:
        return 0.0

    return float(
        candles.apply(
            lower_wick,
            axis=1,
        ).mean()
    )

def short_term_uptrend(
    df,
    lookback=5,
    bars_ago=2,
):

    if len(df) < lookback + bars_ago:
        return False

    end = len(df) - bars_ago + 1
    start = max(0, end - lookback)

    closes = df.close.iloc[start:end]

    if len(closes) < 2:
        return False

    return closes.iloc[-1] > closes.iloc[0]

def short_term_downtrend(
    df,
    lookback=5,
    bars_ago=2,
):

    if len(df) < lookback + bars_ago:
        return False

    end = len(df) - bars_ago + 1
    start = max(0, end - lookback)

    closes = df.close.iloc[start:end]

    if len(closes) < 2:
        return False

    return closes.iloc[-1] < closes.iloc[0]

def body_position(candle):

    rng = candle_range(candle)

    if rng == 0:
        return 0

    center = (candle.open + candle.close) / 2

    return (center - candle.low) / rng

def is_expansion_range(
    candle,
    df,
    multiplier=1.8,
    period=20
):

    avg = average_range(df, period)

    if avg == 0:
        return False

    return candle_range(candle) >= avg * multiplier

def scan_start():
    """
    Starting index.

    -2 = latest CLOSED candle

    -1 = live candle
    """

    if USE_CLOSED_CANDLES_ONLY:
        return 2

    return 1
# ==========================================================
# Scan Last Closed Candles
# ==========================================================

def scan_single_meta(df, lookback=None):

    if lookback is None:
        lookback = PATTERN_LOOKBACK
    """
    Returns one candle at a time.

    Example:
        Hammer
        Shooting Star
        Doji
    """
    start = scan_start()

    max_scan = min(
        lookback,
        len(df) - start + 1,
    )

    for i in range(start, start + max_scan):
            yield {

                "bars_ago": i,

                "index": df.index[-i],

                "candle": df.iloc[-i]
            }




def scan_pairs(df, lookback=None):
    if lookback is None:
       lookback = PATTERN_LOOKBACK
    """
    Returns previous/current candle pairs.

    Example:
        Bullish Engulfing
        Bearish Engulfing
    """
    start = scan_start()

    max_scan = min(
        lookback,
        len(df) - start,
    )

    for i in range(start, start + max_scan):
        prev = df.iloc[-i - 1]
        curr = df.iloc[-i]

        yield {
            "bars_ago": i,
            "previous": prev,
            "current": curr,
            "time": df.index[-i]
        }


def scan_triples(df, lookback=None):
    if lookback is None:
       lookback = PATTERN_LOOKBACK
    """
    Returns three-candle patterns.

    Example:
        Morning Star
        Evening Star
        Three White Soldiers
    """
    start = scan_start() + 1

    max_scan = min(
        lookback,
        len(df) - start - 1,
    )

    for i in range(start, start + max_scan):
        a = df.iloc[-i]
        b = df.iloc[-i + 1]
        c = df.iloc[-i + 2]

        yield {
            "bars_ago": i,
            "first": a,
            "second": b,
            "third": c,
            "time": df.index[-i]
        }
def scan_window(df, size):

    """
    Sliding window scanner.
    """

    start = scan_start()

    max_scan = min(
        PATTERN_LOOKBACK,
        len(df) - start + 1,
    )

    for i in range(start, start + max_scan):

        window = df.iloc[-i-size+1:-i+1]

        if len(window) == size:
            yield {
                "bars_ago": i,
                "window": window,
                "time": df.index[-i],
            }
def build_pattern(
    pattern,
    engine,
    direction,
    candle,
    bars_ago,
    strength,
    confidence=None,
    entry=None,
    stop=None,
    take_profit=None,
    pattern_type="single",
):
    direction = direction.upper()
    confidence = max(
        strength,
        min(
            100,
            round(strength * 1.1)
        )
    )
    pattern_time = getattr(
        candle,
        "Index",
        getattr(candle, "name", None),
    )
    return {

        "pattern": pattern,

        "engine": engine,

        "direction": direction,

        "bars_ago": bars_ago,

        "strength": strength,

        "confidence": confidence,

        "time": pattern_time,

        "price": candle.close,
        "candle": candle,
        "engine_version": 2,
        "type": pattern_type,
        "priority": PATTERN_PRIORITY.get(pattern,50),
        "entry": entry,
        "stop": stop,
        "take_profit": take_profit,

        "pattern_id": (
            f"{engine}_"
            f"{direction}_"
            f"{bars_ago}_"
            f"{pattern_time}"
        )
    }
def pattern_age(pattern):

    return pattern["bars_ago"]


def is_fresh(pattern):

    return pattern["bars_ago"] <= MAX_PATTERN_AGE
def sort_patterns(patterns):

    return sorted(

        patterns,

        key=lambda p: (

            p["priority"],

            p["strength"],

            p["confidence"],

            p.get("volume_score", 0),

            -p["bars_ago"]

        ),

        reverse=True
    )
def recent_patterns(patterns):

    return [

        p

        for p in patterns

        if is_fresh(p)

    ]
def filter_fresh_patterns(patterns):
    """
    Keep only fresh patterns and sort them
    from highest quality to lowest.
    """

    return sort_patterns(
        recent_patterns(patterns)
    )
def swing_low(df, lookback=5, bars_ago=0):

    end = len(df) - bars_ago

    start = max(0, end - lookback)

    return float(df.low.iloc[start:end].min())


def swing_high(df, lookback=5, bars_ago=0):

    end = len(df) - bars_ago

    start = max(0, end - lookback)

    return float(df.high.iloc[start:end].max())
def pivot_low(df, left=2, right=2, bars_ago=2):
    """
    Most recent confirmed swing low.
    """

    signal = len(df) - bars_ago

    for i in range(signal - right - 1, left - 1, -1):

        low = df.low.iloc[i]

        if (
            low < df.low.iloc[i-left:i].min()
            and
            low < df.low.iloc[i+1:i+right+1].min()
        ):
            return float(low)

    return swing_low(df, 10, bars_ago)


def pivot_high(df, left=2, right=2, bars_ago=2):
    """
    Most recent confirmed swing high.
    """

    signal = len(df) - bars_ago

    for i in range(signal - right - 1, left - 1, -1):

        high = df.high.iloc[i]

        if (
            high > df.high.iloc[i-left:i].max()
            and
            high > df.high.iloc[i+1:i+right+1].max()
        ):
            return float(high)

    return swing_high(df, 10, bars_ago)