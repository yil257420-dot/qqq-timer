import yfinance as yf
import requests
import os

def run():
    # 锁定标的并获取最近5个交易日数据
    ticker = yf.Ticker("QQQ")
    hist = ticker.history(period="5d")
    
    # 提取最后两个完整闭市收盘价
    data = hist['Close'].dropna()
    y_close = data.iloc[-1]
    b_close = data.iloc[-2]
    
    # 计算涨跌幅
    chg = (y_close - b_close) / b_close * 100
    
    # 构建中文推送消息
    msg = "QQQ 上一交易日收盘: {:.2f}, 涨跌幅: {:.2f}%".format(y_close, chg)
    
    # 交易策略逻辑
    if chg < 0:
        abs_chg = abs(chg)
        if abs_chg <= 2:
            amt = 30
        elif abs_chg <= 4:
            amt = 50
        else:
            amt = 100
        msg += "。策略：建议买入 {} 美元。".format(amt)
    else:
        msg += "。策略：今日上涨，无需操作。"

    # 执行推送
    key = os.environ.get("PUSHDEER_KEY")
    if key:
        requests.get("https://api2.pushdeer.com/message/push", 
                     params={"pushkey": key, "text": msg}, timeout=10)
    print(msg)

if __name__ == "__main__":
    run()
