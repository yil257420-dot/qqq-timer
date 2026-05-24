import requests
import os
import datetime
import json

def run():
    print(f"[{datetime.datetime.now()}] 任务开始...")
    
    # 1. 尝试获取数据
    url = "https://query1.finance.yahoo.com/v8/finance/chart/QQQ?range=1d&interval=1m"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status() # 如果网络请求失败会抛出异常
        data = res.json()['chart']['result'][0]['meta']
        price = data['regularMarketPrice']
        chg = ((price - data['previousClose']) / data['previousClose']) * 100
        msg = f"测试消息: QQQ当前{price:.2f}, 涨跌{chg:.2f}%"
    except Exception as e:
        msg = f"系统出错: {str(e)}"
    
    # 2. 强制打印结果到 GitHub Actions 日志
    print(f"准备推送内容: {msg}")

    # 3. 推送逻辑 (增加响应打印)
    key = os.environ.get("PUSHDEER_KEY")
    if key:
        push_url = "https://api2.pushdeer.com/message/push"
        # 加上 print 看看接口怎么回复
        resp = requests.get(push_url, params={"pushkey": key, "text": msg}, timeout=10)
        print(f"推送接口返回状态: {resp.status_code}")
        print(f"推送接口返回内容: {resp.text}")
    else:
        print("错误: 找不到 PUSHDEER_KEY")

if __name__ == "__main__":
    run()
