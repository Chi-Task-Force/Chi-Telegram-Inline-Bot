import hashlib
import logging
import os
from queue import Queue
from typing import List, Set

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ChosenInlineResult, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from httpx import AsyncClient

from .corpus import Corpus, UpdateException
from .logger import InlineLogger
from .sell import Seller

API_TOKEN = os.environ["API_TOKEN"]
PROXY = os.environ.get("PROXY", None)

bot = Bot(token=API_TOKEN, proxy=PROXY)
dp = Dispatcher(bot)

answer_map = {}
stat_set: Set[str] = set()


async def update_corpus():
    try:
        logging.warning("Updating corpus.")
        await corpus.update()
        logging.info("Corpus updated.")
    except UpdateException:
        logging.exception("Failed to update corpus.")


@dp.inline_handler()
async def inline_echo(inline_query: InlineQuery):
    text = inline_query.query
    answers: List[str] = seller.sell(text)
    moan: str = seller.vegetable_moan()
    sell_count = await get_user_stat(inline_query.from_user.id)
    sell_stat: str = f"我已经卖了 {sell_count} 句菜{'，我 zc' if sell_count > 20 else ''}"

    stat_hash: str = hashlib.md5(sell_stat.encode()).hexdigest()
    stat_set.add(stat_hash)

    answers_hash = {answer: hashlib.md5(answer.encode()).hexdigest() for answer in answers}
    for answer, _hash in answers_hash.items():
        answer_map[_hash] = answer

    items = [InlineQueryResultArticle(id=hashlib.md5(moan.encode()).hexdigest(),
                                      title="菜喘",
                                      input_message_content=InputTextMessageContent(moan))] + \
            [InlineQueryResultArticle(
                id=_hash,
                title=answer,
                input_message_content=InputTextMessageContent(answer)
            ) for answer, _hash in answers_hash.items()] + \
            [InlineQueryResultArticle(id=stat_hash,
                                      title="卖菜统计",
                                      input_message_content=InputTextMessageContent(sell_stat))]

    await bot.answer_inline_query(inline_query.id, results=items, cache_time=0, is_personal=True)


async def get_user_stat(user_id: int) -> int:
    user_id = hashlib.md5(user_id.to_bytes(16, "little", signed=False)).hexdigest()
    return await logger.get_user_stat(user_id)


@dp.chosen_inline_handler()
async def inline_choice(result: ChosenInlineResult):
    if result.result_id in stat_set:
        stat_set.remove(result.result_id)
        return
    await logger.log(answer_map.get(result.result_id, "-1"),
                     hashlib.md5(result.from_user.id.to_bytes(16, "little", signed=False)).hexdigest())


@dp.message_handler(commands=["stat"])
async def stat_handler(message: types.Message):
    stat = await logger.get_stat()
    top_sentences = "\n".join([f"{k}：{v} 次" for k, v in stat.top_sentences.items()])
    await message.answer(f"总共已经有 {stat.users} 名迟化人卖了 {stat.total_requests} 句菜\n其中最迟的人卖了 {stat.top_user_count} 句\n\n" \
                         f"被卖得最多次的句子：\n{top_sentences}")


logger = InlineLogger(os.environ["LOG_FILE"])
scheduler = AsyncIOScheduler()
scheduler.add_job(update_corpus, "interval", minutes=10)
scheduler.add_job(update_corpus)
corpus = Corpus()
seller = Seller(corpus)
http = AsyncClient()
scheduler.start()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
