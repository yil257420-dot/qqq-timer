import yfinance as yf
import requests
import os

def main():
    ticker = yf.Ticker("QQQ")
    hist = ticker.history(period="5d")
    closes = hist['Close'].dropna()
    y_close = closes.iloc[-1]
    b_close = closes.iloc[-2]
    chg = (y_close - b_close) / b_close * 100
    
    key = os.environ.get("PUSHDEER_KEY")
    if not key: return
    
    msg = "Close: {:.2f}, Change: {:.2f}%".format(y_close, chg)
    if chg < 0:
        amt = 30 if abs(chg) <= 2 else (50 if abs(chg) <= 4 else 100)
        msg += ", Buy: {} USD".format(amt)
            
    requests.get("https://api2.pushdeer.com/message/push", params={"pushkey": key, "text": msg})

if __name__ == "__main__":
    main()
