from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import mines_map

class MineKeyboards(object):


    def mine_map(self, win_sum, close=False, maps=mines_map, add=False):
        keyboard = InlineKeyboardMarkup(row_width=5)

        for k, v in maps.items():
          if add:
            keyboard.insert(InlineKeyboardButton(text=v, callback_data=f'mines:{k}'))
          else:
            keyboard.insert(InlineKeyboardButton(text=v, callback_data=k))
        if close:
          keyboard.add(InlineKeyboardButton(text="❌ Выйти", callback_data="games_back_menu"))
        else:
          keyboard.add(InlineKeyboardButton(
            text=f"🎁 Забрать {win_sum} RUB",
            callback_data=f"mine_game_stop:{win_sum}"))
        
        return keyboard
      
      
    def mine_close (self):
        keyboard = InlineKeyboardMarkup()

        keyboard.add(InlineKeyboardButton(text="❗Отменить", callback_data="games_back_menu"))
        
        return keyboard


    def bak_kb (self):
        keyboard = InlineKeyboardMarkup()

        keyboard.add(InlineKeyboardButton(text="❌ Выйти", callback_data="games_back_menu"))
        
        return keyboard

    def play_mine_kb (self):
        keyboard = InlineKeyboardMarkup()

        keyboard.add(InlineKeyboardButton(text="🚶 Продолжить!", callback_data="mines:0"))
        
        return keyboard
    