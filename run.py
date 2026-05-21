import yfinance as yf
import requests
import os

def run():
    # 强制锁定 QQQ
    ticker = yf.Ticker("QQQ")
    # 获取最近 5 个交易日，确保包含至少两个完整的闭市数据
    hist = ticker.history(period="5d")
    
    # 必须清除空值，确保数据对齐
    data = hist['Close'].dropna()
    
    # 倒数第一位是最后一次结算价，倒数第二位是前一次结算价
    y_close = data.iloc[-1]
    b_close = data.iloc[-2]
    
    # 计算涨跌幅
    chg = (y_close - b_close) / b_close * 100
    
    # 严谨的策略判断：下跌则触发定投计算
    push_msg = f"QQQ Close: {y_close:.2f}, Change: {chg:.2f}%"
    
    if chg < 0:
        # 阶梯加仓策略：跌幅越深，定投金额越大
        abs_chg = abs(chg)
        if abs_chg <= 2:
            amt = 30
        elif abs_chg <= 4:
            amt = 50
        else:
            amt = 100
        push_msg += f" | Strategy: Buy {amt} USD"
    else:
        push_msg += " | Strategy: Wait"

    # 执行推送
    key = os.environ.get("PUSHDEER_KEY")
    if key:
        requests.get("https://api2.pushdeer.com/message/push", 
                     params={"pushkey": key, "text": push_msg}, timeout=10)
    print(push_msg)

if __name__ == "__main__":
    run()
