from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from config import config
from data.functions.Banker import checked_btc
from data.functions.db import update_balance, get_user
from filters.filters import IsPrivate, IsPrivateCall,IsGroup
from keyboards.inline.games_keyboard import understand_keyboard
from keyboards.inline.admin_menu_keyboards import action_output
from keyboards.inline.other_keyboards import deposit_keyboard, output_keyboard
from states.states import get_promocode
from loader import dp, bot
from aiogram import types
from.cabinet_menu import dp
from states.states import OutputState, surprise_states
import re,sqlite3, time

# # # Активация промокода
@dp.message_handler(state=get_promocode.promocode)
async def answer_summa(message: types.Message, state: FSMContext):
    try:
        answer = str(message.text)

        with sqlite3.connect('data/database.db') as conn:
            cursor = conn.execute('SELECT count(*) FROM promocodes WHERE promo_name = ?', (answer, ))
            check = (cursor.fetchone())[0]

        if check != 0:
            with sqlite3.connect('data/database.db') as conn:
                cursor = conn.execute('SELECT summa FROM promocodes WHERE promo_name = ?', (answer, ))
                summa = round(float((cursor.fetchone())[0]), 2)
            with sqlite3.connect('data/database.db') as conn:
                cursor = conn.execute('SELECT activation FROM promocodes WHERE promo_name = ?', (answer, ))
                activation = (cursor.fetchone())[0]
            

            

           
            if activation > 0:
                with sqlite3.connect('data/database.db') as conn:
                    cursor = conn.execute('SELECT activated FROM promocodes WHERE promo_name = ?', (answer, ))
                    activated = str((cursor.fetchone())[0])

                activated = activated.split()

                if str(message.from_user.id) not in activated:

                    activated.append(f'{message.from_user.id}')
                    activated = ' '.join(activated)

                    with sqlite3.connect('data/database.db') as conn:
                        conn.execute('UPDATE promocodes SET activated = ? WHERE promo_name = ?', (activated, answer, ))
                        conn.commit()
                    with sqlite3.connect('data/database.db') as conn:
                        conn.execute('UPDATE promocodes SET activation = activation - ? WHERE promo_name = ?', (1, answer, ))
                        conn.commit()

                    with sqlite3.connect('data/database.db') as conn:
                        conn.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (summa, message.from_user.id, ))
                        conn.commit()

                    await state.finish()
                    await bot.send_message(
                        chat_id = message.from_user.id,
                        text = '🥳 <b>Успешная активация промокода!</b>\n\n'
                                f'💸 Сумма: <b>{summa} ₽</b>'
                    )

                else:
                    await state.finish()
                    await message.answer('<b>🧐 Вы уже активировали этот промокод!</b>')
            else:
                await state.finish()
                await message.answer('<b>🥲 Данный промокод закончился, или не существует!</b>')

        else:
            await state.finish()
            await message.answer('<b>🥲 Данный промокод закончился, или не существует!</b>')
    except Exception as err:
        await state.finish()
        await message.answer(f'<b>❗ Произошла ошибка!</b> {err}')

@dp.callback_query_handler(IsPrivateCall(), text="promocode")
async def admin_promocode(call: CallbackQuery):
    try:

        await call.message.edit_text(
            text = "<b>🥰 Вы пытаетесь активировать промокод!</b>\n\n"
                        "<u>✍ Напишите ваш промокод:</u>"
        )

        await get_promocode.promocode.set()
    except:
       await call.message.answer("Ошибка")
@dp.callback_query_handler(IsPrivateCall(), text="deposit")
async def admin_deposit(call: CallbackQuery):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await call.message.answer(text="<b>❗️ Выберите систему пополнения:</b>\n\n⁉️ Не нашли удобного способа?\n<i> ♻️Напиши в лс администратору: @Andrey19976</i>",
                            reply_markup=deposit_keyboard())


@dp.callback_query_handler(IsPrivateCall(), text="deposit:banker")
async def admin_banker(call: CallbackQuery):
    await call.message.answer("<code>Для оплаты чеком, просто отправьте его в чат.</code>\n\n<b>❗ЧЕК ДОЛЖЕН БЫТЬ В ВИДЕ ССЫЛКИ.</b>\n\n<b>❗ЧЕК МОЖЕТ БЫТЬ В ЛЮБОЙ КРИПТОВАЛЮТЕ, СУММА ПОПОЛНЕНИЯ ОКРУГЛЯЕТСЯ ДО ЦЕЛОГО ЧИСЛА.</b>",
                              parse_mode='HTML')



@dp.message_handler(IsPrivate())
async def deposit_btc(message: Message):
    if re.search(r'CryptoBot\?start=', message.text):
        code = message.text
        msg =  await checked_btc(message.chat.id, code)
        await message.answer(msg)

@dp.callback_query_handler(IsPrivateCall(), text="output")
async def output_1(call: CallbackQuery, state: FSMContext):
    user_balance = get_user(call.message.chat.id)[1]
    if user_balance >= 100:
        await call.message.answer(f"Введите сумму вывода от 100 до {user_balance} RUB")
        await OutputState.amount.set()
    else:
        await call.message.answer(f"Ваш баланс меньше 100 RUB")
        await state.finish()


