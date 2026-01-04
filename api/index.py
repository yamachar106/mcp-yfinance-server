from flask import Flask, request, jsonify
import yfinance as yf
import pandas as pd

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "yfinance API Server - Powered by Vercel",
        "endpoints": {
            "/api/info/<symbol>": "株式情報取得",
            "/api/history/<symbol>": "株価履歴取得（1ヶ月）",
            "/api/financials/<symbol>": "財務諸表取得",
            "/api/earnings/<symbol>": "決算情報取得"
        }
    })

@app.route('/api/info/<symbol>')
def get_info(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history/<symbol>')
def get_history(symbol):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1mo")
        # Pandas DataFrame を JSON に変換
        hist_dict = hist.reset_index().to_dict(orient='records')
        return jsonify(hist_dict)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/financials/<symbol>')
def get_financials(symbol):
    try:
        ticker = yf.Ticker(symbol)
        financials = ticker.financials
        return jsonify(financials.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/earnings/<symbol>')
def get_earnings(symbol):
    try:
        ticker = yf.Ticker(symbol)
        earnings = ticker.earnings
        return jsonify(earnings.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel 用のエントリーポイント
if __name__ == '__main__':
    app.run(debug=True)
