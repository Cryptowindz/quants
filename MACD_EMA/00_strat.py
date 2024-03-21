import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from typing import NamedTuple
from quantfreedom.enums import CandleBodyType
from quantfreedom.helper_funcs import dl_ex_candles
from quantfreedom.indicators.tv_indicators import macd_tv, ema_tv

np.set_printoptions(formatter={"float_kind":"{:,.2f}".format})

candles = dl_ex_candles(
    exchange='mufex',
    symbol='BTCUSDT',
    timeframe='5m',
    candles_to_dl=3000
)

datetimes = candles[:,CandleBodyType.Timestamp].astype('datetime64[ms]')
closing_prices = candles[:,CandleBodyType.Close]
low_prices = candles[:,CandleBodyType.Low]

macd_below = 0
fast_length = 12
slow_length = 26
signal_smoothing = 9
ema_length = 400

histogram, macd, signal = macd_tv(
    source=closing_prices,
    fast_length=fast_length,
    slow_length=slow_length,
    signal_smoothing = signal_smoothing
)

ema = ema_tv(
    source=closing_prices,
    length=ema_length
)

prev_macd = np.roll(macd, 1)
prev_macd[0] = np.nan

prev_signal = np.roll(signal, 1)
prev_signal[0] = np.nan

macd_below_signal = prev_macd < prev_signal
macd_above_signal = macd > signal
low_price_below_ema = low_prices > ema
macd_below_number = macd < macd_below

entries = (
    (low_price_below_ema == True)
    & (macd_below_signal == True)
    & (macd_above_signal == True)
    & (macd_below_number == True)
)

entry_signals = np.where(entries, macd,np.nan)

fig = go.Figure()

fig = make_subplots(
    cols=1,
    rows=2,
    shared_xaxes=True,
    subplot_titles=["Candles", "MACD"],
    row_heights=[0.6, 0.4],
    vertical_spacing=0.1
)

#Candlestick chart for pricing
fig.append_trace(
    go.Candlestick(
        x=datetimes,
        open=candles[:,CandleBodyType.Open],
        high=candles[:,CandleBodyType.High],
        low=candles[:,CandleBodyType.Low],
        close=candles[:,CandleBodyType.Close],
        name="Candles",
    ),
    col=1,
    row=1,
)
fig.append_trace(
    go.Scatter(
        x=datetimes,
        y=ema,
        name="EMA",
        line_color="yellow",
    ),
    col=1,
    row=1,
)
ind_shift = np.roll(histogram,1)
ind_shift[0] = np.nan
colors = np.where(
    histogram >= 0,
    np.where(ind_shift < histogram, "#26A69A", "#B2DFDB"),
    np.where(ind_shift < histogram, "#FFCDD2", "#FF5252"),
)
fig.append_trace(
    go.Bar(
        x=datetimes,
        y=histogram,
        name="histogram",
        marker_color=colors,
    ),
    row=2,
    col=1,
)
fig.append_trace(
    go.Scatter(
        x=datetimes,
        y=macd,
        name="macd",
        line_color="#2962FF",
    ),
    row=2,
    col=1,
)
fig.append_trace(
    go.Scatter(
        x=datetimes,
        y=macd,
        name="signal",
        line_color="#FF6D00",
    ),
    row=2,
    col=1,
)
fig.append_trace(
    go.Scatter(
        x=datetimes,
        y=entry_signals,
        mode="markers",
        name="entries",
        marker=dict(
            size=12,
            symbol="circle",
            color="#00F6FF",
            line=dict(
                width=1,
                color="DarkSlateGrey",
            ),
        ),
    ),
    row=2,
    col=1,
)

#Update actions and show plot
fig.update_layout(
    height=800,
    xaxis_rangeslider_visible=False,
)
fig.show()