import yfinance as yf
import requests
import os
import pandas_market_calendars as mcal
from datetime import datetime

def run():
    # 1. 智能判断节假日
    nyse = mcal.get_calendar('NYSE')
    today = datetime.now().date()
    schedule = nyse.schedule(start_date=today, end_date=today)
    if schedule.empty:
        return

    # 2. 实时抓取行情
    ticker = yf.Ticker("QQQ")
    info = ticker.fast_info
    current_price = info['last_price']
    prev_close = info['previous_close']
    
    # 3. 计算涨跌幅
    chg = (current_price - prev_close) / prev_close * 100
    
    # 4. 中文策略生成
    msg = "QQQ 实时价格: {:.2f}, 涨跌幅: {:.2f}%".format(current_price, chg)
    
    if chg < 0:
        abs_chg = abs(chg)
        amt = 30 if abs_chg <= 2 else (50 if abs_chg <= 4 else 100)
        msg += "。策略：建议立即买入 {} 美元。".format(amt)
    else:
        msg += "。策略：当前未下跌，无需操作。"

    # 5. 推送指令
    key = os.environ.get("PUSHDEER_KEY")
    if key:
        requests.get("https://api2.pushdeer.com/message/push", 
                     params={"pushkey": key, "text": msg}, timeout=10)

if __name__ == "__main__":
    run()
