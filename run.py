import requests
import os

def run():
    # 1. 获取行情
    url = "https://query1.finance.yahoo.com/v8/finance/chart/QQQ?range=1d&interval=1m"
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15).json()
        price = res['chart']['result'][0]['meta']['regularMarketPrice']
        msg = f"【QQQ监测】当前价格: {price:.2f}"
    except Exception as e:
        msg = f"【系统错误】获取数据失败: {str(e)}"

    # 2. 强制推送到手机 (使用 POST 方式，强制触发提醒)
    key = os.environ.get("PUSHDEER_KEY")
    if key:
        push_url = "https://api2.pushdeer.com/message/push"
        # 这里的 is_alert='1' 会强制让手机弹出通知并震动
        payload = {"pushkey": key, "text": msg, "type": "markdown", "is_alert": "1"}
        resp = requests.post(push_url, data=payload, timeout=10)
        print(f"推送完成，状态码: {resp.status_code}")
    else:
        print("错误: PUSHDEER_KEY 未设置")

if __name__ == "__main__":
    run()