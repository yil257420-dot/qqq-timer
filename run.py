import requests
import json
import os
import datetime

def run():
    # 1. 周末休市检查
    if datetime.datetime.now().weekday() >= 5:
        return

    # 2. 直接使用原始 HTTP 请求获取数据，完全避开 yfinance 版本冲突
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/QQQ?range=1d&interval=1m"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10).json()
        
        # 解析数据
        quote = res['chart']['result'][0]['meta']
        current_price = quote['regularMarketPrice']
        prev_close = quote['previousClose']
        
        # 3. 计算涨跌幅
        chg = (current_price - prev_close) / prev_close * 100
        
        # 4. 中文策略逻辑
        msg = "QQQ 实时价格: {:.2f}, 涨跌幅: {:.2f}%".format(current_price, chg)
        
        if chg < 0:
            abs_chg = abs(chg)
            amt = 30 if abs_chg <= 2 else (50 if abs_chg <= 4 else 100)
            msg += "。策略：建议立即买入 {} 美元。".format(amt)
        else:
            msg += "。策略：当前未下跌，无需操作。"

        # 5. 推送
        key = os.environ.get("PUSHDEER_KEY")
        if key:
            requests.get("https://api2.pushdeer.com/message/push", 
                         params={"pushkey": key, "text": msg}, timeout=10)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
