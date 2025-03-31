from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import dp
from keyboards.reply.reply_keyboards import main_menu_keyboard
from filters.filters import IsSub, IsPrivate
from data.functions.db import and_mine_game


@dp.message_handler(IsSub(), IsPrivate(), is_forwarded=False)
async def check_handler(m: types.Message):

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(
            text="✅ Вступить",
            url="https://t.me/pepebet_tg_casino"))
    await m.answer('<b>♥ Добро пожаловать!\n\nЧтобы пользоваться ботом вам нужно вступить в чат:</b>',
        reply_markup=keyboard)
    

@dp.message_handler(IsPrivate(), text=["Отмена","⏪ Выход"], state='*')
async def game_main_handler(message: types.Message, state: FSMContext):
    await state.finish()
    if not isinstance(message, types.Message):
        message = message.message
    and_mine_game(message.from_user.id)
    await message.answer(text="<b>🥰 Подписка проверенна, приятной игры!</b>",
                         reply_markup=main_menu_keyboard())
