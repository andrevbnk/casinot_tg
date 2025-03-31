import asyncio
import middlewares

from aiogram import executor

from data.functions.functions import game_time
from handlers import dp
from loader import bot
# from utils.payments import QiwiAPI, PayeerAPI

middlewares.setup(dp)
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(game_time(bot))
    # loop.create_task(QiwiAPI().CheckTtrans())
    # loop.create_task(PayeerAPI().CheckTtrans())
    executor.start_polling(dp, skip_updates=True)