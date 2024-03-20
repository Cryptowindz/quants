import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from typing import NamedTuple
from quantfreedom.enums import CandleBodyType
from quantfreedom.helper_funcs import dl_ex_candles
from quantfreedom.indicators.tv_indicators import macd_tv, ema_tv

np.set_printoptions(formatter={"float_kind":"{:,.2f}".format})


