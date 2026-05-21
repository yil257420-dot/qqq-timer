import yfinance as yf
import requests
import os
import pandas_market_calendars as mcal
from datetime import datetime

def run():
    # 1. 智能节假日感知
    nyse = mcal.get_calendar('NYSE')
    # 检查今天是否是 NYSE 的交易日
    today = datetime.now().date()
    schedule = nyse.schedule(start_date=today, end_date=today)
    if schedule.empty:
        print("今日休市，任务终止。")
        return

    # 2. 数据获取
    ticker = yf.Ticker("QQQ")
    hist = ticker.history(period="5d")
    data = hist['Close'].dropna()
    
    # 锁定前一交易日收盘数据
    y_close = data.iloc[-1]
    b_close = data.iloc[-2]
    chg = (y_close - b_close) / b_close * 100
    
    # 3. 策略中文推送
    msg = "QQQ 上一交易日收盘: {:.2f}, 涨跌幅: {:.2f}%".format(y_close, chg)
    
    if chg < 0:
        abs_chg = abs(chg)
        amt = 30 if abs_chg <= 2 else (50 if abs_chg <= 4 else 100)
        msg += "。策略：建议买入 {} 美元。".format(amt)
    else:
        msg += "。策略：今日上涨，无需操作。"

    # 4. 执行推送
    key = os.environ.get("PUSHDEER_KEY")
    if key:
        requests.get("https://api2.pushdeer.com/message/push", 
                     params={"pushkey": key, "text": msg}, timeout=10)
    print(msg)

if __name__ == "__main__":
    run()
