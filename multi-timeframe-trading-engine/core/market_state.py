

from config import *

from indicators.ema import ema_signal
from indicators.atr import atr_signal
from indicators.volume import volume_signal
from indicators.trend import trend_signal
from indicators.adx import adx_signal
from indicators.rsi import rsi_signal
from indicators.vwap import vwap_signal
from indicators.range import detect_range

from indicators.support_resistance import support_resistance_signal

from indicators.supply_demand import detect_supply_demand
from indicators.liquidity import detect_liquidity
from indicators.fair_value_gap import detect_fair_value_gap
from indicators.m5_structure import detect_m5_structure

from indicators.location import calculate_location

from indicators.market_regime import market_regime

from indicators.signals import MarketState


def build_market_state(

    symbol,

    timeframe,

    df,

    mode="FULL",

    bias_direction=None,

):
    # ==========================================================
    # Base Indicators (calculate first)
    # ==========================================================

    ema = ema_signal(df)
    atr = atr_signal(df)
    volume = volume_signal(df)
    trend = trend_signal(df)
    adx = adx_signal(df)
    rsi = rsi_signal(df)
    vwap = vwap_signal(df)

    # ==========================================================
    # H1 — BIAS MODE
    # ==========================================================

    if mode == "BIAS":

        regime = market_regime(

            df=df,

            ema=ema,

            adx=adx,

        )

        return MarketState(

            symbol=symbol,

            timeframe=timeframe,

            market_state=regime.state,

            market_score=regime.score,

            ema=ema,

            atr=atr,

            volume=volume,

            trend=trend,

            adx=adx,

            rsi=rsi,

            vwap=vwap,

            regime=regime,

            support=None,

            resistance=None,

            supply=None,

            demand=None,

            liquidity=None,

            fvg=None,

            location=None,

            range=None,

            bos=None,

            choch=None,

            order_block=None,

            breaker=None,

            mitigation=None,

            premium_discount=None,

        )
    # ==========================================================
    # M15 — LOCATION MODE
    # ==========================================================

    if mode == "LOCATION":

        # Location must be built from completed M15 candles only.
        closed_m15 = df.iloc[:-1].copy() if len(df) > 1 else df.copy()
        if len(closed_m15) < 30:
            closed_m15 = df.copy()

        # Recalculate location-layer indicators from the closed source so a
        # forming M15 candle can never create/mutate a zone or FVG.
        ema_loc = ema_signal(closed_m15)
        atr_loc = atr_signal(closed_m15)
        volume_loc = volume_signal(closed_m15)
        trend_loc = trend_signal(closed_m15)
        adx_loc = adx_signal(closed_m15)
        rsi_loc = rsi_signal(closed_m15)
        vwap_loc = vwap_signal(closed_m15)

        sr = support_resistance_signal(
            closed_m15,
            atr_loc.atr,
            adx_loc,
        )


        sd = detect_supply_demand(
            closed_m15,
            atr_loc.atr,
            already_closed=True,
        )


        range_signal = detect_range(
            closed_m15,
            atr_loc.atr,
        )


        liquidity = (

            detect_liquidity(
                closed_m15,
                atr_loc.atr,
                already_closed=True,
            )

            if ENABLE_LIQUIDITY_ZONES

            else None

        )


        # FVG will be added here
        fvg = detect_fair_value_gap(
            closed_m15,
            atr_loc.atr,
            already_closed=True,
        )


        # Use location context.
        regime = market_regime(
            df=closed_m15,
            ema=ema_loc,
            adx=adx_loc,
        )

        location_regime = regime


        if bias_direction == "BUY":

            location_regime = type(
                "LocationRegime",
                (),
                {
                    "state": "STRONG_BULL"
                },
            )()


        elif bias_direction == "SELL":

            location_regime = type(
                "LocationRegime",
                (),
                {
                    "state": "STRONG_BEAR"
                },
            )()


        location = calculate_location(

            location_regime,

            sr,

            sd,

            range_signal,

            liquidity,

            fvg,

            bias_direction=bias_direction,

        )


        return MarketState(

            symbol=symbol,

            timeframe=timeframe,

            market_state=regime.state,

            market_score=regime.score,

            ema=ema_loc,

            atr=atr_loc,

            volume=volume_loc,

            trend=trend_loc,

            adx=adx_loc,

            rsi=rsi_loc,

            vwap=vwap_loc,

            regime=regime,

            support=sr.support,

            resistance=sr.resistance,

            supply=sd.supply,

            demand=sd.demand,

            liquidity=liquidity,

            fvg=fvg,

            location=location,

            range=range_signal,

            bos=None,

            choch=None,

            order_block=None,

            breaker=None,

            mitigation=None,

            premium_discount=None,

        )
    # ==========================================================
    # M5 — CONFIRMATION MODE
    # ==========================================================

    if mode == "CONFIRMATION":

        m5_structure = detect_m5_structure(
            df,
            atr.atr,
            lookback=M5_STRUCTURE_LOOKBACK,
            swing_left=M5_SWING_LEFT,
            swing_right=M5_SWING_RIGHT,
            sweep_lookback=M5_SWEEP_LOOKBACK,
            sweep_max_age=M5_SWEEP_MAX_AGE,
            bos_score=M5_BOS_SCORE,
            choch_score=M5_CHOCH_SCORE,
            sweep_score=M5_SWEEP_SCORE,
            displacement_score=M5_DISPLACEMENT_SCORE,
        )

        regime = market_regime(

            df=df,

            ema=ema,

            adx=adx,

        )


        return MarketState(

            symbol=symbol,

            timeframe=timeframe,

            market_state=regime.state,

            market_score=regime.score,

            ema=ema,

            atr=atr,

            volume=volume,

            trend=trend,

            adx=adx,

            rsi=rsi,

            vwap=vwap,

            regime=regime,

            support=None,

            resistance=None,

            supply=None,

            demand=None,

            liquidity=None,

            fvg=None,

            location=None,

            range=None,

            bos=None,

            choch=None,

            m5_structure=m5_structure,

            order_block=None,

            breaker=None,

            mitigation=None,

            premium_discount=None,

        )

    # ==========================================================
    # Higher-level Analysis
    # ==========================================================

    sr = support_resistance_signal(
        df,
        atr.atr,
        adx,
    )

    sd = detect_supply_demand(
        df,
        atr.atr,
    )

    range_signal = detect_range(
        df,
        atr.atr,
    )

    liquidity = (
        detect_liquidity(df, atr.atr)
        if ENABLE_LIQUIDITY_ZONES
        else None
    )

    fvg = detect_fair_value_gap(df, atr.atr)

    regime = market_regime(
        df=df,
        ema=ema,
        adx=adx,
    )


    location = calculate_location(

        regime,

        sr,

        sd,

        range_signal,

        liquidity,

        fvg,

        bias_direction=bias_direction,

    )
    

    if PRINT_MARKET_STATE:

        print()

        print("=" * 45)
        print(symbol)
        print("=" * 45)

        print(f"Market State : {regime.state}")
        print(f"Trend        : {trend.trend}")
        print(f"EMA Trend    : {ema.trend}")

        print(f"ADX          : {adx.adx:.2f}")
        print(f"RSI          : {rsi.rsi:.2f}")

        print(f"VWAP         : {vwap.vwap:.5f}")
        print(f"Volume x     : {volume.relative:.2f}")

        print(f"ATR          : {atr.atr:.5f}")

        if liquidity is not None:
            print(f"Liquidity    : {liquidity.score:.1f}")
            print(f"Sell Sweep   : {liquidity.swept_sell_side}")
            print(f"Buy Sweep    : {liquidity.swept_buy_side}")

        if PRINT_FVG:
            print(f"FVG Score    : {fvg.score:.1f}")
            print(f"Bullish FVG  : {fvg.near_bullish}")
            print(f"Bearish FVG  : {fvg.near_bearish}")

        print("=" * 45)

    return MarketState(

        symbol=symbol,

        timeframe=timeframe,

        market_state=regime.state,

        market_score=regime.score,

        ema=ema,

        atr=atr,

        volume=volume,

        trend=trend,

        adx=adx,

        rsi=rsi,

        vwap=vwap,

        bos=None,

        choch=None,

        liquidity=liquidity,

        fvg=fvg,

        order_block=None,

        breaker=None,

        mitigation=None,

        premium_discount=None,
        regime=regime,

        support=sr.support,

        resistance=sr.resistance,

        supply=sd.supply,

        demand=sd.demand,

        location=location,

        range=range_signal,

    )