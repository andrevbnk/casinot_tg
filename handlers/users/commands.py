from loader import dp, bot
from config import config
from aiogram.types import CallbackQuery, Message

from data.functions.db import get_user, add_user_to_db, create_fast_kon,add_members,get_members_user,get_fast,get_members, update_balance
from filters.filters import IsPrivate, IsAdmin
from keyboards.inline.admin_menu_keyboards import admin_menu_keyboard
from keyboards.inline.other_keyboards import fast_keyboard, fast_close_keyboard
from keyboards.reply.reply_keyboards import main_menu_keyboard
from keyboards.inline.callback_datas import fast_callback
from keyboards.inline.other_keyboards import sosm_keyboard
from utils.payments import send_safe

import asyncio, random, sqlite3, time, logging
from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import Message
from aiogram.dispatcher import FSMContext

@dp.message_handler(IsPrivate(), Command("start"))
async def answer_start(message: Message, state: FSMContext):
    await state.finish()
    if get_user(message.chat.id) == None:
        add_user_to_db(message.chat.id, message.get_args())
        if message.get_args() and get_user(int(message.get_args())):
          await send_safe(message.get_args(), 'У вас новый реферал!')
    await state.finish()
    await message.answer(text="Главное меню",
                        reply_markup=main_menu_keyboard())

@dp.message_handler(IsPrivate(), Command("admin"))
async def admin_menu(message: Message):
    if get_user(message.chat.id) != None:
        if str(message.chat.id) in str(config("admin_id")):
            await message.reply(text ="<b>♻️ Добро пожаловать в админ меню, выберите дальнейшее действие 👇.</b>",
                                 reply_markup=admin_menu_keyboard())
            

@dp.message_handler(IsAdmin(), commands=["fastdep"])
async def create_fast(message: Message):
    try:
        args =  message.get_args().split(' ')
        deposit = args[0]
        summa = args[1]
        print(args)

        fast_id = random.randint(111111, 999999)

        emoji_captcha = ['🔒', '🧷', '📕', '📯', '🏮', '🎀', '🧸', '🛎', '🔑', '🧬', '🦠', '⚰️', '🪓', '🧨', '💣', '🔫',
                        '🗡', '⚱️', '💎', '⚖️', '💸', '📺', '🛕', '🏰', '🗿', '⚓️', '🚀', '✈️', '🛸', '🚜', '🚨', '🎰',
                        '🎲', '🎮', '🎸', '🎬', '🥁', '🏆', '🥎', '🏈', '⚽️', '🥊', '🍺', '🍫', '🍩', '🍙', '🍔', '🍎',
                        '🍇', '🍅', '❄️', '☀️', '🌪', '⚡️', '🔥', '🐊', '🦑', '🐷', '🐸', '🙈', '👑', '🎩', '💃', '☠️',
                        '👻', '👹', '🤡', '💩', '🤖', '👾', '👽', '🎃', '🤎', '❤️', '🖤']

        emoji_captcha_random = random.sample(emoji_captcha, k=6)
        captcha = random.choice(emoji_captcha_random)

        with sqlite3.connect('data/database.db') as conn:
            conn.execute('INSERT INTO list_of_autofast (fast_id, captcha, summa, deposit) VALUES (?,?,?,?)', (fast_id, captcha, summa, deposit, ))
            conn.commit()

        autofast_keyboard = types.InlineKeyboardMarkup(row_width = 3)
        btn1 = types.InlineKeyboardButton(text = f'{emoji_captcha_random[0]}', callback_data = f'autofastdep_connect_{fast_id}_{emoji_captcha_random[0]}')
        btn2 = types.InlineKeyboardButton(text = f'{emoji_captcha_random[1]}', callback_data = f'autofastdep_connect_{fast_id}_{emoji_captcha_random[1]}')
        btn3 = types.InlineKeyboardButton(text = f'{emoji_captcha_random[2]}', callback_data = f'autofastdep_connect_{fast_id}_{emoji_captcha_random[2]}')
        btn4 = types.InlineKeyboardButton(text = f'{emoji_captcha_random[3]}', callback_data = f'autofastdep_connect_{fast_id}_{emoji_captcha_random[3]}')
        btn5 = types.InlineKeyboardButton(text = f'{emoji_captcha_random[4]}', callback_data = f'autofastdep_connect_{fast_id}_{emoji_captcha_random[4]}')
        btn6 = types.InlineKeyboardButton(text = f'{emoji_captcha_random[5]}', callback_data = f'autofastdep_connect_{fast_id}_{emoji_captcha_random[5]}')
        autofast_keyboard.add(btn1, btn2, btn3, btn4, btn5, btn6)

        await message.answer(f'''

<b>🎲 Розыгрыш [KLAUIS] 🎲</b>

ℹ️ Принять участие могут те, кто пополнял {deposit} ₽ в течение 24ч.

💸 Сумма: {summa} ₽
👤 Первые 6 человек

♻️ <b>Для участия нажмите на</b> {captcha}
''',
            reply_markup = autofast_keyboard
        )

    except Exception as err:
        await message.answer(f'Ошибка {err}')


