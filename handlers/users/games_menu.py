import random
import time

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InputFile, Message

from config import games_photo, other_games_info, config, slots_values, bakkara_values, slots_photo, other_games_photo, \
    blackjack_photo, bakkara_photo, jackpot_photo, blackjack_values
from data.functions.db import get_user, add_other_game_to_db, get_other_game, update_balance, add_blackjack_game_to_db, \
    get_blackjack_game, update_player_blackjack, update_blackjack_game_status, add_card_to_player, \
    delete_blackjack_game, get_user_other_lose_amount, get_user_other_game_win_amount, get_user_other_game_win_sum, \
    get_user_other_game_lose_sum, add_game_log, get_user_blackjack_lose_amount, get_user_blackjack_game_win_amount, \
    get_user_blackjack_game_win_sum, get_user_blackjack_game_lose_sum, add_bakkara_game_to_db, \
    update_bakkara_game_status, update_player_bakkara, get_bakkara_game, add_card_to_bakkara_player, \
    delete_bakkara_game, get_user_bakkara_game_lose_sum, get_user_bakkara_lose_amount, get_user_bakkara_game_win_amount, \
    get_user_bakkara_game_win_sum, add_cards_to_bakkara_player, get_jackpot_bets, get_jackpot_bets_amount, \
    add_jackpot_bet, get_jackpot_end_time, add_slots_log, get_user_jackpot_win_sum, get_user_jackpot_win_amount, \
    get_user_slots_game_amount, get_user_slots_game_bet_amount, get_user_slots_win_sum, get_user_slots_lose_sum
from data.functions.functions import get_first_bakkara_screen, add_bakkara_card, get_bakkara_result, delete_game_photos, send_chats
from filters.filters import IsPrivate, IsPrivateCall
from keyboards.inline.callback_datas import game_callback, game_info_callback, other_game_callback
from keyboards.inline.games_keyboard import games_control_keyboard, other_games_types, games_info_keyboard, \
    blackjack_keyboard, slots_menu_keyboard, understand_keyboard, jackpot_keyboard, jackpot_bank_keyboard, \
    first_bakkara_keyboard, solo_keyboard, othee_keyboard
from keyboards.reply.reply_keyboards import play_slots_keyboard, main_menu_keyboard
from loader import dp, bot
from states.states import OtherGameState, BlackjackGameState, SlotsGameState, BakkaraGameState, JackpotGameState
from texts import statistic_text, jackpot_statistic_text, slots_statistic_text
from utils.games.play_other_games import PlayOtherGames


@dp.callback_query_handler(IsPrivateCall(), game_callback.filter(action="update"))
async def other_game_menu(call: CallbackQuery, callback_data: dict):
    if callback_data["game_name"] == "blackjack":
        photo=InputFile('filaro.jpg')
    elif callback_data["game_name"] == "bakkara":
        photo=InputFile('filaro.jpg')
    elif callback_data["game_name"] == "other":
        photo=InputFile('filaro.jpg')
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await bot.send_photo(chat_id=call.message.chat.id,
                         caption="🖲 Создайте свою либо присоединитесь к существующим играм",
                         photo=InputFile('filaro.jpg'),
                         reply_markup=games_control_keyboard(callback_data["game_name"]))


@dp.callback_query_handler(IsPrivateCall(), text="solo_games_main", state='*')
async def slots_game_menu(c: CallbackQuery, state: FSMContext):
    await state.finish()
    if get_user(c.from_user.id) != None:
        await c.message.edit_reply_markup(reply_markup=solo_keyboard())


@dp.callback_query_handler(IsPrivateCall(), text="game_slots_main", state='*')
async def slots_game_menu(c: CallbackQuery, state: FSMContext):
    await state.finish()
    if get_user(c.from_user.id) != None:
        await c.message.delete()
        await bot.send_photo(chat_id=c.message.chat.id,
                             photo=InputFile('filaro.jpg'),
                             reply_markup=slots_menu_keyboard("slots"))



@dp.callback_query_handler(IsPrivateCall(), game_callback.filter(game_name="jackpot", action="statistic"))
async def get_jackpot_stats(call: CallbackQuery, callback_data: dict):
    user_id = call.message.chat.id
    await call.message.delete()
    win_amount = get_user_jackpot_win_amount(user_id)
    win = get_user_jackpot_win_sum(user_id)
    await call.message.answer(text=jackpot_statistic_text(win_amount, win),
                              reply_markup=understand_keyboard())


@dp.callback_query_handler(IsPrivateCall(), game_callback.filter(game_name="jackpot", action="bank"))
async def play_slots(call: CallbackQuery, callback_data: dict):
    await call.message.delete()
    bets = get_jackpot_bets()
    if len(bets) == 0:
        bank = "В этом раунде еще никто не ставил."
    else:
        bets_sum = get_jackpot_bets_amount()
        bank = f"Ставок на сумму: {bets_sum} RUB\n\n"
        for bet in bets:
            percent = round(bet[1] / (bets_sum / 100))
            user = await bot.get_chat(bet[0])
            bank += f"<a href='t.me//{bet[0]}'>{user.first_name}</a> поставил {bet[1]} RUB\n"
            bank += f"Шанс на победу: {int(percent)}%\n\n"
        if len(bets) >= 2:
            bank += f"\nДо конца раунда осталось {int(get_jackpot_end_time() - time.time())} секунд"
    await call.message.answer(text=f"{bank}", reply_markup=jackpot_bank_keyboard("jackpot"))


