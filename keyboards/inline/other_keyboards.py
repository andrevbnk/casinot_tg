from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import config
from keyboards.inline.callback_datas import fast_callback


def info_keyboard():
    keyboard = InlineKeyboardMarkup()
    #keyboard.row(InlineKeyboardButton(text="🚀 Хочу такого-же бота", url="https://t.me/JamronProg"),
    keyboard.row(InlineKeyboardButton(text="📰 Соглашение проекта", url="https://telegra.ph/Obshchie-pravila-bota-i-chata-09-10"))
    keyboard.row(InlineKeyboardButton(text="💬 Чат", url="https://t.me/+UKC0RlGKxt81YTE6"))
    keyboard.row(InlineKeyboardButton(text="💈 Новости", url="https://t.me/Klauis_News"))
    #keyboard.row(InlineKeyboardButton(text="🔙 Назад", callback_data="output:cancel"))
    keyboard.row(InlineKeyboardButton(text="ℹ Владелец", url="https://t.me/"))
    keyboard.row(InlineKeyboardButton(text="❌Закрыть❌", callback_data="close"))
    return keyboard

def cabinet_keyboard():
    keyboard = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text="☔️ Пополнить ☔️", callback_data="deposit")
    button2 = InlineKeyboardButton(text="🌧 Вывести 🌧", callback_data="output")
    button3 = InlineKeyboardButton(text="📉 Партнерка 📉", callback_data="partners_menu")
    #button4 = InlineKeyboardButton(text="🎁 Сделать подарок", callback_data="surprise")
    button5 = InlineKeyboardButton(text="🌟 Промокод 🌟", callback_data="promocode")
    button6 = InlineKeyboardButton(text="❌Закрыть❌", callback_data="close")

    keyboard.row(button1, button2)
    keyboard.row(button3)
    keyboard.row(button5)
    keyboard.row(button6)
    return keyboard



def deposit_keyboard():
    keyboard = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text="🔥 Другое", callback_data="method_balance:q")
    button3 = InlineKeyboardButton(text="🔥 Платежная система", callback_data="method_balance:a")
    button7 = InlineKeyboardButton(text="🔥 TON", callback_data="method_balance:t")
    button4 = InlineKeyboardButton(text="⚒ Через поддержку", url=f"https://t.me/Andrey19976")
    button5 = InlineKeyboardButton(text="CryptoBot[ЧЕК]", callback_data="deposit:banker")
    #button6 = InlineKeyboardButton(text="🔙 Назад", callback_data="output:cancel")
    button6 = InlineKeyboardButton(text="❌Закрыть❌", callback_data="close")
    keyboard.row(button5, button1)
    keyboard.row(button3, button7)
    keyboard.row(button4)
    keyboard.row(button6)

    return keyboard

def get_pay_aaio_keyboard(url, order_id):
    keyboard = InlineKeyboardMarkup()
    
    keyboard.add(InlineKeyboardButton(text='💳 Оплатить', url=url))
    keyboard.add(InlineKeyboardButton(text='✅ Проверить', callback_data=f'co:{order_id}'))
    return keyboard

def get_pay_ton_keyboard(url, order_id):
    keyboard = InlineKeyboardMarkup()
    
    keyboard.add(InlineKeyboardButton(text='💳 Оплатить', url=url))
    keyboard.add(InlineKeyboardButton(text='✅ Проверить', callback_data=f'ct:{order_id}'))
    return keyboard


async def sosm_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text="Начни аукцион сейчас!",url="https://t.me/+jesjeZdowCk0ZjFi"))
    return keyboard

def output_keyboard():
    keyboard = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text="🥝 Киви / СБП", callback_data="output:qiwi")
    button2 = InlineKeyboardButton(text="CryptoBot", callback_data="output:banker")
    button3 = InlineKeyboardButton(text="🔙 Назад", callback_data="output:cancel")
    keyboard.row(button1, button2)
    keyboard.row(button3)

    return keyboard


def p2p_deposit_keyboard(bill_id, url):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text='💸 Оплатить 💸', url=url))
    keyboard.add(
        InlineKeyboardButton(text='🔁 Проверить платёж', callback_data=f'check_p2p_deposit:{bill_id}'),
        InlineKeyboardButton(text='❌ Отменить', callback_data=f'reject_p2p_payment')
        )
    return keyboard


async def check_menu(cost, user_id):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="↗️Перейти к оплате", url=f"https://qiwi.com/payment/form/99?"
                                                                    f"extra%5B%27account%27%5D="
                                                                    f"{config('QIWI_ADDRESS')}&amountInteger="
                                                                    f"{cost}&amountFraction=0&"
                                                                    f"extra%5B%27comment%27%5D="
                                                                    f"{user_id}&currency=643&blocked[0]=account&"
                                                                    f"blocked[1]=comment&blocked[2]=sum")
            ],
            [
                InlineKeyboardButton(text="✅Проверить оплату", callback_data="check")
            ],
            [
                InlineKeyboardButton(text="⬅️Назад", callback_data="back_to_main_menu")
            ]
        ]
    )
    return markup


back_to_main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️Назад", callback_data="back_to_personal_account")
        ]
    ]
)

rate_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🤩Отзывы🤩", url="https://t.me/BountyX_chat")
        ]
    ]
)

support_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🧑‍💻 Админ", url="https://t.me/vvvv7777zzzz")
        ]
    ]
)

chat_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="💬 CHAT 💬", url="https://t.me/BountyX_chat")
        ]
    ]
)

async def fast_keyboard(chat_id: int, fast_id: int):
    keyboard = InlineKeyboardMarkup(row_width=2).row(
        InlineKeyboardButton(text="Участвовать ✅", callback_data=fast_callback.new(chat_id=chat_id, fast_id=fast_id, action="participate"))
    )
    return keyboard
    

async def fast_close_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2).row(
        InlineKeyboardButton(text="Закрыто ❌", callback_data="close")
    )
    return keyboard
