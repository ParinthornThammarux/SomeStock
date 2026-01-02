"""
pages/custom_content.py - Custom analysis page (ATR-based Support/Resistance ZONES)
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from core.data_fetch import fetch_stock_data


# ----------------------------
# Helpers
# ----------------------------
def get_cols(df):
    close_col = "close" if "close" in df.columns else "Close"
    open_col = "open" if "open" in df.columns else "Open"
    high_col = "high" if "high" in df.columns else "High"
    low_col = "low" if "low" in df.columns else "Low"
    return open_col, high_col, low_col, close_col


def calculate_atr(df, period=14):
    """Average True Range (ATR)"""
    _, high_col, low_col, close_col = get_cols(df)
    high = df[high_col]
    low = df[low_col]
    close = df[close_col]

    prev_close = close.shift(1)
    tr = np.maximum(high - low, np.abs(high - prev_close))
    tr = np.maximum(tr, np.abs(low - prev_close))

    return tr.rolling(window=period).mean()


def find_pivots(df, pivot_strength=4, use_hl=True):
    """
    Confirmed pivots:
    pivot_strength bars on both sides must confirm the local high/low.
    If use_hl=True: pivots use High/Low (stronger S/R structure).
    Else: uses Close.
    """
    _, high_col, low_col, close_col = get_cols(df)

    if use_hl:
        highs = df[high_col].values
        lows = df[low_col].values
    else:
        c = df[close_col].values
        highs = c
        lows = c

    n = len(df)
    L = pivot_strength
    R = pivot_strength

    pivot_highs = []  # (idx, price)
    pivot_lows = []   # (idx, price)

    for i in range(L, n - R):
        hwin = highs[i - L : i + R + 1]
        lwin = lows[i - L : i + R + 1]
        hi = highs[i]
        lo = lows[i]

        # Confirmed pivot high
        if hi == np.max(hwin):
            pivot_highs.append((i, float(hi)))

        # Confirmed pivot low
        if lo == np.min(lwin):
            pivot_lows.append((i, float(lo)))

    return pivot_highs, pivot_lows


# ----------------------------
# ATR-adaptive Zone Logic
# ----------------------------
def _pivot_to_zone_key(pivot_type: str) -> str:
    # keep separate pools to reduce mixing highs and lows
    return "resistance" if pivot_type == "high" else "support"


def build_zones_from_pivots(
    df,
    lookback_bars=300,
    pivot_strength=4,
    atr_period=14,
    atr_width_mult=1.0,
    min_confirmations=3,
    use_hl_for_pivots=True,
    max_zones_per_side=6,
):
    """
    Build ATR-adaptive zones by clustering pivot highs/lows.

    Zone rules:
    - Zones are built by grouping pivots whose total price range (zone_high - zone_low)
      remains within zone_width, where zone_width = ATR_current * atr_width_mult.
    - Zones expand dynamically (update zone_low/zone_high) when new pivots confirm them.
    - Zones become visible only after min_confirmations touches.
    - Zones extend to the right (we will draw rectangles from first_touch_time -> last_time).
    """
    if df is None or len(df) < max(50, pivot_strength * 2 + 10):
        return []

    df_sub = df.iloc[max(0, len(df) - lookback_bars):].copy()
    base_offset = len(df) - len(df_sub)

    atr = calculate_atr(df_sub, atr_period)
    # Use last ATR as volatility scaler
    atr_current = float(atr.iloc[-1]) if not atr.empty and not np.isnan(atr.iloc[-1]) else float(np.std(df_sub[get_cols(df_sub)[3]].values) * 0.5)
    if atr_current <= 0:
        atr_current = float(np.std(df_sub[get_cols(df_sub)[3]].values) * 0.5)

    zone_width = max(atr_current * atr_width_mult, 1e-6)

    pivot_highs, pivot_lows = find_pivots(df_sub, pivot_strength=pivot_strength, use_hl=use_hl_for_pivots)

    # Combine pivots in chronological order so zones "form" over time
    pivots = [(i, p, "high") for i, p in pivot_highs] + [(i, p, "low") for i, p in pivot_lows]
    pivots.sort(key=lambda x: x[0])  # by index/time

    zones = []
    # zone object:
    # {
    #   "side": "support"|"resistance",
    #   "low": float,
    #   "high": float,
    #   "touches": int,
    #   "first_idx": int,
    #   "last_idx": int,
    #   "pivots": [(idx, price), ...]
    # }

    for (idx, price, ptype) in pivots:
        side = _pivot_to_zone_key(ptype)

        # Try assign to an existing zone of same side:
        # "statistically valid area": if adding pivot keeps total range within zone_width
        best_zone = None
        best_cost = None

        for z in zones:
            if z["side"] != side:
                continue

            new_low = min(z["low"], price)
            new_high = max(z["high"], price)

            if (new_high - new_low) <= zone_width:
                # choose the tightest (smallest expanded range) as best fit
                cost = (new_high - new_low)
                if best_cost is None or cost < best_cost:
                    best_cost = cost
                    best_zone = z

        if best_zone is not None:
            best_zone["low"] = min(best_zone["low"], price)
            best_zone["high"] = max(best_zone["high"], price)
            best_zone["touches"] += 1
            best_zone["last_idx"] = idx
            best_zone["pivots"].append((idx, price))
        else:
            zones.append(
                {
                    "side": side,
                    "low": price,
                    "high": price,
                    "touches": 1,
                    "first_idx": idx,
                    "last_idx": idx,
                    "pivots": [(idx, price)],
                }
            )

    # Filter zones by confirmations
    zones = [z for z in zones if z["touches"] >= min_confirmations]

    # Rank zones (more touches + more recent last touch + bigger time span)
    nsub = len(df_sub)

    def score(z):
        recency = z["last_idx"] / max(1, nsub)
        span = (z["last_idx"] - z["first_idx"])
        return (z["touches"] * 2.0) + recency + (min(span, 200) / 200.0)

    zones.sort(key=score, reverse=True)

    # Keep top zones per side
    support = [z for z in zones if z["side"] == "support"][:max_zones_per_side]
    resist = [z for z in zones if z["side"] == "resistance"][:max_zones_per_side]
    zones = support + resist

    # Convert indices back to full df space
    for z in zones:
        z["first_idx"] += base_offset
        z["last_idx"] += base_offset
        z["pivots"] = [(i + base_offset, p) for (i, p) in z["pivots"]]

    return zones


def hex_to_rgba(hex_color: str, alpha: float):
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) != 6:
        return f"rgba(255,255,255,{alpha})"
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def add_zones_as_rectangles(
    fig,
    df,
    zones,
    support_hex="#3B82F6",
    resistance_hex="#EF4444",
    neutral_hex="#A3A3A3",
    fill_alpha=0.20,
    line_alpha=0.65,
):
    """
    Draw zones as plotly layout shapes (rectangles) that extend to the right.
    Color changes dynamically based on current price position:
    - price above zone -> support color
    - price below zone -> resistance color
    - price inside zone -> neutral color
    """
    _, _, _, close_col = get_cols(df)
    last_close = float(df[close_col].iloc[-1])
    x_end = df.index[-1]

    for z in zones:
        zlow = float(z["low"])
        zhigh = float(z["high"])
        x_start = df.index[int(z["first_idx"])]

        # Dynamic color by current price position
        if last_close > zhigh:
            base = support_hex
            role = "Support"
        elif last_close < zlow:
            base = resistance_hex
            role = "Resistance"
        else:
            base = neutral_hex
            role = "In-Zone"

        fill = hex_to_rgba(base, fill_alpha)
        line = hex_to_rgba(base, line_alpha)

        # Rectangle zone
        fig.add_shape(
            type="rect",
            xref="x",
            yref="y",
            x0=x_start,
            x1=x_end,
            y0=zlow,
            y1=zhigh,
            fillcolor=fill,
            line=dict(color=line, width=1),
            layer="below",
        )

        # Invisible trace just to get legend + hover text
        mid = (zlow + zhigh) / 2.0
        fig.add_trace(
            go.Scatter(
                x=[x_start, x_end],
                y=[mid, mid],
                mode="lines",
                line=dict(color="rgba(0,0,0,0)", width=0),
                name=f"{role} Zone ({z['touches']} pivots)",
                hovertemplate=(
                    f"{role} Zone<br>"
                    f"Touches: {z['touches']}<br>"
                    f"Low: {zlow:.2f}<br>"
                    f"High: {zhigh:.2f}<extra></extra>"
                ),
                showlegend=True,
            )
        )


def add_moving_averages(fig, df, close_col, ma_periods=(20, 50, 200)):
    for p in ma_periods:
        if len(df) >= p:
            ma = df[close_col].rolling(p).mean()
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=ma,
                    mode="lines",
                    name=f"MA{p}",
                    line=dict(width=1),
                    opacity=0.8,
                )
            )


def add_fibonacci(fig, df, high_col, low_col, lookback=200):
    if len(df) < 10:
        return

    sub = df.iloc[max(0, len(df) - lookback):]
    swing_high = float(sub[high_col].max())
    swing_low = float(sub[low_col].min())
    if swing_high <= swing_low:
        return

    levels = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
    for r in levels:
        price = swing_high - (swing_high - swing_low) * r
        fig.add_trace(
            go.Scatter(
                x=[df.index[0], df.index[-1]],
                y=[price, price],
                mode="lines",
                name=f"Fib {int(r*100)}%",
                line=dict(width=1, dash="dot"),
                opacity=0.55,
                hovertemplate=f"Fib {int(r*100)}%<br>Price: %{{y:.2f}}<extra></extra>",
            )
        )


# ----------------------------
# Page
# ----------------------------
def render():
    st.title("⚙️ Custom Analysis")
    st.markdown("---")

    col_config, col_analysis = st.columns([1, 3])

    with col_config:
        st.subheader("Configuration")

        symbol = st.text_input("Stock Symbol:", value="AAPL")
        period = st.selectbox("Period:", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max"], index=3)
        timeframe = st.selectbox("Timeframe:", ['1h',"1d", "1wk", "1mo"], index=0, help="Interval for candlestick chart")

        st.markdown("### Zone Logic Settings")
        lookback_bars = st.slider("Bars to Apply (Lookback)", 100, 1200, 300, step=50)
        pivot_strength = st.slider("Pivot Strength", 2, 12, 4)
        min_confirmations = st.slider("Min Pivot Confirmation", 2, 8, 3)
        atr_period = st.slider("ATR Period", 5, 50, 14)
        atr_width_mult = st.slider("Zone Width (ATR Multiplier)", 0.3, 3.0, 1.0, step=0.1)
        max_zones = st.slider("Max Zones per Side", 1, 10, 6)

        st.markdown("### Styling")
        support_color = st.color_picker("Support Color (price above zone)", "#3B82F6")
        resistance_color = st.color_picker("Resistance Color (price below zone)", "#EF4444")
        neutral_color = st.color_picker("Neutral (in-zone) Color", "#A3A3A3")
        fill_alpha = st.slider("Zone Fill Transparency", 0.05, 0.60, 0.20, step=0.05)

        st.markdown("### Confirmations (optional)")
        show_ma = st.checkbox("Show Moving Averages", value=True)
        show_fib = st.checkbox("Show Fibonacci Retracement", value=False)
        use_hl = st.checkbox("Use High/Low for pivots (recommended)", value=True)

    with col_analysis:
        if symbol:
            with st.spinner(f"Loading {symbol}..."):
                try:
                    stock_data = fetch_stock_data(symbol, period=period, interval=timeframe)

                    if stock_data and stock_data.has_data():
                        df = stock_data.price_history
                        open_col, high_col, low_col, close_col = get_cols(df)
                        close_prices = df[close_col].values

                        fig = go.Figure()

                        # Candlestick chart
                        fig.add_trace(
                            go.Candlestick(
                                x=df.index,
                                open=df[open_col],
                                high=df[high_col],
                                low=df[low_col],
                                close=df[close_col],
                                name="OHLC",
                            )
                        )

                        # Build + draw zones
                        zones = build_zones_from_pivots(
                            df=df,
                            lookback_bars=lookback_bars,
                            pivot_strength=pivot_strength,
                            atr_period=atr_period,
                            atr_width_mult=atr_width_mult,
                            min_confirmations=min_confirmations,
                            use_hl_for_pivots=use_hl,
                            max_zones_per_side=max_zones,
                        )

                        add_zones_as_rectangles(
                            fig,
                            df,
                            zones,
                            support_hex=support_color,
                            resistance_hex=resistance_color,
                            neutral_hex=neutral_color,
                            fill_alpha=fill_alpha,
                            line_alpha=min(0.95, fill_alpha + 0.35),
                        )

                        # Optional confirmations
                        if show_ma:
                            add_moving_averages(fig, df, close_col, ma_periods=(20, 50, 200))
                        if show_fib:
                            add_fibonacci(fig, df, high_col, low_col, lookback=min(300, len(df)))

                        fig.update_layout(
                            title=f"{symbol} Support/Resistance Zones ({timeframe.upper()})",
                            height=650,
                            hovermode="x unified",
                            xaxis_rangeslider_visible=False,
                            template="plotly_dark",
                            xaxis_title="Date",
                            yaxis_title="Price ($)",
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        # Statistics
                        st.markdown("### Statistics")
                        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)

                        with stats_col1:
                            st.metric("Latest Price", f"${close_prices[-1]:.2f}")
                        with stats_col2:
                            st.metric("52W High", f"${df[high_col].max():.2f}")
                        with stats_col3:
                            st.metric("52W Low", f"${df[low_col].min():.2f}")
                        with stats_col4:
                            volatility = df[close_col].pct_change().std() * 100
                            st.metric("Volatility", f"{volatility:.2f}%")

                    else:
                        st.error(f"Could not fetch data for {symbol}")

                except Exception as e:
                    st.error(f"Error: {e}")
