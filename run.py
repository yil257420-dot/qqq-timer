import yfinance as yf
import requests
import os
import datetime

def run():
    # 1. 基础逻辑判断是否为周末 (星期六:5, 星期日:6)
    today = datetime.datetime.now().weekday()
    if today >= 5:
        return

    # 2. 实时数据获取
    ticker = yf.Ticker("QQQ")
    # 使用 fast_info 绕过复杂的 pandas 计算，降低报错风险
    info = ticker.fast_info
    current_price = info['last_price']
    prev_close = info['previous_close']
    
    # 3. 计算跌幅
    chg = (current_price - prev_close) / prev_close * 100
    
    # 4. 构建中文推送消息
    msg = "QQQ 实时价格: {:.2f}, 涨跌幅: {:.2f}%".format(current_price, chg)
    
    if chg < 0:
        abs_chg = abs(chg)
        amt = 30 if abs_chg <= 2 else (50 if abs_chg <= 4 else 100)
        msg += "。策略：建议立即买入 {} 美元。".format(amt)
    else:
        msg += "。策略：当前未下跌，无需操作。"

    # 5. 执行推送
    key = os.environ.get("PUSHDEER_KEY")
    if key and key.strip():
        requests.get("https://api2.pushdeer.com/message/push", 
                     params={"pushkey": key, "text": msg}, timeout=10)

if __name__ == "__main__":
    run()
