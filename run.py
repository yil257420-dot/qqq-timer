import os
import requests
import pytz
import yfinance as yf
import pandas_market_calendars as mcal
from datetime import datetime


def push_message(msg):
    key = os.environ.get("PUSHDEER_KEY")

    if not key:
        print("未找到 PUSHDEER_KEY")
        return

    try:
        r = requests.post(
            "https://api2.pushdeer.com/message/push",
            data={
                "pushkey": key,
                "text": msg,
                "type": "markdown",
                "is_alert": "1"
            },
            timeout=10
        )
        r.raise_for_status()
        print("推送成功")

    except Exception as e:
        print(f"PushDeer 推送失败：{e}")


def run():
    # 美东时间，自动处理夏令时 / 冬令时
    tz = pytz.timezone("US/Eastern")
    now = datetime.now(tz)

    # 只有美东 09:30 才真正执行
    # 这样可以解决夏令时 / 冬令时问题
    if not (now.hour == 9 and now.minute == 30):
        print(f"当前美东时间 {now.strftime('%H:%M')}，不是开盘提醒时间，跳过。")
        return

    today = now.date()

    # 用 NYSE 交易所日历判断今天是否真正开盘
    nyse = mcal.get_calendar("NYSE")
    schedule = nyse.schedule(start_date=today, end_date=today)

    # 休市也要准时提醒
    if schedule.empty:
        msg = (
            "【QQQ开盘行动指南】\n"
            "状态：休市\n"
            "策略：今日休市，无操作。"
        )
        push_message(msg)
        return

    try:
        ticker = yf.Ticker("QQQ")

        # 只取日线
        hist = ticker.history(period="10d", interval="1d")

        if hist.empty or len(hist) < 2:
            msg = "【系统提示】QQQ 数据不足，请稍候查看。"
            push_message(msg)
            return

        # 去掉今天可能出现的未完成日线，只保留今天以前的完整交易日
        hist = hist.copy()
        hist["date_only"] = [i.date() for i in hist.index]
        hist = hist[hist["date_only"] < today]

        if len(hist) < 2:
            msg = "【系统提示】完整收盘数据不足，请稍候查看。"
            push_message(msg)
            return

        prev_close = hist.iloc[-2]["Close"]
        curr_close = hist.iloc[-1]["Close"]

        pct = ((curr_close - prev_close) / prev_close) * 100

        if pct >= 0:
            strategy = "涨幅为正，不操作。"
        elif -2.0 <= pct < 0:
            strategy = "跌幅 ≤ 2%，定投 30 美金。"
        elif -4.0 <= pct < -2.0:
            strategy = "跌幅 2%-4%，定投 50 美金。"
        else:
            strategy = "跌幅 > 4%，定投 100 美金。"

        msg = (
            "【QQQ开盘行动指南】\n"
            "状态：开盘\n"
            f"前日收盘：{prev_close:.2f}\n"
            f"昨日收盘：{curr_close:.2f}\n"
            f"涨跌：{pct:+.2f}%\n"
            f"策略：{strategy}"
        )

        push_message(msg)

    except Exception as e:
        msg = f"【系统提示】请求失败：{str(e)}"
        push_message(msg)


if __name__ == "__main__":
    run()
