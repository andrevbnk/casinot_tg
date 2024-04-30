from aiogram import types
from filters.filters import IsMe
from loader import dp
from data.functions.db import add_chat_to_db



@dp.message_handler(IsMe(), chat_type='supergroup', content_types=["new_chat_members"])
async def add_chat_handler(m: types.Message):
    add_chat_to_db(m.chat.id)
    await m.answer('<b>Зачем добавил меня? Ну ладно.. Я очень благодарен что ты меня добавил в свой чат, я буду вас оповещать о новых играх</b> ')