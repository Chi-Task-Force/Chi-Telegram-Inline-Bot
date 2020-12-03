import hashlib
import logging
import os
from typing import List

from aiogram import Bot, Dispatcher, executor
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
            ) for answer, _hash in answers_hash.items()]

    await bot.answer_inline_query(inline_query.id, results=items, cache_time=0, is_personal=True)


@dp.chosen_inline_handler()
async def inline_choice(result: ChosenInlineResult):
    await logger.log(answer_map.get(result.result_id, -1),
                     hashlib.md5(result.from_user.id.to_bytes(16, "little", signed=False)).hexdigest())


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