@dp.callback_query_handler(IsPrivateCall(), game_callback.filter(game_name="jackpot", action="enjoy"))
async def enjoy_jackpot_1(call: CallbackQuery, callback_data: dict):
    await call.message.delete()
    await JackpotGameState.bet_amount.set()
    await call.message.answer(text="Введите сумму ставки.")


@dp.message_handler(IsPrivate(), state=JackpotGameState.bet_amount)
async def enjoy_jackpot_2(message: Message, state: FSMContext):
    await message.delete()
    if message.text.isdigit():
        if float(message.text) >= 10:
            if get_user(message.chat.id)[1] >= float(message.text):
                update_balance(message.chat.id, -float(message.text))
                add_jackpot_bet(message.chat.id, float(message.text))
                if message.from_user.username:
                  username = f'@{message.from_user.username}'
                else:
                  username = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.id}</a>'
                await send_chats(f'💎 JACKPOT 💎\n\n{username} Поставил\n <b>{float(message.text)} RUB</b>')
                await message.answer(text="✅")
                await message.answer(text="Ваша ставка успешно принята")
            else:
                await message.answer(text="Недостаточно средств для создания игры.")
        else:
            await message.answer(text="❔ Минимальная сумма ставки равна 10.")
    else:
        await message.answer(text="❕ Неверный ввод.")
    await state.finish()


@dp.callback_query_handler(IsPrivateCall(), game_callback.filter(game_name="jackpot", action="update_bank"))
async def jackpot_update_bank(call: CallbackQuery, callback_data: dict):
    bets = get_jackpot_bets()
    if len(bets) == 0:
        bank = "В этом раунде еще никто не ставил."
    else:
        bets_sum = get_jackpot_bets_amount()
        bank = f"Ставок на сумму: {bets_sum} RUB\n\n"
        for bet in bets:
            percent = round(bet[1] / (bets_sum / 100))
            user = await bot.get_chat(bet[0])
            bank += f"@{user.username} поставил {bet[1]} RUB\n"
            bank += f"Шанс на победу: {int(percent)}%\n\n"
        if len(bets) >= 2:
            bank += f"\nДо конца раунда осталось {int(get_jackpot_end_time() - time.time())} секунд"
    try:
      await call.message.edit_text(text=f"{bank}", reply_markup=jackpot_bank_keyboard("jackpot"))
    except Exception as e:
      print(e)


@dp.callback_query_handler(IsPrivateCall(), game_callback.filter(game_name="slots", action="play"))
async def play_slots(call: CallbackQuery, callback_data: dict):
    await SlotsGameState.bet_amount.set()
    await call.message.answer(text="Введите сумму ставки.")


@dp.callback_query_handler(IsPrivateCall(), game_callback.filter(game_name="slots", action="statistic"))
async def get_blackjack_stats(call: CallbackQuery, callback_data: dict):
    user_id = call.message.chat.id
    games_amount = get_user_slots_game_amount(user_id)
    bet_sum = get_user_slots_game_bet_amount(user_id)
    win_sim = get_user_slots_win_sum(user_id)
    lose_sum = get_user_slots_lose_sum(user_id)
    await call.message.answer(text=slots_statistic_text(games_amount, bet_sum, win_sim, lose_sum),
                              reply_markup=understand_keyboard())


@dp.message_handler(IsPrivate(), state=SlotsGameState.bet_amount)
async def play_slots_2(message: Message, state: FSMContext):
    if message.text.isdigit():
        if int(message.text) >= 10:
            if get_user(message.chat.id)[1] >= int(message.text):
                await message.answer(text="slots info",
                                     reply_markup=play_slots_keyboard(message.text))
            else:
                await message.answer(text="Недостаточно средств для игры.")
        else:
            await message.answer(text="❔ Минимальная сумма ставки равна 10.")
    else:
        await message.answer(text="❕ Неверный ввод.")
    await state.finish()


@dp.message_handler(IsPrivate(), text_contains="📍 Вращать | Ставка:")
async def play_slots_3(message: Message):
    if message.text.startswith("📍 Вращать | Ставка:"):
        try:

            bet = int(message.text.split(":")[-1])

            if "-" not in message.text and get_user(message.chat.id)[1] >= bet:

                update_balance(message.chat.id, -int(bet))

                value = await bot.send_dice(message.chat.id, emoji="🎰")

                result = int(value.dice.value)

                if result in slots_values["2_same"]:
                    update_balance(message.chat.id, int(bet * 1.75))
                    win = "True"
                    win_amount = int(bet * 1.75)
                    await message.answer(text="Вы выиграли ваша ставка умножена x1.75.")

                elif result in slots_values["3_same"]:
                    update_balance(message.chat.id, int(bet * 2.5))
                    win = "True"
                    win_amount = int(bet * 2.5)
                    await message.answer(text="Вы выиграли ваша ставка умножена x2.5.")

                elif result == 64:
                    update_balance(message.chat.id, int(bet * 5))
                    win = "True"
                    win_amount = int(bet * 5)
                    await message.answer(text="Вы выиграли ваша ставка умножена x5.")
                else:
                    win = "False"
                    win_amount = 0
                add_slots_log(message.chat.id, bet, win, win_amount)
            else:
                await message.answer(text="Недостаточно средств для создания игры.")

        except:
            pass


@dp.message_handler(IsPrivate(), text_contains="🔁 Изменить ставку")
async def slots_edit_bet(message: Message, state: FSMContext):
    await SlotsGameState.bet_amount.set()
    await message.answer(text="Введите сумму ставки.")


