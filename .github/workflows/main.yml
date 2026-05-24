name: QQQ Bot
on:
  workflow_dispatch:
  schedule:
    # 调整为 35 分运行 (美东时间 09:35)，确保开盘波动数据已进入 API
    - cron: '35 13 * * 1-5'

jobs:
  run_bot:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install requests
      - env:
          PUSHDEER_KEY: ${{ secrets.PUSHDEER_KEY }}
        run: python run.py
