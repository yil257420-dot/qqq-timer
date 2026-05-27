import requests, os, pytz, holidays
from datetime import datetime
import yfinance as yf

def run():
    # 锁定美东时间，自动处理夏冬令时切换
    tz = pytz.timezone('US/Eastern')
    now = datetime.now(tz)
    
    # 检查状态：周末或假期标记
    is_holiday = now.weekday() >= 5 or now.strftime('%Y-%m-%d') in holidays.US()
    
    # 获取数据：强制锁定日线颗粒度，确保拿到纯粹的收盘价
    try:
        ticker = yf.Ticker("QQQ")
        hist = ticker.history(period="5d", interval="1d")
        # 确保取到最近两个闭合交易日的收盘价
        prev_close = hist.iloc[-2]['Close']
        curr_close = hist.iloc[-1]['Close']
        pct = ((curr_close - prev_close) / prev_close) * 100
        
        # 阶梯定投逻辑
        if is_holiday:
            strategy = "今日休市，无操作。"
        elif pct >= 0:
            strategy = "涨幅为正，不操作。"
        elif -2.0 <= pct < 0:
            strategy = "跌幅 ≤ 2%，定投 30 美金。"
        elif -4.0 <= pct < -2.0:
            strategy = "跌幅 2%-4%，定投 50 美金。"
        else:
            strategy = "跌幅 > 4%，定投 100 美金。"
            
        msg = f"【QQQ开盘行动指南】\n状态: {'休市' if is_holiday else '开盘'}\n前日收盘: {prev_close:.2f}\n昨日收盘: {curr_close:.2f}\n涨跌: {pct:+.2f}%\n策略: {strategy}"
    except Exception:
        msg = "【系统提示】数据源暂未更新，请稍候查看。"

    # 瞬时推送
    key = os.environ.get("PUSHDEER_KEY")
    if key:
        requests.post("https://api2.pushdeer.com/message/push", 
                      data={"pushkey": key, "text": msg, "type": "markdown", "is_alert": "1"}, timeout=10)

if __name__ == "__main__":
    run()
