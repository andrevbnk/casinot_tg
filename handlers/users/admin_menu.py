from aiogram.dispatcher import FSMContext
from aiogram import  types
from aiogram.dispatcher.filters import Command
from aiogram.types import Message, InputFile, CallbackQuery
import re, sqlite3, time
from config import edit_config, link_regex, config
from data.functions.db import get_bakkara_game,get_other_game,get_blackjack_game,get_chat_dice_game_by_id,get_user, update_balance, change_spinup_status, get_all_users, delete_all_game, delete_other_game, delete_blackjack_game, delete_bakkara_game, delete_chat_game
from filters.filters import IsAdmin
from keyboards.inline.admin_menu_keyboards import admin_mailing_menu_keyboard, admin_settings_keyboard, \
    admin_back_keyboard, admin_menu_keyboard, admin_search_user_keyboard
from keyboards.inline.callback_datas import admin_search_user_callback
from keyboards.inline.games_keyboard import understand_keyboard
from loader import dp, bot
from states.states import AdminSearchUserState, AdminChangeBalance, AdminChangeComission, AdminPictureMailing, \
    AdminWithoutPictureMailing, create_promocode
from texts import admin_search_user_text, admin_statistic_text



@dp.message_handler(state=create_promocode.promocode_name)
async def answer_summa(message: types.Message, state: FSMContext):
    try:
        answer = message.text

        with sqlite3.connect('data/database.db') as conn:
            cursor =  conn.execute('SELECT count(*) FROM promocodes WHERE promo_name = ?', (answer, ))
            check = cursor.fetchone()[0]
            cursor.close()
        print(check)
        if check == 0:
            await message.answer(
                text = '💸 Создать промокод\n\n'
                        '<b>Напишите сумму промокода:</b>'
            )
            await state.update_data(promocode_name=answer)
            await create_promocode.next()
        else:
            await state.finish()

            await message.answer('<b>Такой промокод уже создан !!!</b>')
    except Exception as err:

        await state.finish()
        await message.answer(f'<b>Произошла ошибка !!!</b> {err}')

@dp.message_handler(state=create_promocode.promocode_summa)
async def answer_summa(message: types.Message, state: FSMContext):
    try:
        answer = round(float(message.text), 2)

        if answer >= 0:
            await state.update_data(promocode_summa=answer)
            await create_promocode.next()

            cancel = types.InlineKeyboardMarkup(row_width = 1)
            btn1 = types.InlineKeyboardButton(text = 'Отмена', callback_data = 'back_adminka')
            cancel.add(btn1)

            await bot.send_message(
                chat_id=message.from_user.id,
                text = '💸 Создать промокод\n\n'
                        '<b>Напишите количество активаций:</b>',
                reply_markup=cancel
            )
        else:
            await state.finish()
            await message.answer('<b>Минимальная сумма промокода 0 ₽ !!!</b>')

    except:
        await state.finish()
        await message.answer('<b>Произошла ошибка !!!</b>')

@dp.message_handler(state=create_promocode.promocode_activations)
async def answer_summa(message: types.Message, state: FSMContext):
    try:
        promocode_activations = int(message.text)

        if promocode_activations >= 1:
            data = await state.get_data()
            promocode_name = data.get('promocode_name')
            promocode_summa = data.get('promocode_summa')

            with sqlite3.connect('data/database.db') as conn:
                conn.execute('INSERT INTO promocodes (promo_name, summa, activation) VALUES (?,?,?)', (promocode_name, promocode_summa, promocode_activations, ))
                conn.commit()

            await state.finish()

            await bot.send_message(
                chat_id = message.from_user.id,
                text = '🎉 <b>Промокод создан</b>\n\n'
                        f'💸 Сумма: <b>{promocode_summa} ₽</b>\n'
                        f'👤 Активаций: <b>{promocode_activations}</b>\n'
                        f'— Название: <b><code>{promocode_name}</code></b>'
            )

        else:
            await state.finish()
            await message.answer('<b>Активаций должно быть больше 0 !!!</b>')

    except:

        await state.finish()
        await message.answer('<b>Произошла ошибка !!!</b>')
        
    
