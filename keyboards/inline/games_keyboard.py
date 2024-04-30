from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import other_games_info
from data.functions.db import get_other_games, get_other_game, get_blackjack_games, get_bakkara_games
from keyboards.inline.callback_datas import game_callback, game_info_callback, other_game_callback


def games_control_keyboard(game_name):
    keyboard = InlineKeyboardMarkup(row_width=2)
    emoji = "✔"

    if game_name == "other":
        games = get_other_games()
        for game in games:
            keyboard.row(
                InlineKeyboardButton(text=f"{other_games_info[game[-1]]['emoji']} #{game[0]} | {game[2]}₽",
                                     callback_data=game_info_callback.new(
                                         game_name=game_name, action="info", game_id=f"{game[0]}"
                                     )))

    elif game_name == "blackjack":
        games = get_blackjack_games()
        for game in games:
            keyboard.row(
                InlineKeyboardButton(text=f"🔍 Game #{game[0]} | {game[-2]}₽",
                                     callback_data=game_info_callback.new(
                                         game_name=game_name, action="info", game_id=f"{game[0]}"
                                     )))

    elif game_name == "bakkara":
        games = get_bakkara_games()
        for game in games:
            keyboard.row(
                InlineKeyboardButton(text=f"🔍 Game #{game[0]} | {game[-2]}₽",
                                     callback_data=game_info_callback.new(
                                         game_name=game_name, action="info", game_id=f"{game[0]}"
                                     )))

    button1 = InlineKeyboardButton(text=f"{emoji} Создать", callback_data=game_callback.new(
        game_name=game_name, action="create"
    ))
    button2 = InlineKeyboardButton(text="⚙ Обновить", callback_data=game_callback.new(
        game_name=game_name, action="update"
    ))
    button3 = InlineKeyboardButton(text="📊 Статистика", callback_data=game_callback.new(
        game_name=game_name, action="statistic"
    ))
    keyboard.add(button1, button2, button3)
    keyboard.add(InlineKeyboardButton(text="📝 Правила Игры", url="https://telegra.ph/Pravila-igr-09-18"))
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="games_back_menu"))
    return keyboard


def other_games_types():
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton(text="🎲 Кости", callback_data=other_game_callback.new(
        game_name="other", action="type_choice", game_type="dice"
    ))
    button2 = InlineKeyboardButton(text="🎯 Дартс", callback_data=other_game_callback.new(
        game_name="other", action="type_choice", game_type="darts"
    ))
    button3 = InlineKeyboardButton(text="🏀 Баскетбол", callback_data=other_game_callback.new(
        game_name="other", action="type_choice", game_type="basketball"
    ))
    button4 = InlineKeyboardButton(text="🎳 Боулинг", callback_data=other_game_callback.new(
        game_name="other", action="type_choice", game_type="bowling"
    ))
    keyboard.add(button1, button2, button3, button4)
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="close"))
    return keyboard


def games_info_keyboard(game_name, game_id):
    if game_name == "other":
        emoji = other_games_info[get_other_game(game_id)[-1]]['emoji']
        text = "Играть"
    elif game_name == "blackjack":
        emoji = ""
        text = "Принять ставку"
    elif game_name == "bakkara":
        emoji = ""
        text = "Играть"
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton(text=f"{emoji} {text}",
                                   callback_data=game_info_callback.new(
                                       game_name=game_name, action="enjoy", game_id=game_id
                                   ))
    button2 = InlineKeyboardButton(text="Закрыть", callback_data="close")
    keyboard.add(button1, button2)

    return keyboard


def blackjack_keyboard(game_name, game_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton(text=f'➕ Взять еще карту', callback_data=game_info_callback.new(
        game_name=game_name, action="add_card", game_id=game_id
    ))
    button2 = InlineKeyboardButton(text=f'✔Хватит, вскрываемся', callback_data=game_info_callback.new(
        game_name=game_name, action="stop", game_id=game_id
    ))

    keyboard.add(button1, button2)

    return keyboard


def slots_menu_keyboard(game_name):
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton(text="🎰 Играть", callback_data=game_callback.new(
        game_name=game_name, action="play"
    ))
    button2 = InlineKeyboardButton(text="📊 Статистика", callback_data=game_callback.new(
        game_name=game_name, action="statistic"
    ))

    button3 = InlineKeyboardButton(text="🔙 Назад", callback_data="games_back_menu")

    keyboard.add(button1, button2, button3)

    return keyboard

def chhat_keyboard():
    keyboard = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text="💬 Наш чат", url="https://t.me/+UKC0RlGKxt81YTE6")
    keyboard.add(button1)

    return keyboard

