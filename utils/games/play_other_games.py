import asyncio
import random

from config import config, other_games_info
from data.functions.db import delete_other_game, update_balance, add_game_log, get_user
from loader import bot
from data.functions.functions import send_chats

dice_game_result_txt = """
{} №{}

💸 Выигрыш: {} RUB

1⃣ <a href='tg://user?id={}'>{}</a>\n2⃣ <a href='tg://user?id={}'>{}</a>

👨🏻‍💻Ваш результат: {}
👺Результат соперника: {}

{}
"""


class PlayOtherGames():
    def __init__(self, game_id, player_1, player_2, bet, emoji, game_name):
        self.game_id = game_id
        self.player_1 = player_1
        self.player_2 = player_2
        self.bet = int(bet)
        self.emoji = emoji
        self.game_name = game_name
        self.bank = self.bet*2
        self.win_money = 0
        self.winner = 0
        self.loser = 0

    async def main_start(self, bot):
        delete_other_game(self.game_id)
        update_balance(self.player_2, -self.bet)

        value_dice1, value_dice2 = await self.start_roll(bot)

        info = await self.start_game_dice(value_dice1, value_dice2)

        from_chat_id = lambda i: 1 if i == 0 else 0 if i == 1 else 100

        for i in range(2):
            await bot.send_message(chat_id=info[0][i],
                                   text='❕ Противник бросает эмоджи...')
            await asyncio.sleep(2, 5)
            await bot.forward_message(chat_id=info[0][i],
                                      from_chat_id=info[0][from_chat_id(i)],
                                      message_id=info[2][i])
            await asyncio.sleep(2)
            await bot.send_message(chat_id=info[0][i], text=info[1][i])

        add_game_log(self.game_id, self.winner, self.loser, self.bank, self.bank - self.win_money, self.game_name)

    async def start_game_dice(self, value_dice1, value_dice2):
        self.win_money = ((self.bet * 2) - (self.bet * 2) / 100 * float(config('game_percent')))

        self.player_1_firstname = await bot.get_chat(self.player_1)
        self.player_2_firstname = await bot.get_chat(self.player_2)
        p1, p2 = self.player_1_firstname, self.player_2_firstname

        self.player_1_firstname = self.player_1_firstname.first_name
        self.player_2_firstname = self.player_2_firstname.first_name

        if p1.username:
            username1 = f'@{p1.username}'
        else:
            username1 = \
              f'<a href="tg://user?id={p1.id}">' \
              f'{p1.first_name}</a>'
        
        if p2.username:
            username2 = f'@{p2.username}'
        else:
            username2 = \
              f'<a href="tg://user?id={p2.id}">' \
              f'{p2.first_name}</a>'

        if value_dice1[0] > value_dice2[0]:
            update_balance(self.player_1, self.win_money)
            status1 = '🥇 Вы выиграли'
            status2 = '🛑🛑🛑 Вы проиграли!'
            winner = username1
            self.winner = self.player_1
            self.loser = self.player_2

        elif value_dice1[0] < value_dice2[0]:
            update_balance(self.player_2, self.win_money)
            status1 = '🛑🛑🛑 Вы проиграли!'
            status2 = '🥇 Вы выиграли'
            winner = username2
            self.winner = self.player_2
            self.loser = self.player_1
        

        msg1 = dice_game_result_txt.format(
            other_games_info[self.game_name]["text"],
            self.game_id,
            self.win_money,
            self.player_1,
            self.player_1_firstname,
            self.player_2,
            self.player_2_firstname,
            value_dice1[0],
            value_dice2[0],
            status1
        )

        
        await send_chats(
            f'🥂 <b>Итоги игры №{self.game_id} через бота!\n\n'
            f'1⃣ {username1} ({value_dice1[0]} очков)\n'
            f'2⃣ {username2} ({value_dice2[0]} очков)\n\n 🏆 Победитель:'
            f' {winner}\n\n 💸 Выигрыш: {round(self.win_money, 2)}₽</b>', True)

        msg2 = dice_game_result_txt.format(
            other_games_info[self.game_name]["text"],
            self.game_id,
            self.win_money,
            self.player_1,
            self.player_1_firstname,
            self.player_2,
            self.player_2_firstname,
            value_dice2[0],
            value_dice1[0],
            status2
        )

        return [self.player_1, self.player_2], [msg1, msg2], [value_dice2[1], value_dice1[1]]

    async def start_roll(self, bot):
        await bot.send_message(chat_id=self.player_2, text='❕ Бросаем эмоджи...')
        await asyncio.sleep(2, 5)

        value1 = await self.spin_up(bot, self.player_1)
        value2 = await self.spin_up(bot, self.player_2)

        if value1[0] == value2[0]:
            await bot.send_message(chat_id=self.player_1, text='❕ Противник бросает эмоджи...')
            await bot.forward_message(chat_id=self.player_1, from_chat_id=self.player_2, message_id=value2[1])
            await bot.send_message(chat_id=self.player_1, text='🔹🔹 Ничья!!!')

            await bot.send_message(chat_id=self.player_2, text='❕ Противник бросает эмоджи...')
            await bot.forward_message(chat_id=self.player_2, from_chat_id=self.player_1, message_id=value1[1])
            await bot.send_message(chat_id=self.player_2, text='🔹🔹 Ничья!!!')

            return await self.start_roll(bot)
        else:
            return value1, value2

    async def roll_dice(self, bot, user_id):
        value = await bot.send_dice(user_id, emoji=self.emoji)
        return int(value.dice.value), value.message_id

    async def spin_up(self, bot, user_id):
        if get_user(user_id)[2] == 'True':
            value = await self.roll_dice(bot, user_id)
            if self.game_name != "basketball":
                while int(value[0]) < 6:
                    value = await self.roll_dice(bot, user_id)
            else:
                while int(value[0]) < 5:
                    value = await self.roll_dice(bot, user_id)

            return int(value[0]), value[1]
        else:
            value = await self.roll_dice(bot, user_id)
            return int(value[0]), value[1]