@dp.callback_query_handler(IsAdmin(), text_startswith="admin:create_a_promocode", state="*")
async def output(call: CallbackQuery):
    try:
        btn_promocode = types.InlineKeyboardMarkup(row_width = 2)
        btn2 = types.InlineKeyboardButton(text = 'ALL', callback_data = 'admin:create_promow')
        btn_promocode.add(btn2)

        await call.message.answer(text = '💸 Создать промокод\n\n'
                                            '<b>Напишите название промокода:</b>')

        await create_promocode.promocode_name.set()

    except:
        await call.message.answer('Ошибка')

@dp.message_handler(IsAdmin(), Command("del"))
async def del_game(message: Message, state: FSMContext):
    try:
        game_id = message.text.split(' ')[2]
        type_game = message.text.split(' ')[1]
        if(type_game == "other"):
            other = get_other_game(game_id)
            delete_other_game(game_id)
            player1 = other[1]
            amount = other[2]
        elif(type_game == "blackjack"):
            blackjack = get_blackjack_game(game_id)
            delete_blackjack_game(game_id)
            player1 = blackjack[1]
            amount = blackjack[9]
        elif(type_game == "bakkara"):
            bakkara = get_bakkara_game(game_id)
            delete_bakkara_game(game_id)
            
            player1 = bakkara[1]
            amount = bakkara[7]
        elif(type_game == "chat"):
            chat = get_chat_dice_game_by_id(game_id)
            delete_chat_game(game_id)
            player1 = chat[2]
            amount = chat[9]
        update_balance(player1,amount)
        await message.answer(f'Игра {game_id} удалена! Пользователю {player1} возращены {amount} RUB!')
    except Exception as err:
        await message.answer(f'Ошибка: {err}\n\nПример команды /del typegame id\nother,blackjack,bakkara,chat ')

@dp.callback_query_handler(IsAdmin(), text_startswith="admin:output", state="*")
async def output(call: CallbackQuery):
    try:
        variant = call.data.split(':')[2]
        user_id = call.data.split(':')[3]
        amount = call.data.split(':')[4]
        user = await bot.get_chat(user_id)
        print(variant,user_id,amount)
        if variant == "accept":

            await bot.send_message(config('channel_payment'),f'''
❕ Вывод Отправлен

♥️ Username: @{user.username}
💸 Сумма: {amount} rub

🎲 Играть в казино: <a href='http://t.me/Gloudbot'>«G:L:O:A:D»</a>
💬 Chat Games: <a href='https://t.me/+lXLIzXS0VHM4MWU6'>Тык</a>
            ''')
            await bot.send_message(user_id,f'<b>✅ Ваша заявка на вывод средств обработана\n\n🚀 Средства в сумме: {amount} RUB отправлены на ваши реквизиты\n\n❤️ Спасибо, что вы с нами!</b>')
            await call.message.edit_text(call.message.text+'\n\nВы подтвердили вывод')
        elif variant == "deny":
            update_balance(user_id,amount)
            await bot.send_message(user_id,'<b>❗Ваш вывод был отменён администратором</b>')
            await call.message.edit_text(call.message.text+'\n\nВы отменили вывод')
    except Exception as err:
        print(err)

@dp.callback_query_handler(IsAdmin(), text_contains="admin:mailing_menu")
async def admin_mailing_menu(call: CallbackQuery):
    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text="Управление рассылками",
                                reply_markup=admin_mailing_menu_keyboard())


@dp.callback_query_handler(IsAdmin(), text_contains="admin:statistic")
async def admin_statistic(call: CallbackQuery):
    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=admin_statistic_text(),
                                reply_markup=admin_back_keyboard())


@dp.callback_query_handler(IsAdmin(), text_contains="admin:settings")
async def admin_settings(call: CallbackQuery):
    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text="Настройки",
                                reply_markup=admin_settings_keyboard())


@dp.callback_query_handler(IsAdmin(), text_contains="admin:back_to_main")
async def back_to_admin_main(call: CallbackQuery):
    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text="Админ меню",
                                reply_markup=admin_menu_keyboard())


@dp.callback_query_handler(IsAdmin(), text_contains="admin:search_user")
async def admin_search_user_1(call: CallbackQuery):
    await call.message.answer(text="Введите ID пользователя.")
    await AdminSearchUserState.user_id.set()


