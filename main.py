from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import ta

app = FastAPI()

class OhlcvInput(BaseModel):
    symbol: str
    ohlcv: list  # [{"t":..., "o":..., "h":..., "l":..., "c":..., "v":...}, ...]

@app.post("/analyze")
def analyze(data: OhlcvInput):
    df = pd.DataFrame(data.ohlcv)
    df['rsi'] = ta.momentum.RSIIndicator(df['c'], window=14).rsi()
    df['ema10'] = ta.trend.EMAIndicator(df['c'], window=10).ema_indicator()
    df['ema20'] = ta.trend.EMAIndicator(df['c'], window=20).ema_indicator()
    macd = ta.trend.MACD(df['c'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()

    latest = df.iloc[-1]
    signal = (
        "continueDowntrend" if latest.ema10 < latest.ema20 and latest.rsi < 40 else
        "possibleUptrend" if latest.ema10 > latest.ema20 and latest.rsi > 60 else
        "neutral"
    )

    return {
        "symbol": data.symbol,
        "rsi": float(latest.rsi),
        "ema10": float(latest.ema10),
        "ema20": float(latest.ema20),
        "macd": float(latest.macd),
        "macd_signal": float(latest.macd_signal),
        "signal": signal
    }
