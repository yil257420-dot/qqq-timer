import yfinance as yf
import requests
import os

def run():
    # 锁定 QQQ 标的
    ticker = yf.Ticker("QQQ")
    # 获取最近的历史数据
    hist = ticker.history(period="5d")
    
    # 提取最后两个完整闭市交易日的收盘价，确保数据准确
    data = hist['Close'].dropna()
    y_close = data.iloc[-1]
    b_close = data.iloc[-2]
    
    # 计算涨跌幅
    chg = (y_close - b_close) / b_close * 100
    
    # 策略逻辑：基于涨跌幅生成中文推送内容
    # 使用纯英文字符串作为模板，避免浏览器翻译干扰
    msg = "QQQ Previous Close: {:.2f}, Change: {:.2f}%".format(y_close, chg)
    
    if chg < 0:
        abs_chg = abs(chg)
        if abs_chg <= 2:
            amt = 30
        elif abs_chg <= 4:
            amt = 50
        else:
            amt = 100
        # 强制拼接中文策略，确保推送内容符合你的要求
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
