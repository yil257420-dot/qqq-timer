import requests
import os
import datetime

def run():
    # 1. 基础周六日休市保护
    if datetime.datetime.now().weekday() >= 5:
        return

    # 2. 强力获取数据
    session = requests.Session()
    url = "https://query1.finance.yahoo.com/v8/finance/chart/QQQ?range=1d&interval=1m"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = session.get(url, headers=headers, timeout=15).json()
        data = res['chart']['result'][0]['meta']
        price = data['regularMarketPrice']
        prev = data['previousClose']
        chg = (price - prev) / prev * 100
    except Exception as e:
        # 如果获取失败，发送一个异常状态提醒
        send_push("【QQQ 预警】数据获取异常: " + str(e))
        return

    # 3. 核心：强制构造消息，无论涨跌
    msg = f"【QQQ 开盘监测】当前价格: {price:.2f}, 涨跌: {chg:.2f}%"
    
    if chg < 0:
        abs_chg = abs(chg)
        amt = 30 if abs_chg <= 2 else (50 if abs_chg <= 4 else 100)
        msg += f"。策略：建议买入 {amt} 美元。"
    else:
        msg += "。策略：当前无需操作。"

    # 4. 强制推送
    send_push(msg)

def send_push(text):
    key = os.environ.get("PUSHDEER_KEY")
    if key and key.strip():
        requests.get("https://api2.pushdeer.com/message/push", 
                     params={"pushkey": key, "text": text}, timeout=10)

if __name__ == "__main__":
    run()