@dp.message_handler(IsPrivate(), text_contains="⏪ Выход")
async def slots_leave_game(message: Message, state: FSMContext):
    await message.answer(text="Главное меню",
                         reply_markup=game_menu_keyboard())



@dp.callback_query_handler(IsPrivateCall(), text="game_21_main")
async def blackjack_game_menu(с: CallbackQuery):
    await с.message.delete()
    if get_user(с.from_user.id) != None:
        await bot.send_photo(chat_id=с.from_user.id,
                             caption="🖲 Создайте свою либо присоединитесь к существующим играм",
                             photo=InputFile('filaro.jpg'),
                             reply_markup=games_control_keyboard("blackjack"))


@dp.callback_query_handler(IsPrivateCall(), text="game_jack_pot_main")
async def blackjack_game_menu(с: CallbackQuery):
    await с.message.delete()
    if get_user(с.from_user.id) != None:
        await bot.send_photo(chat_id=с.from_user.id,
                             caption="🖲 Играй с другими игроками и сорви ДЖЕКПОТ!",
                             photo=InputFile('filaro.jpg'),
                             reply_markup=jackpot_keyboard("jackpot"))


@dp.callback_query_handler(IsPrivateCall(), game_callback.filter(game_name="blackjack", action="create"))
async def create_blackjack_game_1(call: CallbackQuery, callback_data: dict):
    await BlackjackGameState.bet_amount.set()
    await call.message.answer(text="Введите сумму ставки.")


@dp.message_handler(IsPrivate(), state=BlackjackGameState.bet_amount)
async def create_blackjack_game_2(message: Message, state: FSMContext):
    if message.text.isdigit():
        if int(message.text) >= 10:
            if get_user(message.chat.id)[1] >= int(message.text):
                game_id = random.randint(1111111, 9999999)
                update_balance(message.chat.id, -int(message.text))
                add_blackjack_game_to_db(game_id, message.chat.id, message.text)
                await message.answer(text="Игра успешно создана.")
                if message.from_user.username:
                  username = f'@{message.from_user.username}'
                else:
                  username = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.id}</a>'
                await send_chats(
                  f'<b>🌟 Новая игра в BlackJack.\n\n👤 Игрок</b> {username}\n\n'
                  f'💰 Ставка: <b>{round(float(message.text), 2)} RUB</b>')
            else:
                await message.answer(text="Недостаточно средств для создания игры.")
        else:
            await message.answer(text="❔ Минимальная сумма ставки равна 10.")
    else:
        await message.answer(text="❕ Неверный ввод.")
    await state.finish()

@dp.callback_query_handler(IsPrivateCall(), game_callback.filter(game_name="blackjack", action="statistic"))
async def get_blackjack_stats(call: CallbackQuery, callback_data: dict):
    user_id = call.message.chat.id
    win_amount = get_user_blackjack_game_win_amount(user_id)
    lose_amount = get_user_blackjack_lose_amount(user_id)
    games_amount = win_amount + lose_amount
    win_sum = get_user_blackjack_game_win_sum(user_id) if get_user_blackjack_game_win_sum(user_id) != None else 0
    lose_sum = get_user_blackjack_game_lose_sum(user_id) if get_user_blackjack_game_lose_sum(user_id) != None else 0
    profit_sum = win_sum - lose_sum
    await call.message.answer(text=statistic_text(games_amount, win_amount, lose_amount,
                                                  win_sum, lose_sum, profit_sum),
                              reply_markup=understand_keyboard())


@dp.callback_query_handler(IsPrivateCall(), game_info_callback.filter(game_name="blackjack", action="info"))
async def info_blackjack_game(call: CallbackQuery, callback_data: dict):
    game_id = callback_data["game_id"]
    game = get_blackjack_game(game_id)
    if game != None:
        player_1 = get_blackjack_game(game_id)[1]
        p1 = await bot.get_chat(player_1)
        game_name = callback_data["game_name"]
        await call.message.answer(text=f"<b>BlackJack №{game_id}\n"
                                       f"Сумма: {game[-2]} ₽\n"
                                       f"1️⃣ <a href='tg://user?id={player_1}'>{p1['first_name']}</a>\n"
                                       f"2️⃣ Ожидание...</b>",
                                  reply_markup=games_info_keyboard(game_name, game_id))

    else:
        await call.message.answer(text="❗ Игра не найдена.")


@dp.callback_query_handler(IsPrivateCall(), game_info_callback.filter(game_name="blackjack", action="enjoy"))
async def enjoy_blackjack_game(call: CallbackQuery, callback_data: dict):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    game_id = callback_data["game_id"]
    game = get_blackjack_game(game_id)
    if game != None:
        if game[1] != call.message.chat.id:
            if game[-1] != "True":
                if get_user(call.message.chat.id)[1] >= game[-2]:
                    update_balance(call.message.chat.id, -game[-2])
                    update_player_blackjack(game_id, call.message.chat.id)
                    update_blackjack_game_status(game_id)
                    await bot.send_message(game[1],
                                           f"<b>♻️ Игра №{game_id} начинается, ожидайте свой ход.</b>")
                    await call.message.answer(f"ℹ<b>Количество карт</b>: {game[4]}"
                                              f"🔄 <b>Количество очков</b>: {game[3]}",
                                              reply_markup=blackjack_keyboard("blackjack", game_id))
                else:
                    await call.message.answer(text="❗ Недостаточно средств для начала игры.")
            else:
                await call.message.answer(text="❗ Данная игра уже началась.")
        else:
            await call.message.answer(text="❗ Нельзя играть с самим собой.")
    else:
        await call.message.answer(text="❗ Данная игра не найдена.")


