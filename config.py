import configparser
import os
import time 

path = 'data/config.cfg'
games_photo  = "https://i.yapx.ru/WNN3g.jpg"
cabinet_photo = "https://i.yapx.ru/WNN3g.jpg"
slots_photo = "https://i.yapx.ru/WNN3g.jpg"
other_games_photo ="https://i.yapx.ru/WNN3g.jpg"
blackjack_photo = "https://i.yapx.ru/WNN3g.jpg"
bakkara_photo = "https://i.yapx.ru/WNN3g.jpg"
jackpot_photo = "https://i.yapx.ru/WNN3g.jpg"

link_regex = "^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$"

other_games_info = {"dice": {"emoji": "🎲", "text": "🎲Кубик"},
                    "darts": {"emoji": "🎯", "text": "🎯Дартс"},
                    "basketball": {"emoji": "🏀", "text": "🏀Баскетбол"},
                    "bowling": {"emoji": "🎳", "text": "🎳Боулинг"}}

slots_values = {
    "2_same" : [32, 6, 62, 4, 2, 49, 59, 48, 63, 44, 38,
                21, 32, 16, 3, 23, 44, 54, 27, 33, 42, 11,
                41, 13, 24, 17 ],
    "3_same" : [43, 11, 22]
}

bakkara_values = {
    "1" : {"value" : 1, "name": 1, "file_name" : "1h.png:1d.png:1c.png:1s.png"},
    "2" : {"value" : 2, "name": 2, "file_name" : "2h.png:2d.png:2c.png:2s.png"},
    "3" : {"value" : 3, "name": 3, "file_name" : "3h.png:3d.png:3c.png:3s.png"},
    "4" : {"value" : 4, "name": 4, "file_name" : "4h.png:4d.png:4c.png:4s.png"},
    "5" : {"value" : 5, "name": 5, "file_name" : "5h.png:5d.png:5c.png:5s.png"},
    "6" : {"value" : 6, "name": 6, "file_name" : "6h.png:6d.png:6c.png:6s.png"},
    "7" : {"value" : 7, "name": 7, "file_name" : "7h.png:7d.png:7c.png:7s.png"},
    "8" : {"value" : 8, "name": 8, "file_name" : "8h.png:8d.png:8c.png:8s.png"},
    "9" : {"value" : 9, "name": 9, "file_name" : "9h.png:9d.png:9c.png:9s.png"},
    "10" : {"value" : 10, "name": 10, "file_name" : "10h.png:10d.png:10c.png:10s.png"},
    "jack" : {"value" : 10, "name": 1, "file_name" : "11h.png:11d.png:11c.png:11s.png"},
    "lady" : {"value" : 10, "name": 1, "file_name" : "12h.png:12d.png:12c.png:12s.png"},
    "king" : {"value" : 10, "name": 1, "file_name" : "13h.png:13d.png:13c.png:13s.png"},
}


blackjack_values = {
    "2" : {"value" : 2, "name": 2, "file_name" : "2h.png:2d.png:2c.png:2s.png"},
    "3" : {"value" : 3, "name": 3, "file_name" : "3h.png:3d.png:3c.png:3s.png"},
    "4" : {"value" : 4, "name": 4, "file_name" : "4h.png:4d.png:4c.png:4s.png"},
    "5" : {"value" : 5, "name": 5, "file_name" : "5h.png:5d.png:5c.png:5s.png"},
    "6" : {"value" : 6, "name": 6, "file_name" : "6h.png:6d.png:6c.png:6s.png"},
    "7" : {"value" : 7, "name": 7, "file_name" : "7h.png:7d.png:7c.png:7s.png"},
    "8" : {"value" : 8, "name": 8, "file_name" : "8h.png:8d.png:8c.png:8s.png:11h.png:11d.png:11c.png:11s.png"},
    "9" : {"value" : 9, "name": 9, "file_name" : "9h.png:9d.png:9c.png:9s.png:12h.png:12d.png:12c.png:12s.png"},
    "10" : {"value" : 10, "name": 10, "file_name" : "10h.png:10d.png:10c.png:10s.png:13h.png:13d.png:13c.png:13s.png"},
    "11": {"value": 11, "name": 11, "file_name": "1h.png:1d.png:1c.png:1s.png"},
}

