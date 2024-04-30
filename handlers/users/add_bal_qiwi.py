import asyncio, time, sqlite3, random
import hashlib
from tonrocketapisdk import RocketApi

from urllib.parse import urlencode
from requests.exceptions import ConnectTimeout, ReadTimeout
import requests

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import config
from data.functions.db import get_user, add_stat, select_buy_stat, update_balance, delete_stat, addRefill, create_order_aaio, get_order_by_id_aaio, order_is_done_aaio
from data.functions.functions import get_pay_link, checkPm, findPayment
from keyboards.inline.other_keyboards import check_menu, back_to_main_menu, cabinet_keyboard, get_pay_aaio_keyboard, get_pay_ton_keyboard
from loader import dp, bot
from states.states import balance_states
from texts import cabinet_text
from utils.payments import send_admins

SHOP_ID = 'f'
SHOP_SECRET = ''
SHOP_API = ''

TON_API = ''
TON_COURSE = 115


@dp.callback_query_handler(text="back_to_personal_account", state="*")
async def back_to_personal_account(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text(cabinet_text(get_user(call.from_user.id)),
                                 reply_markup=cabinet_keyboard())


@dp.callback_query_handler(regexp="^method_balance:\w$")
async def add_balance_qiwi_main(call: CallbackQuery):
    if call.data.split(":")[1] == 'q':
        await balance_states.BS1.set()
    elif call.data.split(":")[1] == 'y':
        await balance_states.BS3.set()
    elif call.data.split(":")[1] == 'a':
        await balance_states.BS4.set()
    elif call.data.split(":")[1] == 't':
        await balance_states.BS5.set()
        return await call.message.edit_text("Напишите сумму, которую вы хотите пополнить."
                                 "\n❗️*Внимание*❗️\n`Минимальная сумма пополнения - 0.01 TON`",
                                 parse_mode="MarkDown", reply_markup=back_to_main_menu)
    
    await call.message.edit_text("Напишите сумму, которую вы хотите пополнить."
                                 "\n❗️*Внимание*❗️\n`Минимальная сумма пополнения - 10₽`",
                                 parse_mode="MarkDown", reply_markup=back_to_main_menu)

# Оплата AAIO
@dp.message_handler(state=balance_states.BS4)
async def add_balance_aaio(message: Message, state: FSMContext):
    if float(message.text) >= 10:

        value = int(message.text)

        currency = 'RUB'

        order_id = f'{create_order_aaio(message.from_user.id, value)[0]}|v'

        print(order_id)

        desc = 'Покупка валюты в боте'
        lang = 'ru'

        sign = f':'.join([
            str(SHOP_ID),
            str(value),
            str(currency),
            str(SHOP_SECRET),
            str(order_id)
        ])

        params = {
            'merchant_id': SHOP_ID,
            'amount': value,
            'currency': currency,
            'order_id': order_id,
            'sign': hashlib.sha256(sign.encode('utf-8')).hexdigest(),
            'desc': desc,
            'lang': lang
        }

        await bot.send_message(message.chat.id,
                               f"Счет выставлен, оплатите его и нажмите кнопку проверить!",
                               reply_markup=get_pay_aaio_keyboard("https://aaio.io/merchant/pay?" + urlencode(params), order_id),
                               parse_mode="MarkDown")
        
        await state.finish()
    else:
        await message.answer("Неверное количество, попробуйте еще раз :)")
    

# Проверка платежа
@dp.callback_query_handler(text_startswith='co:', state='*')
async def order_check(call: CallbackQuery, state: FSMContext):
    await state.finish()

    url = 'https://aaio.io/api/info-pay'
    order_id = f'{call.data.split(":")[1]}'

    order = await get_order_by_id_aaio(order_id.replace('|v', ''))
    print(order_id.replace('|v', ''))
    if order[4] == 1:
        await call.message.delete()
        return await call.message.answer(
            'Платеж уже был получен!'
        )

    params = {
        'merchant_id': SHOP_ID,
        'order_id': order_id
    }

    headers = {
        'Accept': 'application/json',
        'X-Api-Key': SHOP_API
    }

    try:
        response = requests.post(url, data=params, headers=headers, timeout=(15, 60))
    except ConnectTimeout:
        print('ConnectTimeout') # Не хватило времени на подключение к сайту
        return await call.message.answer(
            'Платеж не найден!'
        )
    except ReadTimeout:
        print('ReadTimeout') # Не хватило времени на выполнение запроса
        return await call.message.answer(
            'Платеж не найден!'
        )

    if(response.status_code in [200, 400, 401]):
        try:
            response_json = response.json() # Парсинг результата
        except:
            print('Не удалось пропарсить ответ')
            return await call.message.answer(
                'Платеж не найден!'
            )

        if(response_json['type'] == 'success'):
            print(response_json['status']) # Вывод результата

            if response_json['status'] == 'success':
                order_is_done_aaio(order_id.replace('|v', ''))
                value = int(response_json['amount'])

                await call.message.delete()
                await call.message.answer(
                    'Платеж прошёл!\n'
                )

                update_balance(call.from_user.id, value)

                return
            
        else:
            print('Ошибка: ' + response_json['message']) # Вывод ошибки
    else:
        print('Response code: ' + str(response.status_code)) # Вывод неизвестного кода ответа
    
    await call.message.answer(
        'Платеж не найден!'
    )

# Оплата TonRocket
@dp.message_handler(state=balance_states.BS5)
async def add_balance_ton(message: Message, state: FSMContext):
    if float(message.text) >= 0.01:
        value = float(message.text)

        api = RocketApi(TON_API)

        invoice = api.createInvoice({
            "amount": value,
            "description": "Оплата в боте",
            "hiddenMessage": "thank you",
            "callbackUrl": "https://t.me/ton_rocket",
            "payload": "Ну типо тут что-то",
            "expiredIn": 600
        })

        await bot.send_message(message.chat.id,
                               f"Счет выставлен, оплатите его и нажмите кнопку проверить!",
                               reply_markup=get_pay_ton_keyboard(invoice['data']['link'], invoice['data']['id']),
                               parse_mode="MarkDown")
        
        await state.finish()

    else:
        await message.answer("Неверное количество, попробуйте еще раз :)")

# Проверка платежа
@dp.callback_query_handler(text_startswith='ct:', state='*')
async def order_check(call: CallbackQuery, state: FSMContext):
    await state.finish()
    api = RocketApi(TON_API)

    invoice = api.getInvoice({
        'id': call.data.split(":")[1]
    })

    if invoice['data']['status'] == 'paid':
        await call.message.delete()
        value = invoice['data']['amount'] * TON_COURSE
        update_balance(call.from_user.id, value)

        return await call.message.answer(f'Ваш счет пополнен на {value} руб!')

    await call.answer(
        'Платеж не найден!'
    )


##################

@dp.message_handler(state=balance_states.BS1)
async def add_balance_qiwi(message: Message, state: FSMContext):
    if float(message.text) >= 10:

        await bot.send_message(message.chat.id,
                               f"*Для того, чтобы пополнить свой баланс на" 
                               f" {round(float(message.text), 2)}руб вам нужно:*\n\n"
                               f"💰Перевести - `{round(float(message.text), 2)}₽`\n"
                               f"💎На PAYEER - `P1100315883` \n"
                               f"💳На КАРТУ(МИР) - `2200700613606465` \n"
                               f"📃С комментарием - `G{message.from_user.id}`\n"
                               f"После чего отправить чек: @Andrey19976 !",
                               parse_mode="MarkDown")
        
        await state.finish()
    else:
        await message.answer("Неверное количество, попробуйте еще раз :)")
        
        
@dp.message_handler(state=balance_states.BS3)
async def add_balance_ym(message: Message, state: FSMContext):
    if float(message.text) >= 10:
        amount = int(float(message.text))
        passwd = list("1234567890ABCDEFGHIGKLMNOPQRSTUVYXWZ")
        random.shuffle(passwd)
        code = "".join([random.choice(passwd) for x in range(10)])
        link = await get_pay_link(amount=amount, code=code)
        payId = addRefill(message.from_user.id, message.from_user.username,
                          message.from_user.first_name, code, amount)
        asyncio.ensure_future(checkPm(payId))

        ma = InlineKeyboardMarkup(1)
        ma.insert(InlineKeyboardButton('💸 Оплатить счёт', url=link))
        ma.insert(InlineKeyboardButton('✅ Проверить оплату', callback_data=f'findPay|{payId}'))
        await bot.send_message(message.chat.id,
                               f"""<b>🆙 Пополнение баланса

Для того, чтобы пополнить свой баланс на {round(float(message.text), 2)}руб вам нужно:
                               
🟢🟢 Нажать на ссылку ниже: «💸 Оплатить счёт»
➖➖➖➖➖➖➖➖➖➖➖➖➖

♻ Платёж зачислится автоматически, в случае, если оплата будет произведена в течение 30 минут
➖➖➖➖➖➖➖➖➖➖➖➖➖

🔰 Если Вы оплатили позже чем через 30 минут, просто нажмите кнопку «✅ Проверить оплату» Время зачисления до 3 минут</b>""",
                               reply_markup=ma)

        await state.finish()
    else:
        await message.answer("Неверное количество, попробуйте еще раз :)")

@dp.callback_query_handler(Text(startswith=('findPay')))
async def findPayBtn(call: CallbackQuery, state: FSMContext):
    await state.finish()
    pId = call.data.split('|')[1]
    res = await findPayment(pId)
    print(f'rr res["status"]')
    if res['status'] == 'PAID':
        fact = res['am_fact']
        amount = res['amount']
        user_id = res['user_id']
        username = res['username']
        userName = res['userName']
        asyncio.ensure_future(send_admins(f""""💥 {username} | {userName} | <code>{user_id}</code>
Пополнил баланс на {amount} ₽
Фактически пришло {fact} ₽"""))
        with sqlite3.connect('data/database.db') as conn:
                conn.execute('INSERT INTO list_of_deposits (user_id, summa, time) VALUES (?,?,?)', (user_id, amount, time.time(), ))
                conn.commit()
        return await call.message.edit_text(f"✅ Пополнение прошло успешно, <code>на ваш баланс зачислено: {fact} руб.</code>",
                                            reply_markup=InlineKeyboardMarkup().insert(InlineKeyboardButton("Вернуться", callback_data='back_to_personal_account')))
    else:
        return await call.message.edit_text("<b>🔎 Ищём ваш платёж...</b>",
                                            reply_markup=InlineKeyboardMarkup().insert(InlineKeyboardButton("Вернуться", callback_data='back_to_personal_account')))
