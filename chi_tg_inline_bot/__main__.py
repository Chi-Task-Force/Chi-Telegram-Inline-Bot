import hashlib
import logging
import os
import random
from typing import List

from aiogram import Bot, Dispatcher, executor
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from httpx import AsyncClient

from .corpus import Corpus, UpdateException

API_TOKEN = os.environ["API_TOKEN"]
PROXY = os.environ.get("PROXY", None)

bot = Bot(token=API_TOKEN, proxy=PROXY)
dp = Dispatcher(bot)

scheduler = AsyncIOScheduler()


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
    answers: List[str] = [sentence for sentence in corpus.common if text in sentence] if text else corpus.common
    try:
        answers = sorted(random.sample(answers, 5))
    except ValueError:
        answers = sorted(answers[:5])
    items = [InlineQueryResultArticle(
        id=hashlib.md5(answer.encode()).hexdigest(),
        title=answer,
        input_message_content=InputTextMessageContent(answer)
    ) for answer in answers]
    await bot.answer_inline_query(inline_query.id, results=items, cache_time=10, is_personal=True)


scheduler.add_job(update_corpus, "interval", minutes=10)
scheduler.add_job(update_corpus)
corpus = Corpus()
http = AsyncClient()
scheduler.start()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
