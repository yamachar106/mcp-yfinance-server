from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import yfinance as yf
import pandas as pd
from typing import Optional

app = FastAPI(
    title="yfinance API Server",
    description="Yahoo Finance データ取得 API（Railway 版）",
    version="1.0.0"
)

@app.get("/")
def home():
    """
    トップページ - 利用可能なエンドポイント一覧
    """
    return {
        "message": "yfinance API Server - Powered by Railway",
        "status": "running",
        "endpoints": {
            "/": "このページ（エンドポイント一覧）",
            "/health": "ヘルスチェック",
            "/api/info/{symbol}": "株式情報取得（企業名、時価総額、セクターなど）",
            "/api/history/{symbol}": "株価履歴取得（デフォルト1ヶ月）",
            "/api/history/{symbol}?period={period}": "株価履歴取得（期間指定：1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max）",
            "/api/financials/{symbol}": "財務諸表取得",
            "/api/earnings/{symbol}": "決算情報取得",
            "/api/holders/{symbol}": "株主情報取得",
            "/api/recommendations/{symbol}": "アナリスト推奨取得",
            "/api/calendar/{symbol}": "企業カレンダー取得",
            "/docs": "API ドキュメント（Swagger UI）"
        }
    }

@app.get("/health")
def health_check():
    """
    ヘルスチェック用エンドポイント
    """
    return {"status": "healthy", "service": "yfinance-api"}

@app.get("/api/info/{symbol}")
def get_info(symbol: str):
    """
    株式情報を取得
    
    Args:
        symbol: 株式シンボル（例: AAPL, TSLA, MSFT）
    
    Returns:
        企業名、時価総額、セクター、現在価格など
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info
        
        if not info or len(info) == 0:
            raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found")
        
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching info: {str(e)}")

@app.get("/api/history/{symbol}")
def get_history(symbol: str, period: str = "1mo"):
    """
    株価履歴を取得
    
    Args:
        symbol: 株式シンボル
        period: 期間（1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max）
    
    Returns:
        日付、始値、高値、安値、終値、出来高のリスト
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        hist = ticker.history(period=period)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No history data for '{symbol}'")
        
        # DataFrame を JSON 形式に変換
        hist_dict = hist.reset_index().to_dict(orient='records')
        
        # 日付を文字列に変換
        for record in hist_dict:
            if 'Date' in record:
                record['Date'] = record['Date'].strftime('%Y-%m-%d')
        
        return {
            "symbol": symbol.upper(),
            "period": period,
            "count": len(hist_dict),
            "data": hist_dict
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")

@app.get("/api/financials/{symbol}")
def get_financials(symbol: str):
    """
    財務諸表を取得
    
    Args:
        symbol: 株式シンボル
    
    Returns:
        年次財務諸表データ
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        financials = ticker.financials
        
        if financials is None or financials.empty:
            raise HTTPException(status_code=404, detail=f"No financial data for '{symbol}'")
        
        return {
            "symbol": symbol.upper(),
            "data": financials.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching financials: {str(e)}")

@app.get("/api/earnings/{symbol}")
def get_earnings(symbol: str):
    """
    決算情報を取得
    
    Args:
        symbol: 株式シンボル
    
    Returns:
        四半期決算データ
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        earnings = ticker.earnings
        
        if earnings is None or earnings.empty:
            raise HTTPException(status_code=404, detail=f"No earnings data for '{symbol}'")
        
        return {
            "symbol": symbol.upper(),
            "data": earnings.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching earnings: {str(e)}")

@app.get("/api/holders/{symbol}")
def get_holders(symbol: str):
    """
    株主情報を取得
    
    Args:
        symbol: 株式シンボル
    
    Returns:
        主要株主と機関投資家の保有情報
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        
        major_holders = ticker.major_holders
        institutional_holders = ticker.institutional_holders
        
        result = {"symbol": symbol.upper()}
        
        if major_holders is not None and not major_holders.empty:
            result["major_holders"] = major_holders.to_dict()
        
        if institutional_holders is not None and not institutional_holders.empty:
            result["institutional_holders"] = institutional_holders.to_dict()
        
        if len(result) == 1:  # symbol のみ
            raise HTTPException(status_code=404, detail=f"No holder data for '{symbol}'")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching holders: {str(e)}")

@app.get("/api/recommendations/{symbol}")
def get_recommendations(symbol: str):
    """
    アナリスト推奨を取得
    
    Args:
        symbol: 株式シンボル
    
    Returns:
        アナリストの推奨データ
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        recommendations = ticker.recommendations
        
        if recommendations is None or recommendations.empty:
            raise HTTPException(status_code=404, detail=f"No recommendations for '{symbol}'")
        
        return {
            "symbol": symbol.upper(),
            "data": recommendations.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recommendations: {str(e)}")

@app.get("/api/calendar/{symbol}")
def get_calendar(symbol: str):
    """
    企業カレンダーを取得（決算発表日など）
    
    Args:
        symbol: 株式シンボル
    
    Returns:
        企業カレンダー情報
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        calendar = ticker.calendar
        
        if calendar is None or (isinstance(calendar, pd.DataFrame) and calendar.empty):
            raise HTTPException(status_code=404, detail=f"No calendar data for '{symbol}'")
        
        # DataFrameの場合は辞書に変換
        if isinstance(calendar, pd.DataFrame):
            calendar_dict = calendar.to_dict()
        else:
            calendar_dict = calendar
        
        return {
            "symbol": symbol.upper(),
            "data": calendar_dict
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching calendar: {str(e)}")

# Railway 用のハンドラー（必須）
handler = app
