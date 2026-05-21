import yfinance as yf
import requests
import os

def run():
    ticker = yf.Ticker("QQQ")
    # 获取实时信息
    info = ticker.fast_info
    
    current_price = info['last_price']
    prev_close = info['previous_close']
    
    # 计算实时跌幅
    chg = (current_price - prev_close) / prev_close * 100
    
    # 策略判断
    push_msg = f"QQQ Real-time: {current_price:.2f}, Change: {chg:.2f}%"
    
    if chg < 0:
        abs_chg = abs(chg)
        if abs_chg <= 2:
            amt = 30
        elif abs_chg <= 4:
            amt = 50
        else:
            amt = 100
        push_msg += f" | Strategy: Buy {amt} USD"
    else:
        push_msg += " | Strategy: Wait (Price is up)"

    # 执行推送
    key = os.environ.get("PUSHDEER_KEY")
    if key:
        requests.get("https://api2.pushdeer.com/message/push", 
                     params={"pushkey": key, "text": push_msg}, timeout=10)
    print(push_msg)

if __name__ == "__main__":
    run()
