import random
import json

from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.reply.reply_keyboards import mines_numb_default
from keyboards.inline.mines import MineKeyboards
from keyboards.inline.games_keyboard import solo_keyboard
from filters.filters import IsPrivateCall
from data.functions.db import get_mines, get_user, save_to_db, update_balance, \
                              update_mines_open, update_mines_map, update_mines_bets, \
                              update_mines_wins, and_mine_game, add_open_field, get_open_field
from states.states import MinesStorage
from config import mine_cof, mines_map
from loader import dp

kb = MineKeyboards()

@dp.callback_query_handler(IsPrivateCall(), text="mines_game_play", state='*')

async def get_mines_main_handlers(c: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await c.message.delete()

    if get_user(c.from_user.id) != None:
      game_status = get_mines(c.from_user.id)

      if not game_status:
        
        save_to_db(user_id=c.from_user.id, colum='create')
        
        msg = await c.message.answer_photo(
              photo=types.InputFile('miners.jpg'),
              caption=f'❕ Введите число мин [3 - 24], чем больше мин, тем больше выигрыш. ❕',
              reply_markup=kb.mine_close())
        await MinesStorage.get_mines.set()
        async with state.proxy() as data:
              data['msg'] = msg
        
      else:
        await c.message.answer(
          f'❌ Завершите предыдущую игру прежде чем начать новую',
          reply_markup=kb.play_mine_kb())
        
        

@dp.callback_query_handler(IsPrivateCall(), regexp="^mines:", state='*')

async def get_mines_handlers(c: types.CallbackQuery, state: FSMContext):

    await state.finish()

    cord = c.data.split(':')[1]
    game_status = get_mines(c.from_user.id)

    if get_user(c.from_user.id) != None:

      if game_status:
        opens = get_open_field(c.from_user.id)
  
        if cord in opens or []:
          return await c.answer('❌ Ошибка\n\nВы уже открыли данное поле!', show_alert=True)
        old = json.dumps(game_status[6])
        mine_maps = eval(json.loads(old))
        
        try:
          win_money = round(game_status[3] * mine_cof.get(game_status[2]) * game_status[5], 2)
          next_money = round(game_status[3] * mine_cof.get(game_status[2]) * (game_status[5] + 1), 2)
        except Exception as e:
          print(f'Error {e}')
  
        if cord == '0':
          return await c.message.answer_photo(
            photo=types.InputFile('miners.jpg'),
            caption=f'💸 Ваша ставка: {game_status[3]} ₽\n\n❕ Вы можете забрать: {win_money} ₽\n➡ Следующий выигрыш: {next_money} ₽',
            reply_markup=kb.mine_map(win_money, maps=mine_maps, close=True, add=True))
  
        mines = []
        for x in range(25):
          if x + 1 <= game_status[2]:
            mines.append('😔')
          else:
            mines.append('💎')
        await state.finish()
        random.shuffle(mines)
        smile = random.choice(mines)
        mine_maps[cord] = smile
        if mine_maps.get(cord) == '💎':
          
          add_open_field(cord, c.from_user.id)
          update_mines_map(mine_maps, c.from_user.id)
          update_mines_wins(win_money, c.from_user.id)
          update_mines_bets(game_status[3], c.from_user.id)
          update_mines_open(win_money, c.from_user.id)
          
          await c.message.edit_caption(f'💸 Ваша ставка: {game_status[3]} ₽\n\n❕ Вы можете забрать: {win_money} ₽\n➡ Следующий выигрыш: {next_money} ₽', reply_markup=kb.mine_map(win_money, maps=mine_maps, add=True))
          
        else:
          and_mine_game(c.from_user.id)
          
          await c.message.edit_caption(
            '😔 <b>Ой, Вы наступили на бомбу.\n\n🛑 К сожалению вы проиграли :(</b>.', reply_markup=kb.mine_map(win_money, maps=mine_maps, close=True))
      else:
        await c.message.delete()
        await c.message.answer('❌ Игра не найдена')
        
        
        
@dp.callback_query_handler(IsPrivateCall(), regexp="mine_game_stop", state='*')

async def get_stop_main_handlers(c: types.CallbackQuery, state: FSMContext):
    await state.finish()
    game_status = get_mines(c.from_user.id)
    if game_status:
      and_mine_game(c.from_user.id)
      update_balance(c.from_user.id, game_status[4])
      
      await c.message.answer_photo(
        photo=types.InputFile('miners.jpg'),
        caption=f'🥳 Игра завершена!\n\n💸 Ваша ставка - {game_status[3]} ₽\n🏆 Текущий выигрыш - {round(game_status[4], 2)} ₽')
    else:
      await c.message.delete()
      await c.message.answer('❌ Игра не найдена')