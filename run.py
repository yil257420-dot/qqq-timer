import requests
import os
import datetime

def run():
    log_msg = f"[{datetime.datetime.now()}] 运行检查: "
    
    # 强制跳过周六日
    if datetime.datetime.now().weekday() >= 5:
        return

    session = requests.Session()
    url = "https://query1.finance.yahoo.com/v8/finance/chart/QQQ?range=1d&interval=1m"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = session.get(url, headers=headers, timeout=15).json()
        data = res['chart']['result'][0]['meta']
        price = data['regularMarketPrice']
        prev = data['previousClose']
        chg = (price - prev) / prev * 100
        log_msg += f"成功获取数据, QQQ={price}, 涨跌={chg:.2f}%"
    except Exception as e:
        log_msg += f"API数据获取异常: {e}"
        price, chg = 0, 0

    # 策略构造
    if chg < 0:
        amt = 30 if abs(chg) <= 2 else (50 if abs(chg) <= 4 else 100)
        final_msg = f"{log_msg} | 策略：建议买入 {amt} 美元。"
    else:
        final_msg = f"{log_msg} | 策略：当前无需买入。"

    # 强制推送：无论逻辑如何，这里必须执行
    key = os.environ.get("PUSHDEER_KEY")
    if key and key.strip():
        try:
            session.get("https://api2.pushdeer.com/message/push", 
                        params={"pushkey": key, "text": final_msg}, timeout=10)
        except Exception as e:
            print(f"推送彻底失败: {e}")
    else:
        print("未检测到 PUSHDEER_KEY")

if __name__ == "__main__":
    run()