# # # Обработчик автофаст депозитный
@dp.callback_query_handler(text_startswith=['autofastdep_connect_'], state='*')
async def callback_inline(call: types.CallbackQuery, state: FSMContext):
    try:
        data = call.data[20:]
        fast_id = data.split('_')[0]
        captcha_user = data.split('_')[1]

        user_id = call.from_user.id

        with sqlite3.connect('data/database.db') as conn:
            cursor = conn.execute('SELECT * FROM list_of_autofast WHERE fast_id = ?', (fast_id, ))
            autofast = cursor.fetchall()

        for row in autofast:
            if row[1] == captcha_user:
                deposit48 = await deposit_check(user_id, 24)
                if deposit48 >= row[3]:
                    try:
                        users = row[4].split()
                    except:
                        users = []
                    if str(user_id) not in users:
                        users.append(str(user_id))
                        str_users = ' '.join(users)

                        with sqlite3.connect('data/database.db') as conn:
                            conn.execute(f'UPDATE list_of_autofast SET users = ? WHERE fast_id = ?', (str_users, row[0], ))
                            conn.commit()

                        await bot.answer_callback_query(call.id, text='🎉 Вы приняли участие!', show_alert = True)

                    else:
                        await bot.answer_callback_query(call.id, text='😐 Вы уже участвуете!', show_alert = True)
                else:
                    await bot.answer_callback_query(call.id, text=f'❗ Для участия необходим депозит от {row[3]} ₽ за 24ч!', show_alert = True)
            else:
                await bot.answer_callback_query(call.id, text='Капча пройдена не правильно !!!', show_alert = True)

        with sqlite3.connect('data/database.db') as conn:
            cursor = conn.execute('SELECT * FROM list_of_autofast WHERE fast_id = ?', (fast_id, ))
            autofast_stop = cursor.fetchall()
        for row in autofast_stop:
            try:
                users = row[4].split()
            except:
                users = []
            if len(users) >= 6:
                with sqlite3.connect('data/database.db') as conn:
                    conn.execute('DELETE FROM list_of_autofast WHERE fast_id = ?', (row[0], ))
                    conn.commit()

                await call.message.edit_reply_markup(
                    reply_markup = None
                )
                name1 = await bot.get_chat(users[0])
                name1 = name1.first_name
                name2 = await bot.get_chat(users[1])
                name2 = name2.first_name
                name3 = await bot.get_chat(users[2])
                name3 = name3.first_name
                name4 = await bot.get_chat(users[3])
                name4 = name4.first_name
                name5 = await bot.get_chat(users[4])
                name5 = name5.first_name
                name6 = await bot.get_chat(users[5])
                name6 = name6.first_name

                await call.message.answer(
                    
                    text = '✅ <b>Участники набраны:</b>\n\n'
                            f'1. <a href="tg://user?id={users[0]}">{name1}</a>\n'
                            f'2. <a href="tg://user?id={users[1]}">{name2}</a>\n'
                            f'3. <a href="tg://user?id={users[2]}">{name3}</a>\n'
                            f'4. <a href="tg://user?id={users[3]}">{name4}</a>\n'
                            f'5. <a href="tg://user?id={users[4]}">{name5}</a>\n'
                            f'6. <a href="tg://user?id={users[5]}">{name6}</a>\n\n'
                            '<b>🥇 Победителя выберет кубик, всем удачи! :)</b>'
                )

                await asyncio.sleep(2)

                fast_msg = await call.message.answer_dice( emoji = '🎲')

                fast_value = fast_msg.dice.value - 1

                winner = await bot.get_chat(users[fast_value])
                print(winner)
                winner = winner.first_name
                
                await asyncio.sleep(3)

                with sqlite3.connect('data/database.db') as conn:
                    conn.execute(f'UPDATE users SET balance = balance + ? WHERE user_id = ?', (row[2], users[fast_value], ))
                    conn.commit()

                await call.message.answer(
                    
                    text = f'🥳 <b>Поздравляем победителя: <a href="tg://user?id={users[fast_value]}">{winner}</a></b>\n\n❤️ <b>Другим участникам удачи в следующих конкурсах!</b>'
                )
                await bot.send_message(chat_id=users[fast_value],
                    text = f'<b>🥳 Поздравляем, вы выиграли {row[2]} ₽ в розыгрыше!</b>'
                )

    except Exception as err:
        print(err)

 # # Проверка депозитов
