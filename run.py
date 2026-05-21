import requests
import os
import datetime
import time

def run():
    # 1. 交易日判断 (美东时间：需排除美股法定休市日，此处使用简单工作日判断)
    if datetime.datetime.now().weekday() >= 5:
        return

    # 2. 深度重试逻辑：开盘时网络可能有波动，允许 3 次重试
    session = requests.Session()
    url = "https://query1.finance.yahoo.com/v8/finance/chart/QQQ?range=1d&interval=1m"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    data = None
    for i in range(3):
        try:
            res = session.get(url, headers=headers, timeout=15).json()
            if 'chart' in res and res['chart']['result']:
                data = res['chart']['result'][0]['meta']
                break
        except Exception:
            time.sleep(2) # 失败等待2秒后重试
            
    if not data:
        print("Error: 数据获取失败")
        return

    current_price = data['regularMarketPrice']
    prev_close = data['previousClose']
    chg = (current_price - prev_close) / prev_close * 100
    
    # 3. 策略逻辑
    msg = f"QQQ 实时: {current_price:.2f}, 涨跌: {chg:.2f}%"
    if chg < 0:
        amt = 30 if abs(chg) <= 2 else (50 if abs(chg) <= 4 else 100)
        msg += f"。策略：建议买入 {amt} 美元。"
    else:
        msg += "。策略：今日上涨，无需操作。"

    # 4. 推送
    key = os.environ.get("PUSHDEER_KEY")
    if key:
        session.get("https://api2.pushdeer.com/message/push", 
                    params={"pushkey": key, "text": msg}, timeout=10)

if __name__ == "__main__":
    run()
