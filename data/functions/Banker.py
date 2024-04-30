from time import sleep
from telethon import TelegramClient
import asyncio
import re

from telethon import TelegramClient, events
from telethon.tl.types import PeerUser, MessageMediaDocument, PeerChannel, MessageMediaPhoto

from data.functions.db import update_balance

api_id = '24910534'
api_hash = '15190f8c790a3d1a690b5e1a4c2ada63'

client = TelegramClient('hi', api_id, api_hash, device_model="Iphone", system_version="6.12.0",
						app_version="10 P (28)")

# client.start()


async def checked_btc(user_id, cheque):
	await client.send_message('me', 'start')
	cheque = cheque.replace('http://t.me/CryptoBot?start=', '')
	cheque = cheque.replace('t.me/CryptoBot?start=', '')
	await client.send_message('CryptoBot', '/start ' + cheque)
	await asyncio.sleep(1)

	transaction = await client.get_messages('CryptoBot', limit=1)
	msg_transaction = transaction[0].message
	print(msg_transaction)
	if 'Получение' in msg_transaction:
		msg_transaction = msg_transaction.replace('(', '').replace(')', '').split(' ')
		print(msg_transaction)
		print("efwefwefewfwfwefewfew")
		print(msg_transaction[5])
		print(msg_transaction[4])
		if msg_transaction[5] != 'RUB…':
			print('Валюта была не в рублях!')

			return 'Валюта была не в рублях'
		else:
			amount = round(float(msg_transaction[4]))
			update_balance(user_id, amount)
			return f'<b>✅ Пополнение прошло успешно</b>, <code>на ваш баланс зачислено: {amount} RUB</code>.\n\n<b>❤️ Приятной игры</b>'

		await client.disconnect()

	elif 'Мультивалютный криптокошелек' in msg_transaction:
		return 'Ошибка при обналичивании чека'

		await client.disconnect()
	else:
		return msg_transaction

		await client.disconnect()