@dp.callback_query_handler(IsPrivateCall(), game_info_callback.filter(game_name="blackjack", action="add_card"))
async def add_card_blackjack_game(call: CallbackQuery, callback_data: dict):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    game_id = callback_data["game_id"]
    game = get_blackjack_game(game_id)
    player_id = call.message.chat.id
    card = random.choice(range(2, 12))
    if game[1] == player_id:
        add_card_to_player(game_id, "player_1", card)
        game = get_blackjack_game(game_id)
        amount = game[-4]
        qnt = game[3]
    else:
        add_card_to_player(game_id, "player_2", card)
        game = get_blackjack_game(game_id)
        amount = game[-3]
        qnt = game[4]
    card_info = blackjack_values[f'{card}']['file_name'].split(':')
    image = random.choice(card_info)
    await call.message.answer_photo(photo=open(f'data/photos/{image}', 'rb'),
                                    caption=f"ℹ<b>Карт на руке</b>: {qnt}"
                                            f"🔄 <b>Всего очков</b>: {amount}",
                                    reply_markup=blackjack_keyboard("blackjack", game_id))


@dp.callback_query_handler(IsPrivateCall(), game_info_callback.filter(game_name="blackjack", action="stop"))
async def stop_blackjack_game(call: CallbackQuery, callback_data: dict):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    game_id = callback_data["game_id"]
    game = get_blackjack_game(game_id)
    player_id = call.message.chat.id
    if game[2] == player_id:
        game = get_blackjack_game(game_id)
        amount = game[-4]
        qnt = game[3]
        await bot.send_message(game[1], f"ℹКарт на руке: {qnt}"
                                        f"🔄 Всего очков: {amount}",
                               reply_markup=blackjack_keyboard("blackjack", game_id))
    else:
        game = get_blackjack_game(game_id)
        p1_result, p2_result = game[-4], game[-3]
        win_amount = ((game[-2] * 2) - (game[-2] * 2) / 100 * float(config('game_percent')))
        bank = f"💰 Выигрыш: {win_amount}₽"
        bank_amount = game[-2] * 2
        p1 = await bot.get_chat(game[1])
        p2 = await bot.get_chat(game[2])
        p1_username = p1["username"]
        p2_username = p2["username"]
        if p1_result > p2_result and p1_result < 22:
            update_balance(game[1], win_amount)
            winner = f"🏆 <b>Победитель</b>: <a href='t.me//{p1_username}'>{p1['first_name']}</a>"
            winner_id = game[1]
            loser_id = game[2]
        elif p2_result > p1_result and p2_result < 22:
            update_balance(game[2], win_amount)
            winner = f"🏆 <b>Победитель</b>: <a href='t.me//{p2_username}'>{p2['first_name']}</a>"
            winner_id = game[2]
            loser_id = game[1]
        elif p2_result == p1_result and p2_result < 22:
            update_balance(game[1], game[-2])
            update_balance(game[2], game[-2])
            bank = f"💰 <b>Выигрыш</b>: 0₽"
            winner = f"<b>❕Ничья, ставки возвращены на баланс.</b>"
            winner_id = 0
            loser_id = 0
        elif p2_result >= 22 and p1_result >= 22:
            update_balance(game[1], game[-2])
            update_balance(game[2], game[-2])
            bank = f"💰 Выигрыш: 0₽"
            winner = f"<b>❕Ничья, ставки возвращены на баланс.</b>"
            winner_id = 0
            loser_id = 0
        elif p2_result >= 22 and p1_result < 22:
            update_balance(game[1], win_amount)
            winner = f"🏆 Победитель: <a href='t.me//{p1_username}'>{p1['first_name']}</a>"
            winner_id = game[1]
            loser_id = game[2]
        elif p1_result >= 22 and p2_result < 22:
            update_balance(game[2], win_amount)
            winner = f"🏆 Победитель: <a href='t.me//{p2_username}'>{p2['first_name']}</a>"
            winner_id = game[2]
            loser_id = game[1]
        delete_blackjack_game(game_id)
        add_game_log(game_id, winner_id, loser_id, bank_amount, bank_amount - win_amount, "blackjack")

        if p1.username:
            username1 = f'@{p1.username}'
        else:
            username1 = f'<a href="tg://user?id={p1.id}">{p1.first_name}</a>'
        
        if p2.username:
            username2 = f'@{p2.username}'
        else:
            username2 = f'<a href="tg://user?id={p2.id}">{p2.first_name}</a>'
        await send_chats(
            f'🍷 Итоги игры №{game_id}\n\n'
            f'1️⃣ {username1} ({p1_result} очков)\n2️⃣'
            f' {username2} ({p2_result} очков)\n\n{bank}\n\n{winner}', True)
        await bot.send_message(game[1], f"🍷 Итоги игры!\n\n<a href='tg://user?id={game[1]}'>{p1['first_name']}</a> {game[-4]} очков"
                                        f"\n<a href='tg://user?id={game[2]}'>{p2['first_name']}</a> {game[-3]} очков\n\n{bank}\n{winner}",
                               disable_web_page_preview=False)

        await bot.send_message(game[2], f"🍷 Итоги игры №{game_id}\n\n<a href='tg://user?id={game[1]}'>{p1['first_name']}</a> {game[-4]} очков"
                                        f"\n<a href='tg://user?id={game[2]}'>{p2['first_name']}</a> {game[-3]}\n\n{bank}\n\n{winner}",
                               disable_web_page_preview=False)


