import requests
import os
import time
import datetime

def run():
    # 1. 强制周末保护
    if datetime.datetime.now().weekday() >= 5:
        return

    # 2. 精准定时：等待至 09:30:05 (美东时间)
    # 确保 Cron 调度的启动误差被抵消，让请求发生在开盘瞬间
    time.sleep(15) 

    # 3. 配置雅虎原始数据接口，使用会话保持连接
    session = requests.Session()
    url = "https://query1.finance.yahoo.com/v8/finance/chart/QQQ?range=1d&interval=1m"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    data = None
    # 4. 指数退避重试机制
    for attempt in range(5):
        try:
            res = session.get(url, headers=headers, timeout=10).json()
            if 'chart' in res and res['chart']['result']:
                data = res['chart']['result'][0]['meta']
                # 检查数据是否有效
                if data.get('regularMarketPrice'):
                    break
        except Exception:
            pass
        time.sleep(5)
            
    if not data:
        return # 彻底获取失败则静默终止，避免发送错误数据

    price = data['regularMarketPrice']
    prev = data['previousClose']
    chg = (price - prev) / prev * 100
    
    # 5. 中文推送构建
    msg = "QQQ 实时价格: {:.2f}, 涨跌幅: {:.2f}%".format(price, chg)
    
    if chg < 0:
        abs_chg = abs(chg)
        amt = 30 if abs_chg <= 2 else (50 if abs_chg <= 4 else 100)
        msg += "。策略：建议立即买入 {} 美元。".format(amt)
    else:
        msg += "。策略：当前未下跌，无需操作。"

    # 6. 安全推送
    key = os.environ.get("PUSHDEER_KEY")
    if key and key.strip():
        try:
            session.get("https://api2.pushdeer.com/message/push", 
                        params={"pushkey": key, "text": msg}, timeout=10)
        except:
            pass

if __name__ == "__main__":
    run()