@dp.message_handler(IsAdmin(), state=AdminSearchUserState.user_id)
async def admin_search_user_2(message: Message, state: FSMContext):
    if message.text.isdigit():
        if get_user(message.text) != None:
            await message.answer(text=admin_search_user_text(get_user(message.text)),
                                 reply_markup=admin_search_user_keyboard(message.text))
        else:
            await message.answer(text="Пользователь не найден в базе данных.")
    else:
        await message.answer(text="Неверный ввод.")
    await state.finish()


@dp.callback_query_handler(IsAdmin(), admin_search_user_callback.filter(action="change_balance"))
async def admin_change_balance(call: CallbackQuery, callback_data: dict, state: FSMContext):
    user_id = callback_data["user_id"]
    await state.update_data(user_id=user_id)
    await call.message.answer("<b>❗Введите сумму на которую хотите выдать депозит пользователю.</b>")
    await AdminChangeBalance.amount.set()


@dp.message_handler(IsAdmin(), state=AdminChangeBalance.amount)
async def admin_admin_change_balance_2(message: Message, state: FSMContext):
    if message.text.isdigit():
        data = await state.get_data()
        await state.update_data(user_id=data["user_id"])
        await state.update_data(amount= int(message.text))
        
        await message.answer(text=f"Баланс пользователя <b>{data['user_id']}</b> изменится на <b>{message.text} RUB</b>\n\n"
                                  f"Для подтвреждения действия отправьте <b>+</b>", )
        await AdminChangeBalance.next()
    else:
        await message.answer(text="Неверный ввод.")
        await state.finish()


@dp.message_handler(IsAdmin(), state=AdminChangeBalance.confitm)
async def admin_admin_change_balance_2(message: Message, state: FSMContext):
    if message.text == "+":
        data = await state.get_data()
        await state.update_data(user_id=data["user_id"])
        await state.update_data(amount=data["amount"])
        
        
        update_balance(data["user_id"], data["amount"], add=False)
        with sqlite3.connect('data/database.db') as conn:
            conn.execute('INSERT INTO list_of_deposits (user_id, summa, time) VALUES (?,?,?)', (data["user_id"], data["amount"], time.time(), ))
            conn.commit()
        await message.answer(text="✅ Баланс успешно изменён.")
    else:
        await message.answer(text="Смена баланса отменена.")
    await state.finish()


@dp.callback_query_handler(IsAdmin(), admin_search_user_callback.filter(action="on_spinup"))
async def admin_change_balance(call: CallbackQuery, callback_data: dict):
    user_id = callback_data["user_id"]
    if get_user(user_id)[2] == "False":
        change_spinup_status(user_id, "True")
        await call.message.answer("✅ Подкуртка успешно включена.")
    else:
        await call.message.answer("Подкуртка уже включена.")


@dp.callback_query_handler(IsAdmin(), admin_search_user_callback.filter(action="off_spinup"))
async def admin_change_balance(call: CallbackQuery, callback_data: dict):
    user_id = callback_data["user_id"]
    if get_user(user_id)[2] == "True":
        change_spinup_status(user_id, "False")
        await call.message.answer("✅ Подкуртка успешно выключена.")
    else:
        await call.message.answer("Подкуртка уже выключена.")


@dp.callback_query_handler(IsAdmin(), text_contains="admin:change_markup_percent")
async def admin_change_markup_percent(call: CallbackQuery):
    await call.message.answer(text="Введите новый процент комиссии с игр.")
    await AdminChangeComission.percent.set()


@dp.message_handler(IsAdmin(), state=AdminChangeComission.percent)
async def admin_change_markup_percent_2(message: Message, state: FSMContext):
    if message.text.isdigit():
        if int(message.text) >= 0:
            
            with state.proxy() as data:
                data["percent"] = int(message.text)
            await message.answer(text=f"Процент комисси изменится на <b>{message.text}%</b>\n\n"
                                      f"Для подтвреждения действия отправьте <b>+</b>", )
            await AdminChangeComission.next()
        else:
            await message.answer(text="Процент не может быть отрицательным.")
            await state.finish()
    else:
        await message.answer(text="Неверный ввод.")
        await state.finish()


@dp.message_handler(IsAdmin(), state=AdminChangeComission.confitm)
async def admin_admin_change_balance_2(message: Message, state: FSMContext):
    if message.text == "+":
        with state.proxy() as data:
            percent = data["percent"]
        edit_config("game_percent", str(percent))
        await message.answer(text="✅ Процент комиссии успешно изменён.")
    else:
        await message.answer(text="Смена процента комиссии отменена.")
    await state.finish()