@dp.callback_query_handler(IsPrivateCall(), text='game_bakkara_main')
async def bakkara_game_menu(c: CallbackQuery):
    await c.message.delete()
    if get_user(c.from_user.id) != None:
        await bot.send_photo(chat_id=c.from_user.id,
                             caption="♻️ <b>Выберите нужный пункт</b>",
                             photo=InputFile('filaro.jpg'),
                             reply_markup=games_control_keyboard("bakkara"))


@dp.callback_query_handler(IsPrivateCall(), game_callback.filter(game_name="bakkara", action="create"))
async def create_bakkara_game_1(call: CallbackQuery, callback_data: dict):
    await BakkaraGameState.bet_amount.set()
    await call.message.answer(text="Введите сумму ставки.")


@dp.message_handler(IsPrivate(), state=BakkaraGameState.bet_amount)
async def create_bakkara_game_2(message: Message, state: FSMContext):
    if message.text.isdigit():
        if int(message.text) >= 10:
            if get_user(message.chat.id)[1] >= int(message.text):
                game_id = random.randint(1111111, 99999999)
                update_balance(message.chat.id, -int(message.text))
                add_bakkara_game_to_db(game_id, message.chat.id, message.text)
                await message.answer(text="Игра успешно создана.")
                if message.from_user.username:
                  username = f'@{message.from_user.username}'
                else:
                  username = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.id}</a>'
                await send_chats(
                  f'<b>🌟 Новая игра в Baccarat.\n\n👤 Игрок: {username}</b>\n\n'
                  f'<b>💰 Ставка: {round(float(message.text), 2)} RUB</b>')
            else:
                await message.answer(text="Недостаточно средств для создания игры.")
        else:
            await message.answer(text="❔ Минимальная сумма ставки равна 10.")
    else:
        await message.answer(text="❕ Неверный ввод.")
    await state.finish()


@dp.callback_query_handler(IsPrivateCall(), game_info_callback.filter(game_name="bakkara", action="info"))
async def info_bakkara_game(call: CallbackQuery, callback_data: dict):
    game_id = callback_data["game_id"]
    game = get_bakkara_game(game_id)
    if game != None:
        player_1 = get_bakkara_game(game_id)[1]
        p1 = await bot.get_chat(player_1)
        game_name = callback_data["game_name"]
        await call.message.answer(text=f"♠ <b>Baccarat №{game_id}\n"
                                       f"Сумма: {game[-2]} ₽\n"
                                       f"1️⃣ <a href='tg://user?id={player_1}'>{p1['first_name']}</a>\n"
                                       f"2️⃣ Ожидание...</b>",
                                  reply_markup=games_info_keyboard(game_name, game_id))

    else:
        await call.message.answer(text="❗ Данная игра не найдена.")


@dp.callback_query_handler(IsPrivateCall(), game_info_callback.filter(game_name="bakkara", action="enjoy"))
async def enjoy_bakkara_game(call: CallbackQuery, callback_data: dict):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    game_id = callback_data["game_id"]
    game = get_bakkara_game(game_id)
    if game != None:
        if game[1] != call.message.chat.id:
            if game[-1] != "True":
                if get_user(call.message.chat.id)[1] >= game[-2]:
                    update_balance(call.message.chat.id, -game[-2])

                    update_player_bakkara(game_id, call.message.chat.id)

                    update_bakkara_game_status(game_id)

                    await bot.send_message(game[1],
                                           f"<b>♻️ Игра №{game_id} начинается, ожидайте свой ход.</b>")

                    card_1 = random.choice(list(bakkara_values.keys()))
                    watermark_1 = random.choice(bakkara_values[card_1]["file_name"].split(":"))
                    get_first_bakkara_screen(watermark_1,
                                             game[0],
                                             call.message.chat.id)
                    amount = (bakkara_values[card_1]["value"]) % 10
                    add_card_to_bakkara_player(game_id, "player_2", amount)
                    add_cards_to_bakkara_player(game_id, "player_2", f"{watermark_1}")
                    with open(f"{game[0]}_{call.message.chat.id}.jpg", "rb") as photo:
                        await bot.send_photo(
                            chat_id=call.message.chat.id,
                            photo=photo,
                            caption=f"ℹКоличество карт: {1}\n\n"
                                    f"🔄 Всего очков: {amount}",
                            reply_markup=first_bakkara_keyboard("bakkara", game_id))
                else:
                    await call.message.answer(text="❗ Недостаточно средств для начала игры.")
            else:
                await call.message.answer(text="❗ Данная игра уже началсь.")
        else:
            await call.message.answer(text="❗ Нельзя играть с самим собой.")
    else:
        await call.message.answer(text="❗ Данная игра не найдена.")