mines_map = {'mines:A1': '🎁','mines:A2': '🎁','mines:A3': '🎁','mines:A4': '🎁','mines:A5': '🎁', 
            'mines:B1': '🎁','mines:B2': '🎁','mines:B3': '🎁','mines:B4': '🎁','mines:B5': '🎁', 
            'mines:C1': '🎁','mines:C2': '🎁','mines:C3': '🎁','mines:C4': '🎁','mines:C5': '🎁', 
            'mines:D1': '🎁','mines:D2': '🎁','mines:D3': '🎁','mines:D4': '🎁','mines:D5': '🎁', 
            'mines:E1': '🎁','mines:E2': '🎁','mines:E3': '🎁','mines:E4': '🎁','mines:E5': '🎁'}

apple_map = {'mines:A1': '🎁','mines:A2': '🎁','mines:A3': '🎁','mines:A4': '🎁','mines:A5': '🎁', 
            'mines:B1': '🎁','mines:B2': '🎁','mines:B3': '🎁','mines:B4': '🎁','mines:B5': '🎁', 
            'mines:C1': '🎁','mines:C2': '🎁','mines:C3': '🎁','mines:C4': '🎁','mines:C5': '🎁', 
            'mines:D1': '🎁','mines:D2': '🎁','mines:D3': '🎁','mines:D4': '🎁','mines:D5': '🎁', 
            'mines:E1': '🎁','mines:E2': '🎁','mines:E3': '🎁','mines:E4': '🎁','mines:E5': '🎁'}
##Кофицент
mine_cof = { 
  3: 0.15,
  4: 0.2,
  5: 0.26,
  6: 0.33,
  7: 0.41,
  8: 0.5,
  9: 0.63,
  10: 0.8,
  11: 1,
  12: 1.18,
  13: 1.33,
  14: 1.5,
  15: 1.65,
  16: 1.8,
  17: 2.15,
  18: 2.5,
  19: 2.8,
  20: 3.5,
  21: 4.3,
  22: 5.5,
  23: 8,
  24: 16
      }

apple_cof = { 
  3: 0.15,
  4: 0.2,
  5: 0.26,
  6: 0.33,
  7: 0.41,
  8: 0.5,
  9: 0.63,
  10: 0.8,
  11: 1,
  12: 1.18,
  13: 1.33,
  14: 1.5,
  15: 1.65,
  16: 1.8,
  17: 2.15,
  18: 2.5,
  19: 2.8,
  20: 3.5,
  21: 4.3,
  22: 5.5,
  23: 8,
  24: 16
      }

def create_config():
    config = configparser.ConfigParser()
    config.add_section("Settings")
    config.set("Settings", "bot_token", "6377493023:AAHtM2D8jccMcs")
    config.set("Settings", "admin_id", "5085462106")
    config.set("Settings", "p2p_qiwi_key", "")
    config.set("Settings", "admin_chat", "-1002058259354")
    config.set("Settings", "game_percent", "10")
    config.set("Settings", "ref_percent", "10")
    config.set("Settings", "notification_chat", "-1002058259354")
    config.set("Settings", "support_username", "Andrey19976")
    config.set("Settings", "qiwi_address", "79610165162")
    config.set("Settings", "qiwi_token", "619rvF0IPYgA")


    with open(path, "w") as config_file:
        config.write(config_file)


def check_config_file():
    if not os.path.exists(path):
        create_config()

        print('Config created')
        time.sleep(3)
        exit(0)


def config(what):
    config = configparser.ConfigParser()
    config.read(path)

    value = config.get("Settings", what)

    return value


def edit_config(setting, value):
    config = configparser.ConfigParser()
    config.read(path)

    config.set("Settings", setting, value)

    with open(path, "w") as config_file:
        config.write(config_file)


check_config_file()