@dp.callback_query_handler(IsAdmin(), text_contains="admin:mailing_with_picture")
async def mailing_with_picture(call: CallbackQuery):
    await call.message.answer(text="Введите текст рассылки.")
    await AdminPictureMailing.text.set()


@dp.callback_query_handler(IsAdmin(), text_contains="admin:mailing_without_picture")
async def mailing_without_picture(call: CallbackQuery):
    await call.message.answer(text="Введите текст рассылки.")
    await AdminWithoutPictureMailing.text.set()


@dp.message_handler(IsAdmin(), state=AdminWithoutPictureMailing.text)
async def mailing_without_picture_1(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await bot.send_message(chat_id=message.chat.id,
                           text="<i>Введите <b>+</b> для запуска рассылки!</i>")

    await AdminWithoutPictureMailing.next()


@dp.message_handler(IsAdmin(), state=AdminWithoutPictureMailing.confirm)
async def mailing_without_picture_2(message: Message, state: FSMContext):
    answer = message.text
    if answer == "+":
        data = await state.get_data()
        text = data["text"]
        await state.finish()
        await bot.send_message(chat_id=message.chat.id,
                               text="<b>Рассылка запущена!</b>")
        errors = 0
        good = 0
        users = get_all_users()
        for user in users:
            try:
                await bot.send_message(chat_id=user[0],
                                       text=text,
                                       reply_markup=understand_keyboard(),
                                       disable_web_page_preview=True)
                good += 1
            except:
                errors += 1
        await bot.send_message(chat_id=message.chat.id,
                               text="✅ Рассылка завершена!\n\n"
                                    f"❗️ Отправлено: {good}\n"
                                    f"❗️ Не отправлено: {errors}\n")
    else:
        await bot.send_message(chat_id=message.chat.id, text="<b>❗️Рассылка отменена.</b>")
        await state.finish()


@dp.message_handler(IsAdmin(), state=AdminPictureMailing.text)
async def mailing_with_picture(message: types.Message, state: FSMContext):
    with state.proxy() as data:
        data["text"] = message.text
    await bot.send_message(chat_id=message.chat.id,
                           text="<i>Отправтьте ссылку на фотографию которую хотите отправить. Загрузить фото можно тут @imgurbot_bot!</i>")

    await AdminPictureMailing.next()


@dp.message_handler(IsAdmin(), state=AdminPictureMailing.picture)
async def mailing_with_picture_2(message: Message, state: FSMContext):
    answer = re.search(link_regex, message.text)
    if answer:
        with state.proxy() as data:
            data["picture"] = message.text
        await bot.send_message(chat_id=message.chat.id,
                         text="<i>Введите <b>+</b> для запуска рассылки!</i>")

        await AdminPictureMailing.next()
    else:
        await bot.send_message(chat_id=message.chat.id,
                         text="<b>Вы не отправили ссылку. Рассылка отменена.</b>")
        await state.finish()


@dp.message_handler(IsAdmin(), state=AdminPictureMailing.confirm)
async def mailing_with_picture_3(message: Message, state: FSMContext):
    with state.proxy() as data:
        text = data["text"]
        picture = data["picture"]
    await state.finish()
    answer = message.text
    if answer == "+":
        await bot.send_message(chat_id=message.chat.id,
                               text="<b>Рассылка запущена!</b>")
        errors = 0
        good = 0
        users = get_all_users()
        for user in users:
            try:
                await bot.send_photo(chat_id=user[0],
                                     photo=InputFile.from_url(picture),
                                     caption=text,
                                     reply_markup=understand_keyboard())
                good += 1
            except Exception as e:
                errors += 1
        await bot.send_message(chat_id=message.chat.id,
                               text="✅Рассылка завершена!\n\n"
                                    f"❗️Отправлено: {good}\n"
                                    f"❗️Не отправлено: {errors}\n")
    else:
        await bot.send_message(chat_id=message.chat.id, text="<b>❗ Рассылка отменена</b>")



@dp.message_handler(IsAdmin(), commands=['clear'])
async def clear_games(message: Message, state: FSMContext):
    log = delete_all_game()
    if not log:
      await message.answer('✅ Игры удалены, все хорошо 👍')
    else:
      await message.answer(f'❌ Игры не удалены, из за какой то ошибки 😔 {log}')