@dp.callback_query_handler(IsPrivateCall(), game_info_callback.filter(game_name="bakkara", action="add_card"))
async def add_card_bakkara_game(call: CallbackQuery, callback_data: dict):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    game_id = callback_data["game_id"]
    game = get_bakkara_game(game_id)
    player_id = call.message.chat.id
    card = random.choice(list(bakkara_values.keys()))
    if game[2] == player_id:
        watermark = random.choice(bakkara_values[card]["file_name"].split(":"))

        amount = (game[4] + bakkara_values[card]["value"]) % 10

        add_card_to_bakkara_player(game_id, "player_2", amount)

        add_cards_to_bakkara_player(game_id, "player_2", f"{game[-3]}:{watermark}")

        game = get_bakkara_game(game_id)

        add_bakkara_card(watermark,
                         game[0],
                         call.message.chat.id,
                         game[-3])

        if len(game[-3].split(':')) == 3:

            with open(f"{game[0]}_{call.message.chat.id}.jpg", "rb") as photo:
                await bot.send_photo(
                    chat_id=call.message.chat.id,
                    photo=photo,
                    caption=f"ℹКарт на руке: {3}\n\n"
                            f"🔄 Всего очков: {amount}")

            card_1 = random.choice(list(bakkara_values.keys()))
            watermark_1 = random.choice(bakkara_values[card_1]["file_name"].split(":"))
            amount = (bakkara_values[card_1]["value"]) % 10
            add_card_to_bakkara_player(game_id, "player_1", amount)
            add_cards_to_bakkara_player(game_id, "player_1", f"{watermark_1}")
            get_first_bakkara_screen(watermark_1,
                                     game[0],
                                     game[1])

            with open(f"{game[0]}_{game[1]}.jpg", "rb") as photo:
                await bot.send_photo(
                    chat_id=game[1],
                    photo=photo,
                    caption=f"ℹКарт на руке: {1}\n\n"
                            f"🔄 Всего очков: {amount}",
                    reply_markup=first_bakkara_keyboard("bakkara", game_id))

        else:

            with open(f"{game[0]}_{call.message.chat.id}.jpg", "rb") as photo:
                await bot.send_photo(
                    chat_id=call.message.chat.id,
                    photo=photo,
                    caption=f"ℹКарт на руке: {2}\n\n"
                            f"🔄 Всего очков: {amount}",
                    reply_markup=blackjack_keyboard("bakkara", game_id))

    elif game[2] != player_id:

        watermark = random.choice(bakkara_values[card]["file_name"].split(":"))

        amount = (game[3] + bakkara_values[card]["value"]) % 10

        add_card_to_bakkara_player(game_id, "player_1", amount)

        add_cards_to_bakkara_player(game_id, "player_1", f"{game[-4]}:{watermark}")

        game = get_bakkara_game(game_id)

        add_bakkara_card(watermark,
                         game[0],
                         call.message.chat.id,
                         game[-4])

        if len(game[-4].split(':')) == 3:

            with open(f"{game[0]}_{call.message.chat.id}.jpg", "rb") as photo:
                await bot.send_photo(
                    chat_id=call.message.chat.id,
                    photo=photo,
                    caption=f"ℹКарт на руке: {3}\n\n"
                            f"🔄 Всего очков: {amount}")
        else:

            with open(f"{game[0]}_{call.message.chat.id}.jpg", "rb") as photo:
                await bot.send_photo(
                    chat_id=call.message.chat.id,
                    photo=photo,
                    caption=f"ℹКарт на руке: {2}\n\n"
                            f"🔄 Всего очков: {amount}",
                    reply_markup=blackjack_keyboard("bakkara", game_id))

        game = get_bakkara_game(game_id)
        if len(game[-4].split(":")) == 3:
            game = get_bakkara_game(game_id)
            p1_result, p2_result = game[3], game[4]
            win_amount = ((game[-2] * 2) - (game[-2] * 2) / 100 * float(config('game_percent')))
            bank = f"💰 Выигрыш: {win_amount}₽"
            bank_amount = game[-2] * 2
            p1 = await bot.get_chat(game[1])
            p2 = await bot.get_chat(game[2])
            p1_username = p1["username"]
            p2_username = p2["username"]
            if p1_result > p2_result:
                update_balance(game[1], win_amount)
                winner = f"🏆 Победитель: <a href='t.me//{p1_username}'>{p1['first_name']}</a>"
                winner_id = game[1]
                loser_id = game[2]
            elif p2_result > p1_result:
                update_balance(game[2], win_amount)
                winner = f"🏆 Победитель: <a href='t.me//{p2_username}'>{p2['first_name']}</a>"
                winner_id = game[2]
                loser_id = game[1]
            elif p2_result == p1_result and p2_result < 22:
                update_balance(game[1], game[-2])
                update_balance(game[2], game[-2])
                bank = f"💰 Выигрыш: 0₽"
                winner = f"❕Ничья, ставки возвращены на баланс."
                winner_id = 0
                loser_id = 0
            delete_bakkara_game(game_id)
            add_game_log(game_id, winner_id, loser_id, bank_amount, bank_amount - win_amount, "bakkara")
            get_bakkara_result(game[0], game[1], game[2], game[-2], game[-4], game[-3], winner_id, game[3], game[4])

            if p1.username:
                username1 = f'@{p1.username}'
            else:
                username1 = f'<a href="tg://user?id={p1.id}">{p1.first_name}</a>'
            
            if p2.username:
                username2 = f'@{p2.username}'
            else:
                username2 = f'<a href="tg://user?id={p2.id}">{p2.first_name}</a>'
            await send_chats(
                f'<b>🍷 Итоги игры №{game_id}\n\n'
                f'1️⃣ {username1} ({p1_result} очков)\n'
                f'2️⃣ {username2} ({p2_result} очков)\n\n{winner}\n\n{bank}</b>', True)

            with open(f"result_{game[0]}.jpg", "rb") as photo:
                await bot.send_photo(
                    chat_id=game[1],
                    photo=photo)
            with open(f"result_{game[0]}.jpg", "rb") as photo:
                await bot.send_photo(
                    chat_id=game[2],
                    photo=photo)
            await bot.send_message(game[1], f"<b>🍷 Итоги игры № {game[0]}\n\n"
                                            f"{bank}\n\n{winner}</b>",
                                   disable_web_page_preview=False)

            await bot.send_message(game[2], f"<b>🍷 Итоги игры № {game[0]}\n\n"
                                            f"{bank}\n\n{winner}</b>",
                                   disable_web_page_preview=False)

            delete_game_photos(game_id, game[1], game[2])


