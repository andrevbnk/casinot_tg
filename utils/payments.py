import re
import time
import asyncio
import aiohttp, sqlite3

from config import config
from loader import bot
from data.functions.db import get_user, update_balance



async def send_safe(user_id, message):

    try:
      await bot.send_message(
        chat_id=user_id, text=message,
        parse_mode='html', disable_web_page_preview=True)
    except:
      pass


async def send_admins(message):

    for x in config("admin_id").split(":"):
      await send_safe(x, message)
      
      
      
class PayeerAPI(object):

    def __init__(self):
        self.bot = bot
        self.account = config('payeer_account')
        self.api_id = config('payeer_apiId')
        self.api_pass = config('payeer_apiPass')


    async def GetHistory(self, rows, tx_type):
      try:
        data = {'account': self.account, 'apiId': self.api_id,
                'apiPass': self.api_pass, 'action': 'history',
                'count': rows, 'type': tx_type }
        
        async with aiohttp.ClientSession() as session:
          async with session.post('https://payeer.com/ajax/api/api.php', data=data) as resp:
            b = await resp.json()
        if b['errors']:
          print(f'Ошибка [Payeer GetHistory] {b["errors"][0]}')
          return {'status': False, 'data': b['errors'][0]}
        else:
          return {'status': True, 'data': b}
      except Exception as e:
        print(f'Ошибка [Payeer GetHistory] {e}')
        return {'status': False, 'data': e}



    async def GetRate(self):
      try:
        data = {'account': self.account,
                'apiId': self.api_id,
                'apiPass': self.api_pass,
                'action': 'getExchangeRate',
                'output':'Y' }
        url = 'https://payeer.com/ajax/api/api.php'
        async with aiohttp.ClientSession() as session:
          async with session.post(url, data=data) as resp:
            b = await resp.json()
        if b.get("errors"):
          return {'status': False, 'data': b['errors'][0]}
        else:
          return {'status': True,
                  'usd': float(b.get("rate", {}).get("USD/RUB")),
                  'eur': float(b.get("rate", {}).get("EUR/RUB"))}
      except Exception as e:
        print(f'Error [Payeer GetRate] {e}')
        return {'status': False, 'data': e}



    async def CheckTtrans(self):
        print('Payeer History checked start')
        lastTxnID, start_check = [], False
        while self.account != '0':

          try:

            history = await self.GetHistory(50, 'incoming')

            if history.get("status"):

              for k, v in (history.get("data").get("history", {})).items():

                if re.search(r'^g\d*$', v.get("comment", "").lower().strip()) and \
                  v.get("status") == 'success' and start_check and k not in lastTxnID:

                  amount_text = ''

                  if v['creditedCurrency'] == "RUB":
                    amount = float(v['creditedAmount'])
                  elif v['creditedCurrency'] == "USD":
                    rate = await self.GetRate()
                    if not rate.get("status"):
                      raise NameError(f'Error [Check pay GetRate] {rate.get("data")}')
                    amount = float(v['creditedAmount']) * rate.get("usd")
                    amount_text = f' (<b>{round(amount, 2)}₽ ({v.get("creditedAmount")}$)</b>)'
                  elif v['creditedCurrency'] == "EUR":
                    rate = await self.GetRate()
                    if not rate.get("status"):
                      raise NameError(f'Error [Check pay GetRate] {rate.get("data")}')
                    amount = float(v['creditedAmount']) * rate.get("eur")
                    amount_text = f' (<b>{round(amount, 2)}₽ ({v.get("creditedAmount")}€)</b>)'
                  else:
                    return False

                  user_id = int(re.findall(r'\d*$', v.get("comment", "").strip())[0])
                  if get_user(user_id) != None:
                    update_balance(user_id, amount)
                    with sqlite3.connect('data/database.db') as conn:
                      conn.execute('INSERT INTO list_of_deposits (user_id, summa, time) VALUES (?,?,?)', (user_id, amount, time.time(), ))
                      conn.commit()
                    await send_safe(user_id,
                      f'<b>✅ Пополнение прошло успешно</b>, <code>на ваш баланс зачислено: {round(amount, 2)} RUB{amount_text} через PAYEER</code>\n\n<b>❤️ Приятной игры</b>')
                    await send_admins(
                      f'Пользователь <a href="tg://user?id={user_id}">{user_id}</a>'
                      f' пополнен на {round(amount, 2)} RUB{amount_text} через PAYEER')

                if k and k not in lastTxnID and v.get("status") == 'success':
                  lastTxnID.append(k)

              start_check = True
          except Exception as e:
            print(f'PAYEER check:\n{e}')
          await asyncio.sleep(120)
          
           

class QiwiAPI(object):

    def __init__(self):
        self.wallet = config('qiwi_address')
        self.token = config('qiwi_token')


    async def GetHistory(self, rows_num, operation_type):

      try:
        async with aiohttp.ClientSession() as session:

          session.headers['authorization'] = f'Bearer {self.token}'
          parameters = {'rows': rows_num,
                        'operation': operation_type,
                        'sources': ['QW_RUB']}
          url = f'https://edge.qiwi.com/payment-history/v2/persons/+{self.wallet}/payments'

          async with session.get(url, params=parameters) as resp:
            return {'status': True, 'data': await resp.json()}

      except Exception as e:
        print(f'Error [utils.QiwiAPI.GetHistory] {e}')
        return {'status': False, 'data': e}
    


    async def CheckTtrans(self):

        lastTxnID, start_check = [], False
        print('QIWI History checked start')
        while self.wallet != '0':

          try:

            history = await self.GetHistory(50, 'IN')
            if history.get('status'):
              history = history.get('data')
            else:
              raise NameError(history.get('data'))

            for x in history.get("data") or []:

              if start_check and x.get("txnId") not in lastTxnID \
                and x.get("comment") and x.get("status") == 'SUCCESS':

                if re.search(r'^g\d*$', x.get("comment", "").lower().strip()):

                  user_id = int(re.findall(r'\d*$', x.get("comment", "").strip())[0])
                  amount = x['sum']['amount']
                  user = get_user(user_id)
                  if user:

                    update_balance(user_id, amount)
                    with sqlite3.connect('data/database.db') as conn:
                      conn.execute('INSERT INTO list_of_deposits (user_id, summa, time) VALUES (?,?,?)', (user_id, amount, time.time(), ))
                      conn.commit()
                    await send_safe(user_id,
                      f'<b>✅ Пополнение прошло успешно</b>,<code> на ваш баланс зачислено:</code> {round(amount, 2)} RUB через QIWI\n\n<b>❤️ Приятной игры</b>')
                    await send_admins(
                      f'Пользователь <a href="tg://user?id={user_id}">{user_id}</a>'
                      f' пополнен на {round(amount, 2)} RUB через QIWI')
                    if user[5]:
                      ref_pay = amount * (float(config('ref_percent')) / 100)
                      update_balance(user[5], ref_pay)
                      await send_safe(user[5],
                      f'Выш баланс пополнен на {round(ref_pay, 2)} RUB за пополнение вашего реферала')

              if x.get("txnId") not in lastTxnID and x.get("status") == 'SUCCESS':
                lastTxnID.append(x.get("txnId"))

            start_check = True
          except Exception as e:
            print(f'QIWI check:\n{e}')
          await asyncio.sleep(30)