from aiogram.types import ReplyKeyboardMarkup


def main_menu_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🎲 GAMES")
    keyboard.row("🚀 INFO", "✉️ CHAT")
    keyboard.row("💰 PROFILE")
    return keyboard


def play_slots_keyboard(bet):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"📍 Вращать | Ставка: {bet}")
    keyboard.row("🔁 Изменить ставку", "⏪ Выход")
    return keyboard


def mines_numb_default():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=3)
    keyboard.add('3', '5', '10', '15', '20', '24', 'Отмена')
        
    return keyboard
