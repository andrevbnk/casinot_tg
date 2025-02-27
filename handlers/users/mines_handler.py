import random

from aiogram import types
from aiogram.dispatcher import FSMContext
from data.functions.db import save_to_db, get_user, get_mines, update_mines_bets, \
                              set_status_game, update_mines_open, update_mines_num, update_balance
from keyboards.inline.mines import MineKeyboards
from filters.filters import IsPrivate
from states.states import MinesStorage
from loader import dp
from config import mine_cof, mines_map

kb = MineKeyboards()

@dp.message_handler(IsPrivate(), state=MinesStorage.get_mines)

async def get_mines_handlers(m: types.Message, state: FSMContext):
    user = get_user(m.from_user.id)
    if user != None:
      if m.text.isdigit():
        if int(m.text) >= 3 and int(m.text) <= 24:
          game_status = get_mines(m.from_user.id)
          if not game_status:
            save_to_db(nums=int(m.text), user_id=m.from_user.id, colum='num')
            async with state.proxy() as data:
              try:
                await data['msg'].delete()
              except:
                pass
            msg = await m.answer_photo(
              photo=types.InputFile('miners.jpg'),
              caption=f'<b>💸 Введите сумму ставки от 10 ₽\n\n💰 Ваш баланс: <code>{round(user[1], 2)}</code></b> ₽',
              reply_markup=kb.mine_close())
            async with state.proxy() as data:
              data['nums'] = int(m.text)
              data['msg'] = msg
            await MinesStorage.start.set()
          else:
            await m.answer(
              f'❌ Завершите предыдущую игру прежде чем начать новую',
              reply_markup=kb.play_mine_kb())
        else:
          await m.answer('<b>🧨 Введите количество бомб от [3 - 24]</b>')



@dp.message_handler(IsPrivate(), state=MinesStorage.start)

async def get_mines_handlers(m: types.Message, state: FSMContext):
    user = get_user(m.from_user.id)
    if user != None:
      async with state.proxy() as data:
        nums = data['nums']
        try:
          await data['msg'].delete()
        except:
          pass
      
      if m.text.isdigit() and int(m.text) >= 10:
        if float(user[1]) >= int(m.text):
          
          set_status_game(1, user_id=m.from_user.id)
          try:
            win_money = round(int(m.text) * mine_cof.get(nums), 2)
            next_money = round(int(m.text) * mine_cof.get(nums) * 2, 4)
          except Exception as e:
            print(e)

          update_mines_num(nums, m.from_user.id)
          update_mines_bets(int(m.text), m.from_user.id)
          update_mines_open(int(m.text), m.from_user.id)
          update_balance(m.from_user.id, -int(m.text))
 
          await m.answer_photo(
            photo=types.InputFile('miners.jpg'),
            caption=f'<b>💰 Ваша ставка - {m.text} ₽\n🏆 Следующий выигрыш - {int(m.text)} ₽</b>',
            reply_markup=kb.mine_map(int(m.text), close=True))
        else:
          await m.answer(f'‼ Недостаточно денег\n\n<b>💰 Ваш баланс: {round(user[1], 2)} RUB\nВведите целую сумму ставки от 10 ₽<b>')
      else:
        # await state.finish()
        await m.answer('❌ Минимальная ставка 10 RUB, введите ')