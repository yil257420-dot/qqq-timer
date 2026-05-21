import requests
import os
import time
import datetime

def run():
    # 1. 周末保护：周末休市不发送
    if datetime.datetime.now().weekday() >= 5:
        return

    # 2. 强力获取数据：直接请求雅虎 API
    session = requests.Session()
    url = "https://query1.finance.yahoo.com/v8/finance/chart/QQQ?range=1d&interval=1m"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    data = None
    # 尝试抓取数据
    try:
        res = session.get(url, headers=headers, timeout=15).json()
        if 'chart' in res and res['chart']['result']:
            data = res['chart']['result'][0]['meta']
    except Exception:
        return

    if not data or 'regularMarketPrice' not in data:
        return

    # 3. 计算涨跌幅
    price = data['regularMarketPrice']
    prev = data['previousClose']
    chg = (price - prev) / prev * 100
    
    # 4. 构建推送内容
    msg = "QQQ 实时: {:.2f}, 涨跌: {:.2f}%".format(price, chg)
    if chg < 0:
        abs_chg = abs(chg)
        amt = 30 if abs_chg <= 2 else (50 if abs_chg <= 4 else 100)
        msg += "。策略：建议立即买入 {} 美元。".format(amt)
    else:
        msg += "。策略：当前未下跌，无需操作。"

    # 5. 最终推送：使用刚才确认成功的链路
    key = os.environ.get("PUSHDEER_KEY")
    if key and key.strip():
        session.get("https://api2.pushdeer.com/message/push", 
                    params={"pushkey": key, "text": msg}, timeout=10)

if __name__ == "__main__":
    run()
