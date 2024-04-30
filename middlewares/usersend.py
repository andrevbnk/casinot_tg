import time

from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram import types


class ReadUser(BaseMiddleware):
    async def on_pre_process_message(self, m: types.Message, data: dict):
      if m.chat.type == 'private':
        print(f'[{time.strftime("%H:%M:%S", time.localtime(time.time()))}] {m.from_user.first_name} ID: {m.from_user.id} отправил: {m.text}')

    async def on_pre_process_callback_query(self, call: types.CallbackQuery, data: dict):
      if call.message.chat.type == 'private':
        print(f'[{time.strftime("%H:%M:%S", time.localtime(time.time()))}] {call.from_user.first_name} ID: {call.from_user.id} отправил callback: {call.data}')