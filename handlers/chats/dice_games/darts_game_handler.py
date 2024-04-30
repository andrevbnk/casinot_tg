import asyncio

from aiogram import types
from filters.filters import IsPrivate
from loader import dp
from data.functions.db import add_chat_dice_game_to_db, get_chat_last_id_dice_game, \
                              get_user, update_balance
from keyboards.inline.games_keyboard import dice_chat_game_keyboard



@dp.message_handler(~IsPrivate(), is_reply=False,  chat_type='supergroup',
                    commands=["darts", "дартс", "dar"])
async def add_dice_game_chat_handler(m: types.Message):
    user = get_user(m.from_user.id)
    if user:
      if m.get_args():
        
        if m.get_args().isdigit() and int(m.get_args()) >= 5:
          
          if user[1] >= int(m.get_args()):
            
            if m.from_user.username:
              username = f'@{m.from_user.username}'
            else:
              username = f'<a href="tg://user?id={m.from_user.id}">{m.from_user.id}</a>'
            
            create_status = add_chat_dice_game_to_db(
              chat_id=m.chat.id,
              player_id_1=m.from_user.id,
              player_name_1=username,
              emoji='🎯',
              bet=int(m.get_args()))
            if create_status:
              update_balance(m.from_user.id, -int(m.get_args()))
              game = get_chat_last_id_dice_game()
              msg = await m.answer(
                f'🎯 Дартс №{game[0]}\n\n1️⃣ Игрок: {username}\n2️⃣ Игрок: Ожидание..\n\n💸 Ставка: <code>{m.get_args()}</code> RUB.\n\n♻️ <i>Чтобы присоединиться, нажмите кнопку ниже</i>: [ ✅ Присоединиться ]',
                reply_markup=dice_chat_game_keyboard(game[0]))
              
            else:
              await msg.edit_text('❌ Что-то пошло не так, не удалось создать игру')
              await asyncio.sleep(10)
              await msg.delete()
              
          else:
            msg = await m.reply('❌ Недостаточно денег!')
            await asyncio.sleep(10)
            await msg.delete()
        else:
          msg = await m.reply('<b>❗Минимальная ставка: 5 ₽</b>')
          await asyncio.sleep(10)
          
      else:
        msg = await m.reply('Введите ставку в виде аргумента команды:')
        await asyncio.sleep(10)
        await msg.delete()