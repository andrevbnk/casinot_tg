from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from loader import bot
from config import config


class IsPrivate(BoundFilter):
    async def check(self, message: types.Message):
        return message.chat.type == types.ChatType.PRIVATE


class IsPrivateCall(BoundFilter):
    async def check(self, call: types.CallbackQuery):
        return call.message.chat.type == types.ChatType.PRIVATE


class IsAdmin(BoundFilter):
    async def check(self, message: types.Message):
        return str(message.from_user.id) in config("admin_id")


class IsMe(BoundFilter):
    async def check(self, message: types.Message):
        status = False
        for x in message.new_chat_members:
          if int(x.id) == int(config("bot_token").split(":")[0]):
            status = True
        return status


class IsSub(BoundFilter):
    async def check(self, m: types.Message):
        try:
          if m.chat.type == types.ChatType.PRIVATE:
            print(int(config("chat_id")))
            member = await bot.get_chat_member(int(config("chat_id")), m.from_user.id)
            if member.status == 'left':
              return True
            else:
              return False
        except Exception as e:
          print(f'Subscription verification error {e}')
          return False


class IsGroup(BoundFilter):
    async def check(self, message: types.Message):
        return message.chat.type != types.ChatType.PRIVATE