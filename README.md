# Chi Telegram Inline Bot

在 Telegram 上快速模仿迟先生卖弱。

Telegram: [@realskyzh_bot](https://t.me/realskyzh_bot)

## 卖弱方式

在任意聊天窗口输入 @realskyzh_bot 即会随机弹出至多五句卖弱语录，输入文字更可过滤筛选语录，
点击弹出的语录即可自动发出。若语句不令人满意，可以删除整条消息 10s 后重试。

## 开始上手

1. 从 BotFather 申请到 Telegram Bot 账号，牢记 token
2. 修改 docker-compose.yml 中的 API_TOKEN 为你的 token
3. `docker-compose up -d`

或

``` shell script
$ pip install -r requirements.txt
$ API_TOKEN=<your_token_here> python -m chi_tg_inline_bot.__main__
```