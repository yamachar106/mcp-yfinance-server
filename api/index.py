from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import yfinance as yf
import pandas as pd

app = FastAPI(title="yfinance API Server")

@app.get("/")
def home():
    return {
        "message": "yfinance API Server - Powered by Vercel",
        "endpoints": {
            "/api/info/{symbol}": "株式情報取得",
            "/api/history/{symbol}": "株価履歴取得（1ヶ月）",
            "/api/financials/{symbol}": "財務諸表取得",
            "/api/earnings/{symbol}": "決算情報取得",
            "/api/holders/{symbol}": "株主情報取得"
        }
    }

@app.get("/api/info/{symbol}")
def get_info(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history/{symbol}")
def get_history(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1mo")
        # Pandas DataFrame を JSON 変換
        hist_dict = hist.reset_index().to_dict(orient='records')
        return hist_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/financials/{symbol}")
def get_financials(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        financials = ticker.financials
        return financials.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/earnings/{symbol}")
def get_earnings(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        earnings = ticker.earnings
        return earnings.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/holders/{symbol}")
def get_holders(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        holders = {
            "major_holders": ticker.major_holders.to_dict() if ticker.major_holders is not None else None,
            "institutional_holders": ticker.institutional_holders.to_dict() if ticker.institutional_holders is not None else None
        }
        return holders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Vercel 用のハンドラー
handler = app