@dp.callback_query_handler(IsPrivateCall(), game_info_callback.filter(game_name="bakkara", action="stop"))
async def stop_bakkara_game(call: CallbackQuery, callback_data: dict):
    await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
    game_id = callback_data["game_id"]
    game = get_bakkara_game(game_id)
    player_id = call.message.chat.id
    if game[2] == player_id:
        game = get_bakkara_game(game_id)
        card_1 = random.choice(list(bakkara_values.keys()))
        watermark_1 = random.choice(bakkara_values[card_1]["file_name"].split(":"))
        add_cards_to_bakkara_player(game_id, "player_1", f"{watermark_1}")
        get_first_bakkara_screen(watermark_1,
                                 game[0],
                                 game[1])
        amount = (bakkara_values[card_1]["value"]) % 10
        add_card_to_bakkara_player(game_id, "player_1", amount)
        game = get_bakkara_game(game_id)
        with open(f"{game[0]}_{game[1]}.jpg", "rb") as photo:
            await bot.send_photo(
                chat_id=game[1],
                photo=photo,
                caption=f"ℹКоличество карт: {len(game[-4].split(':'))}\n\n"
                        f"🔄 Количество очков: {amount}",
                reply_markup=first_bakkara_keyboard("bakkara", game_id))
    else:
        game = get_bakkara_game(game_id)
        p1_result, p2_result = game[3], game[4]
        win_amount = ((game[-2] * 2) - (game[-2] * 2) / 100 * float(config('game_percent')))
        bank = f"💰 Выигрыш: {win_amount}₽"
        bank_amount = game[-2] * 2
        p1 = await bot.get_chat(game[1])
        p2 = await bot.get_chat(game[2])
        p1_username = p1["username"]
        p2_username = p2["username"]
        if p1_result > p2_result:
            update_balance(game[1], win_amount)
            winner = f"🏆 Победитель: <a href='t.me//{p1_username}'>{p1['first_name']}</a>"
            winner_id = game[1]
            loser_id = game[2]
        elif p2_result > p1_result:
            update_balance(game[2], win_amount)
            winner = f"🏆 Победитель: <a href='t.me//{p2_username}'>{p2['first_name']}</a>"
            winner_id = game[2]
            loser_id = game[1]
        elif p2_result == p1_result:
            update_balance(game[1], game[-2])
            update_balance(game[2], game[-2])
            bank = f"💰 Выигрыш: 0₽"
            winner = f"❕Ничья, ставки возвращены на баланс."
            winner_id = 0
            loser_id = 0
        delete_bakkara_game(game_id)
        add_game_log(game_id, winner_id, loser_id, bank_amount, bank_amount - win_amount, "bakkara")
        get_bakkara_result(game[0], game[1], game[2], game[-2], game[-4], game[-3], winner_id, game[3], game[4])
        if p1.username:
            username1 = f'@{p1.username}'
        else:
            username1 = f'<a href="tg://user?id={p1.id}">{p1.first_name}</a>'
        
        if p2.username:
            username2 = f'@{p2.username}'
        else:
            username2 = f'<a href="tg://user?id={p2.id}">{p2.first_name}</a>'
        await send_chats(
            f'<b>🍷 Итоги игры №{game_id}\n'
            f'1️⃣ {username1} ({p1_result} очков)\n'
            f'2️⃣ {username2} ({p2_result} очков)\n\n{winner}\n\n{bank}</b>', True)
        with open(f"result_{game[0]}.jpg", "rb") as photo:
            await bot.send_photo(
                chat_id=game[1],
                photo=photo)
        with open(f"result_{game[0]}.jpg", "rb") as photo:
            await bot.send_photo(
                chat_id=game[2],
                photo=photo)
        await bot.send_message(game[1], f"Игра #{game[0]} завершена\n\n"
                                        f"{winner}\n\n{bank}",
                               disable_web_page_preview=False)

        await bot.send_message(game[2], f"Игра #{game[0]} завершена\n\n"
                                        f"{winner}\n\n{bank}",
                               disable_web_page_preview=False)

        delete_game_photos(game_id, game[1], game[2])


@dp.callback_query_handler(IsPrivateCall(), game_callback.filter(game_name="bakkara", action="statistic"))
async def get_blackjack_stats(call: CallbackQuery, callback_data: dict):
    user_id = call.message.chat.id
    win_amount = get_user_bakkara_game_win_amount(user_id)
    lose_amount = get_user_bakkara_lose_amount(user_id)
    games_amount = win_amount + lose_amount
    win_sum = get_user_bakkara_game_win_sum(user_id) if get_user_bakkara_game_win_sum(user_id) != None else 0
    lose_sum = get_user_bakkara_game_lose_sum(user_id) if get_user_bakkara_game_lose_sum(user_id) != None else 0
    profit_sum = win_sum - lose_sum
    await call.message.answer(text=statistic_text(games_amount, win_amount, lose_amount,
                                                  win_sum, lose_sum, profit_sum),
                              reply_markup=understand_keyboard())


