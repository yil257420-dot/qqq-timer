import requests
import os
import pytz
import holidays
from datetime import datetime
import yfinance as yf

def run():
    # 1. 时令与节假日初始化
    tz = pytz.timezone('US/Eastern')
    now = datetime.now(tz)
    us_holidays = holidays.US()
    
    # 2. 节假日/周末判定
    if now.weekday() >= 5 or now.strftime('%Y-%m-%d') in us_holidays:
        msg = "【QQQ监测】今天是节假日或周末，美股不开盘。"
    else:
        # 3. 智能获取上一个交易日收盘价
        try:
            ticker = yf.Ticker("QQQ")
            hist = ticker.history(period="5d")
            prev_close = hist.iloc[-2]['Close']
            curr_price = hist.iloc[-1]['Close']
            
            pct = ((curr_price - prev_close) / prev_close) * 100
            
            # 4. 你的阶梯策略逻辑
            if pct >= 0:
                strategy = "涨幅为正，不操作。"
            elif -2.0 <= pct < 0:
                strategy = "跌幅 ≤ 2%，定投 30 美金。"
            elif -4.0 <= pct < -2.0:
                strategy = "跌幅 2%-4%，定投 50 美金。"
            else:
                strategy = "跌幅 > 4%，定投 100 美金。"
                
            msg = f"【QQQ监测】\n昨日收盘: {prev_close:.2f}\n现价: {curr_price:.2f}\n涨跌: {pct:+.2f}%\n策略: {strategy}"
        except Exception as e:
            msg = f"【系统错误】数据获取失败: {str(e)}"

    # 5. 强制推送 (is_alert='1' 确保震动提醒)
    key = os.environ.get("PUSHDEER_KEY")
    if key:
        requests.post("https://api2.pushdeer.com/message/push", 
                      data={"pushkey": key, "text": msg, "type": "markdown", "is_alert": "1"}, 
                      timeout=10)
    print(msg)

if __name__ == "__main__":
    run()