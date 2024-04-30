from tonrocketapisdk import *

# api = RocketApi('dc447b1aa19ffb11d99a422dd')
api = RocketApi('8c1e9dff9f7f266076f6952a6')

# invoice = api.createInvoice({
#   "amount": 0.01,
#   "description": "best thing in the world, 1 item",
#   "hiddenMessage": "thank you",
#   "callbackUrl": "https://t.me/ton_rocket",
#   "payload": "Ну типо тут что-то",
#   "expiredIn": 600
# })

invoice = api.getInvoice({
    'id': 220490
})

print(invoice)