@dp.callback_query_handler(IsPrivateCall(), text="game_other_main")
async def other_game_menu(c: CallbackQuery):
    await c.message.delete()
    if get_user(c.from_user.id) != None:
        await bot.send_photo(chat_id=c.from_user.id,
                             caption="🖲 Создайте свою либо присоединитесь к существующим играм",
                             photo=InputFile('filaro.jpg'),
                             reply_markup=games_control_keyboard("other"))

@dp.callback_query_handler(IsPrivateCall(), text="game_othee_main")
async def other_game_menu(c: CallbackQuery):
    await c.message.delete()
    if get_user(c.from_user.id) != None:
        await bot.send_photo(chat_id=c.from_user.id,                           
                             caption="Выберите нужную вам игру!",
                             photo=InputFile('filaro.jpg'),
                             reply_markup=othee_keyboard())

@dp.callback_query_handler(IsPrivateCall(), game_callback.filter(game_name="other", action="create"))
async def create_other_game_1(call: CallbackQuery, callback_data: dict):
    await call.message.answer(text="Выберите тип игры:",
                              reply_markup=other_games_types())


@dp.callback_query_handler(IsPrivateCall(), other_game_callback.filter(game_name="other", action="type_choice"))
async def create_other_game_2(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await OtherGameState.bet_amount.set()
    async with state.proxy() as data:
        data["game_name"] = callback_data["game_type"]
    await call.message.answer(text="Введите сумму ставки.")


@dp.callback_query_handler(IsPrivateCall(), game_callback.filter(game_name="other", action="statistic"))
async def get_other_stats(call: CallbackQuery, callback_data: dict):
    user_id = call.message.chat.id
    win_amount = get_user_other_game_win_amount(user_id)
    lose_amount = get_user_other_lose_amount(user_id)
    games_amount = win_amount + lose_amount
    win_sum = get_user_other_game_win_sum(user_id) if get_user_other_game_win_sum(user_id) != None else 0
    lose_sum = get_user_other_game_lose_sum(user_id) if get_user_other_game_lose_sum(user_id) != None else 0
    profit_sum = win_sum - lose_sum
    await call.message.answer(text=statistic_text(games_amount, win_amount, lose_amount,
                                                  win_sum, lose_sum, profit_sum),
                              reply_markup=understand_keyboard())


@dp.message_handler(IsPrivate(), state=OtherGameState.bet_amount)
async def create_other_game_3(message: Message, state: FSMContext):
    if message.text.isdigit():
        if int(message.text) >= 10:
            if get_user(message.chat.id)[1] >= int(message.text):

                async with state.proxy() as data:
                    game_name = data["game_name"]
                game_id = random.randint(1111111, 9999999)
                update_balance(message.chat.id, -int(message.text))
                add_other_game_to_db(game_id, message.chat.id, message.text, game_name)
                game_text = '{}'.format({
                          game_name:f'🎲 Новая игра в (OtherGame)',
                          "dice": '🎲 Новая игра кости',
                          "darts": '🎯 Новая игра дартс',
                          "basketball": '🏀 Новая игра баскетбол',
                          "bowling": '🎳 Новая игра боулинг'
                          }[game_name])

                if message.from_user.username:
                  username = f'@{message.from_user.username}'
                else:
                  username = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.id}</a>'
                await send_chats(
                  f'{game_text}\nИгрок {username}\n'
                  f'Ставка: <b>{round(float(message.text), 2)} RUB</b>')
                await message.answer(text="Игра успешно создана.")
            else:
                await message.answer(text="❕ Недостаточно средств для создания игры.")
        else:
            await message.answer(text="❔ Минимальная сумма ставки равна 10.")
    else:
        await message.answer(text="Неверный ввод.")
    await state.finish()


@dp.callback_query_handler(IsPrivateCall(), game_info_callback.filter(game_name="other", action="info"))
async def info_other_game(call: CallbackQuery, callback_data: dict):
    game_id = callback_data["game_id"]
    game = get_other_game(game_id)
    if game != None:
        player_1 = get_other_game(game_id)[1]
        p1 = await bot.get_chat(player_1)
        game_name = callback_data["game_name"]
        await call.message.answer(text=f"{other_games_info[get_other_game(game_id)[-1]]['text']} #{game_id}\n"
                                       f"Сумма: {game[-2]} ₽\n"
                                       f"👤1 Игрок: <a href='tg://user?id={player_1}'>{p1['first_name']}</a>\n"
                                       f"👤2 Игрок: Ожидание...",
                                  reply_markup=games_info_keyboard(game_name, game_id))

    else:
        await call.message.answer(text="❗ Данная игра не найдена.")


@dp.callback_query_handler(IsPrivateCall(), game_info_callback.filter(game_name="other", action="enjoy"))
async def enjoy_other_game(call: CallbackQuery, callback_data: dict):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    game_id = callback_data["game_id"]
    game = get_other_game(game_id)
    if game != None:
        if game[1] != call.message.chat.id:
            if get_user(call.message.chat.id)[1] >= game[2]:
                emoji = other_games_info[game[-1]]['emoji']
                other_game = PlayOtherGames(game_id, game[1], call.message.chat.id, game[2], emoji, game[-1])
                await other_game.main_start(bot)
            else:
                await call.message.answer(text="❗ Недостаточно средств для начала игры.")
        else:
            await call.message.answer(text="❗ Нельзя играть с самим собой.")
    else:
        await call.message.answer(text="❗ Данная игра не найдена.")


@dp.callback_query_handler(IsPrivateCall(), text="close")
async def close_message(call: CallbackQuery):
    await bot.delete_message(call.message.chat.id, call.message.message_id)