def understand_keyboard():
    keyboard = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text="💬 Наш чат", url="https://t.me/+UKC0RlGKxt81YTE6")
    keyboard.add(button1)

    return keyboard


def jackpot_keyboard(game_name):
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton(text="🎰 Внести ставку", callback_data=game_callback.new(
        game_name=game_name, action="enjoy"
    ))
    button2 = InlineKeyboardButton(text="🏦 Банк джекпота", callback_data=game_callback.new(
        game_name=game_name, action="bank"
    ))

    button3 = InlineKeyboardButton(text="📊 Статистика", callback_data=game_callback.new(
        game_name=game_name, action="statistic"
    ))


    button5 = InlineKeyboardButton(text="🔙 Назад", callback_data="games_back_menu") 

    keyboard.add(button1, button2, button3)
    keyboard.add(button5)


    return keyboard
    

def jackpot_bank_keyboard(game_name):
    keyboard = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text="♻ Обновить", callback_data=game_callback.new(
        game_name=game_name, action="update_bank"
    ))
    button2 = InlineKeyboardButton(text="💢 Понятно", callback_data="game_jack_pot_main")

    keyboard.add(button1)
    keyboard.add(button2)

    return keyboard


def first_bakkara_keyboard(game_name, game_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton(text=f'➕ Взять еще карту', callback_data=game_info_callback.new(
        game_name=game_name, action="add_card", game_id=game_id
    ))

    keyboard.add(button1)

    return keyboard


def game_menu_keyboard():
    keyboard = InlineKeyboardMarkup()
    
    button1 = InlineKeyboardButton(text="🎴 Baccarat", callback_data='game_bakkara_main'
    )
    button2 = InlineKeyboardButton(text="♠️ BlackJack", callback_data='game_21_main'
    )
    button4 = InlineKeyboardButton(text="🧨 MINES", callback_data='mines_game_play'
    )
    button8 = InlineKeyboardButton(text="🌟 Другое", callback_data='game_other_main'
    )
    button5 = InlineKeyboardButton(text="🎰 SLOTS", callback_data='game_slots_main'
    )
    button6 = InlineKeyboardButton(text="💸 JACKPOT", callback_data='game_jack_pot_main'
    )
    button7 = InlineKeyboardButton(text="❌ Закрыть ❌", callback_data="close"
    )

    keyboard.add(button8)
    keyboard.add(button2, button1)
    keyboard.add(button5,button4)
    keyboard.add(button6)
    keyboard.add(button7)

    return keyboard


def solo_keyboard():
    keyboard = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text="🎰 Slots", callback_data="game_slots_main")
    button2 = InlineKeyboardButton(text="💣 Mines", callback_data="mines_game_play")
    button3 = InlineKeyboardButton(text="⬅️ Back", callback_data="games_back_menu")
    keyboard.row(button1, button2)
    keyboard.row(button3)

    return keyboard

def othee_keyboard():
    keyboard = InlineKeyboardMarkup()
    button3 = InlineKeyboardButton(text="🌟 Другое", callback_data='game_other_main')
    button4 = InlineKeyboardButton(text="🎴 Baccarat", callback_data='game_bakkara_main')
    button5 = InlineKeyboardButton(text="♠️ BlackJack", callback_data='game_21_main')
    button6 = InlineKeyboardButton(text="💸 JACKPOT", callback_data='game_jack_pot_main')
    button7 = InlineKeyboardButton(text="❌ Закрыть ❌", callback_data="close")
    keyboard.row(button4, button3, button5)
    keyboard.row(button6)
    keyboard.row(button7)

    return keyboard

def dice_chat_game_keyboard(game_id: int):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        text="✅ Присоединиться",
        callback_data=f'join_dice_chat:{game_id}'))
    return keyboard
