import requests
import os
import pytz
import holidays
from datetime import datetime
import yfinance as yf


def run():
    # 锁定美东时间（自动处理夏令时 / 冬令时）
    tz = pytz.timezone('US/Eastern')
    now = datetime.now(tz)

    # 判断是否休市
    is_holiday = (
        now.weekday() >= 5
        or now.strftime('%Y-%m-%d') in holidays.US()
    )

    # 休市直接推送
    if is_holiday:
        msg = (
            "【QQQ开盘行动指南】\n"
            "状态：休市\n"
            "策略：今日休市，无操作。"
        )

    else:
        try:
            # 获取 QQQ 日线数据
            ticker = yf.Ticker("QQQ")

            # 强制使用日线，只看已收盘数据
            hist = ticker.history(
                period="5d",
                interval="1d"
            )

            # 前一个交易日收盘
            prev_close = hist.iloc[-2]['Close']

            # 最近一个交易日收盘
            curr_close = hist.iloc[-1]['Close']

            # 涨跌幅
            pct = ((curr_close - prev_close) / prev_close) * 100

            # 阶梯定投策略
            if pct >= 0:
                strategy = "涨幅为正，不操作。"

            elif -2.0 <= pct < 0:
                strategy = "跌幅 ≤ 2%，定投 30 美金。"

            elif -4.0 <= pct < -2.0:
                strategy = "跌幅 2%-4%，定投 50 美金。"

            else:
                strategy = "跌幅 > 4%，定投 100 美金。"

            # 推送内容
            msg = (
                f"【QQQ开盘行动指南】\n"
                f"状态：开盘\n"
                f"前日收盘：{prev_close:.2f}\n"
                f"昨日收盘：{curr_close:.2f}\n"
                f"涨跌：{pct:+.2f}%\n"
                f"策略：{strategy}"
            )

        except Exception as e:
            msg = f"【系统提示】请求失败：{str(e)}"

    # PushDeer 推送
    key = os.environ.get("PUSHDEER_KEY")

    if key:
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

            # 检查是否真正发送成功
            r.raise_for_status()

        except Exception as e:
            print(f"PushDeer 推送失败：{e}")


if __name__ == "__main__":
    run()