@dp.message_handler(IsPrivate(), state=OutputState.amount)
async def output_2(message: Message, state: FSMContext):
    if message.text.isdigit():
        user_balance = get_user(message.chat.id)[1]
        if 100 <= int(message.text):
            if int(message.text) <= user_balance:
                await state.update_data(amount=int(message.text))
                await message.answer(f"Куда вы хотите вывести баланс.",
                                     reply_markup=output_keyboard())
                await OutputState.next()
            else:
                await message.answer(f"❗ На вашем балансе нет данной суммы.")
                await state.finish()
        else:
            await message.answer(f"❗ <b>Минимальная сумма вывода 100 RUB</b>.")
            await state.finish()
    else:
        await message.answer(f"❗ Неверный ввод.")
        await state.finish()

@dp.callback_query_handler(IsPrivateCall(), state=OutputState.place)
async def output_3(call: CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if call.data == "output:qiwi":
        await state.update_data(place="qiwi")
        await call.message.answer(f"<b>Для вывода по сбп указывайте: номер и банк ❗️</b>\n\n✏️ Пример: +7999999999 Tinkoff\n\nНа вывод действует коммисия <code>5%</code>!\n\nℹ Укажите реквизиты для вывода:")
        await OutputState.next()
    elif call.data == "output:banker":
        await state.update_data(place="banker")
        await state.update_data(place="banker")
        data = await state.get_data()
        amount = data["amount"]
        await call.message.answer(f"❗Вывод\n\n"
                                  f"🤖 Платёжная система: <b>CryptoBot</b>\n\n"
                                  f"💸 Сумма к выводу: <b>{amount}</b> RUB\n\n"
                                  f"✏️ Отправьте: <b>«+»</b> для подтверждения вывода.")
        await OutputState.confirm.set()
    elif call.data == "output:cancel":
        await call.message.answer(f"Заявка на вывод отменена.")
        await state.finish()

@dp.callback_query_handler(IsPrivateCall(), text="deposit:sbp")
async def admin_banker(call: CallbackQuery):
    await call.message.answer("Для того, чтобы пополнить свой баланс вы можете перевести сумму пополнения на:\nYoomoney - <code>2204120110700107</code> \n️\n ❗️Комментарий к переводу: <code>{message.from_user.id}</code> \n<i> ☑️После перевода отправьте чек: @Andrey19976 </i>")

@dp.message_handler(IsPrivate(), state=OutputState.requesites)
async def output_4(message: Message, state: FSMContext):
    data = await state.get_data()
    print(data)
    await state.update_data(requesites=message.text)
    amount = data["amount"]
    await message.answer(f"💰 Сумма вывода: <b>{amount}</b> RUB\n\n"
                         f"📱 Реквезиты: <b>{message.text}</b>\n\n"
                              f"ℹ️Площадка: <b>🥝 Киви \ СБП</b>\n\n"
                              f"Для подтверждения отправьте <b>+</b>")
    await OutputState.confirm.set()


@dp.message_handler(IsPrivate(), state=OutputState.confirm)
async def output_4(message: Message, state: FSMContext):
    if message.text == "+":
        data = await state.get_data()
        
        if data["place"] == "qiwi":
            requesites = data["requesites"]
        amount = data["amount"]
        place = data["place"]
        update_balance(message.chat.id, -amount)
        await message.answer("♥️ Ваша заявка на вывод находится в обработке.\n\n✅ Заявка на вывод будет обработана в течение часа, исключение ночного времени.")
        text = f"""🆕 Новый вывод!

🆔 Telegram ID: {message.chat.id}
👤 INFO: @{message.from_user.username} | <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>
💸 Сумма: {amount}₽
🤖 Платёжная система: {place}\n"""
        if place == "qiwi":
            text += f"🏦 Реквизиты: {requesites}"
        for admin in config("admin_id").split(":"):
            await bot.send_message(chat_id=admin, text=text, reply_markup=action_output(message.from_user.id, amount))
    await state.finish()


@dp.callback_query_handler(IsPrivateCall(), text="surprise")
async def surprise(call: CallbackQuery):
    user_balance = get_user(call.message.chat.id)[1]
    await call.message.answer(
        f"ℹВведите 🆔 пользователя и сумму перевода через пробел\n"
        
        "✍ Пример: 123456789 10")
    await surprise_states.id_amount.set()


@dp.message_handler(IsPrivate(), state=surprise_states.id_amount)
async def surprise(message: Message, state: FSMContext):
    print(message.text)
    try:
        user_id, amount = map(int, message.text.split())
    except:
        await message.answer("<b>❌ Подарок отменён.</b>")
        await state.finish()
        return
    print(int(get_user(message.from_user.id)[1]), int(amount))
    if "-" in str(amount):
        await message.answer("❌ <b>Соси багоюзер, я тебя ща в полицию сдам дебилка</b>.")
    elif int(get_user(message.from_user.id)[1]) < int(amount):
        await message.answer("❌ <b>Недостаточно средств для перевода.</b>")
    else:
        if get_user(user_id) == None:
            await message.answer("❌ Этот пользователь не зарегистрирован в боте.")
        else:
            update_balance(message.from_user.id, -amount)
            update_balance(user_id, +amount)
            await bot.send_message(user_id,
                                f"✅ <b>Вам пришел подарок в размере</b>: {amount} RUB.\n💸 <b>Отправитель</b>: @{message.from_user.username}")
            await message.answer(f"✅ <b>Передача средств завершена успешно, с вашего баланса снята сумма в размере: {amount} RUB.</b>")
    await state.finish()