async def deposit_check(user_id, hours):
    try:

        seconds = hours * 60 * 60
        deposit_sum = 0

        with sqlite3.connect('data/database.db') as conn:
            cursor =  conn.execute('SELECT * FROM list_of_deposits WHERE user_id = ?', (user_id, ))
            list_deposit = cursor.fetchall()
        print(f'list_deposit {list_deposit}')
        for row in list_deposit:
            if time.time() - float(row[2]) <= seconds:
                deposit_sum += int(row[1])

        with sqlite3.connect('data/database.db') as conn:
            cursor =  conn.execute('SELECT * FROM list_of_deposits')
            list_deposit_all = cursor.fetchall()

        for row in list_deposit_all:
            if time.time() - float(row[2]) >= 259200:
                with sqlite3.connect('data/database.db') as conn:
                    conn.execute('DELETE FROM list_of_deposits WHERE time = ?', (row[2], ))
                    conn.commit()

        return deposit_sum
    except:
        logging.exception('message')





@dp.callback_query_handler(text="sos")
async def sos_message(call: CallbackQuery):
    await call.message.edit_caption("<b>🆘 Если у вас случилась проблему обратись в нашу тех поддержку:</b>",
                                    reply_markup=sosm_keyboard)



    
@dp.message_handler(IsAdmin(), commands=["fast", "фаст"])
async def create_fast(message: Message):
    try:
        amount = message.get_args()
        if not amount.isdigit():
            await message.reply("❌ Аргумент должен быть числом.")

        else:
            create = await create_fast_kon(chat_id=message.chat.id, amount=amount)
            await message.answer(f'''
<b>🎲 Розыгрыш 🎲

💸 Сумма:</b> <code>{amount}</code> ₽

<i>ℹ Для участия, нажмите на кнопку ниже:</i> <code>«✅ Участвовать»</code>

<b>👤 Только первые 6⃣ человек!
🥇 Победителя выберет кубик! (🎲)</b>
                        ''',reply_markup=await fast_keyboard(message.chat.id, create))
    except Exception as err:
        print(f'Fast {err}')
                
                
@dp.callback_query_handler(fast_callback.filter(action="participate"))
async def participate(call: types.CallbackQuery, callback_data: dict):
    fast_id = int(callback_data["fast_id"])
    fast = await get_fast(fast_id)
    members_fast = await get_members(fast_id)
    if len(members_fast) < 6:
        user_fast = await get_members_user(fast_id, call.from_user.id)
        if not user_fast:
            await add_members(fast_id, call.from_user.id, call.from_user.first_name)
            await call.answer('✅ Участие в фасте успешно. Ожидай результатов!', show_alert=True)
            members_fast = await get_members(fast_id)
        else:
            await call.answer('🤨 Ты уже учавствуешь в фасте!', show_alert=True)

    members_fast = await get_members(fast_id)
    if len(members_fast) == 6:
        await call.message.edit_reply_markup(await fast_close_keyboard())
        text = f"🚀 Розыгрыш №{fast_id} начинается, участвуют:\n\n"
        for i in range(6):
            num = i+1
            text += f"{num}. <a href='tg://user?id={members_fast[i][1]}'>{members_fast[i][2]}</a>\n"
        await call.message.reply(text, parse_mode="HTML")
        emoji = await call.message.answer_dice(emoji="🎲")
        await asyncio.sleep(3)
        win = emoji.dice.value - 1
        update_balance(members_fast[win][1], fast[2])
        await call.message.reply(f"🥳 Победил игрок №{emoji.dice.value}\n💎 Игрок <a href='tg://user?id={members_fast[win][1]}'>{members_fast[win][2]}</a> поздравляю тебя, ты выигрываешь <code>{fast[2]}</code> RUB!", parse_mode="HTML")
        
