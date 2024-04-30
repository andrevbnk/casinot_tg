import sqlite3
import datetime
import time

from config import mines_map

field_list = {}

db = sqlite3.connect('data/database.db')
cursor = db.cursor()
cursor.execute(f'CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, tg_id VARCHAR(120), value FLOAT, reg_date TIMESTAMP, is_done INTEGER DEFAULT 0)')
db.commit()

def get_now_date():
    date = datetime.datetime.today().strftime("%d.%m.%Y")
    return date


# STAT
def add_stat(user_id, cost, pre_bal):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    user = [user_id, 0, "False", "False", get_now_date()]
    cursor.execute("INSERT INTO stat (user_id, cost, pre_bal) VALUES(?,?,?)",
                   (user_id, cost, pre_bal,))
    db.commit()


def select_buy_stat(user_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM stat WHERE user_id =?", (user_id,))
    row = cursor.fetchone()
    return row


def delete_stat(user_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    user = [user_id, 0, "False", "False", get_now_date()]
    cursor.execute("DELETE FROM stat WHERE user_id =?", (user_id,))
    db.commit()


def add_user_to_db(user_id, referer):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    user = [user_id, 0, "False", "False", get_now_date(), referer or 0]
    cursor.execute(f'''INSERT INTO users(user_id, balance, twist, banned, registration_date, referer) VALUES(?,?,?,?,?,?)''', user)
    db.commit()


def get_user(user_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f"""SELECT * FROM users WHERE user_id = '{user_id}'""")
    row = cursor.fetchone()
    return row


def get_all_users():
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f"""SELECT * FROM users""")
    row = cursor.fetchall()
    return row


def get_all_games():
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT * FROM games_logs''')
    row = cursor.fetchall()
    return row


def get_all_slots_games():
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT * FROM slots_logs''')
    row = cursor.fetchall()
    return row

def get_orel_games():
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT * FROM games_logs''')
    row = cursor.fetchall()
    return row

def get_all_bets_sum():
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT SUM(bank) FROM games_logs''')
    row = cursor.fetchone()[0]
    return row


def get_all_slots_bets_sum():
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT SUM(bet) FROM slots_logs''')
    row = cursor.fetchone()[0]
    return row


def get_all_today_users():
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f"""SELECT * FROM users WHERE registration_date = '{get_now_date()}' """)
    row = cursor.fetchone()
    return row


def get_all_today_games():
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT * FROM games_logs WHERE date = '{get_now_date()}' ''')
    row = cursor.fetchall()
    return row


def get_all_today_slots_games():
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT * FROM slots_logs WHERE date = '{get_now_date()}' ''')
    row = cursor.fetchall()
    return row


def get_all_today_bets_sum():
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT SUM(bank) FROM games_logs WHERE date = '{get_now_date()}' ''')
    row = cursor.fetchone()[0]
    return row


def get_all_today_slots_bets_sum():
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT SUM(bet) FROM slots_logs WHERE date = '{get_now_date()}' ''')
    row = cursor.fetchone()[0]
    return row


def change_spinup_status(user_id, status):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f"""UPDATE users SET twist = '{status}' WHERE user_id = '{user_id}' """)
    db.commit()


def update_balance(user_id, amount, add=True):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    if add:
        cursor.execute(f"UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id,))
    else:
        cursor.execute(f"""UPDATE users SET balance = ? WHERE user_id = ? """, (amount, user_id,))
    db.commit()


def add_other_game_to_db(game_id, player_1, bet, game_name):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    game = [game_id, player_1, bet, game_name]
    cursor.execute(f'''INSERT INTO other_games(game_id, player_1, bet, game_name) VALUES(?,?,?,?)''', game)
    db.commit()


def get_other_games():
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f"""SELECT * FROM other_games""")
    row = cursor.fetchall()
    return row


def get_other_game(game_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f"""SELECT * FROM other_games WHERE game_id = '{game_id}'""")
    row = cursor.fetchone()
    return row


def delete_other_game(game_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f"""DELETE FROM other_games WHERE game_id = '{game_id}'""")
    db.commit()


def add_blackjack_game_to_db(game_id, player_1, bet):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    game = [game_id, player_1, 0, 0, 0, 0, 0, 0, 0, bet, "False"]
    cursor.execute(f'''INSERT INTO blackjack_games VALUES(?,?,?,?,?,?,?,?,?,?,?)''', game)
    db.commit()


def get_blackjack_games():
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f"""SELECT * FROM blackjack_games WHERE status = 'False' """)
    row = cursor.fetchall()
    return row


def get_blackjack_game(game_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f"""SELECT * FROM blackjack_games WHERE game_id = '{game_id}'""")
    row = cursor.fetchone()
    return row


def update_player_blackjack(game_id, player_2):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f"""UPDATE blackjack_games SET player_2 = '{player_2}' WHERE game_id = '{game_id}' """)
    db.commit()


def update_blackjack_game_status(game_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f"""UPDATE blackjack_games SET status = 'True' WHERE game_id = '{game_id}' """)
    db.commit()


def add_card_to_player(game_id, player, number):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f"""UPDATE blackjack_games SET {player}_amount = {player}_amount + 1 WHERE game_id = '{game_id}' """)
    db.commit()
    cursor.execute(
        f"""UPDATE blackjack_games SET {player}_result = {player}_result + {number} WHERE game_id = '{game_id}' """)
    db.commit()


def delete_blackjack_game(game_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f"""DELETE FROM blackjack_games WHERE game_id = '{game_id}'""")
    db.commit()


def add_game_log(game_id, winner, loser, bank, profit, game_name):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    game = [game_id, winner, loser, bank, profit, game_name, get_now_date()]
    cursor.execute(f'''INSERT INTO games_logs VALUES(?,?,?,?,?,?,?)''', game)
    db.commit()


def add_slots_log(player, bet, win, win_amount):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    game = [player, bet, win, win_amount, get_now_date()]
    cursor.execute(f'''INSERT INTO slots_logs VALUES(?,?,?,?,?)''', game)
    db.commit()


def add_jackpot_log(winner, bank, profit, losers):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    game = [winner, bank, profit, losers, get_now_date()]
    cursor.execute(f'''INSERT INTO jackpot_logs VALUES(?,?,?,?,?)''', game)
    db.commit()


def get_user_other_game_win_sum(user_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT SUM(bank - profit) FROM games_logs WHERE winner = '{user_id}'
    AND NOT game_name = 'blackjack'
    AND NOT game_name = 'bakkara' ''')
    row = cursor.fetchone()[0]
    return row


def get_user_other_game_lose_sum(user_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT SUM((bank - profit)/2) FROM games_logs WHERE loser = '{user_id}'
    AND NOT game_name = 'blackjack'
    AND NOT game_name = 'bakkara' ''')
    row = cursor.fetchone()[0]
    return row


def get_user_other_game_win_amount(user_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT COUNT(winner) FROM games_logs WHERE winner = '{user_id}'
    AND NOT game_name = 'blackjack'
    AND NOT game_name = 'bakkara' ''')
    row = cursor.fetchone()[0]
    return row


def get_user_other_lose_amount(user_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT COUNT(loser) FROM games_logs WHERE loser = '{user_id}' 
    AND NOT game_name = 'blackjack'
    AND NOT game_name = 'bakkara' ''')
    row = cursor.fetchone()[0]
    return row


def get_user_blackjack_game_win_amount(user_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT COUNT(winner) FROM games_logs WHERE winner = '{user_id}'
    AND game_name = 'blackjack' ''')
    row = cursor.fetchone()[0]
    return row


def get_user_blackjack_lose_amount(user_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT COUNT(loser) FROM games_logs WHERE loser = '{user_id}' 
    AND game_name = 'blackjack' ''')
    row = cursor.fetchone()[0]
    return row


def get_user_blackjack_game_win_sum(user_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT SUM(bank - profit) FROM games_logs WHERE winner = '{user_id}'
    AND game_name = 'blackjack' ''')
    row = cursor.fetchone()[0]
    return row


def get_user_blackjack_game_lose_sum(user_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT SUM((bank - profit)/2) FROM games_logs WHERE loser = '{user_id}'
    AND game_name = 'blackjack' ''')
    row = cursor.fetchone()[0]
    return row


def add_bakkara_game_to_db(game_id, player_1, bet):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    game = [game_id, player_1, 0, 0, 0, None, None, bet, "False"]
    cursor.execute(f'''INSERT INTO bakkara_games VALUES(?,?,?,?,?,?,?,?,?)''', game)
    db.commit()


def update_bakkara_game_status(game_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f"""UPDATE bakkara_games SET status = 'True' WHERE game_id = '{game_id}' """)
    db.commit()


def update_player_bakkara(game_id, player_2):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f"""UPDATE bakkara_games SET player_2 = '{player_2}' WHERE game_id = '{game_id}' """)
    db.commit()


def get_bakkara_game(game_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f"""SELECT * FROM bakkara_games WHERE game_id = '{game_id}'""")
    row = cursor.fetchone()
    return row


def get_bakkara_games():
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f"""SELECT * FROM bakkara_games WHERE status = 'False' """)
    row = cursor.fetchall()
    return row


def add_card_to_bakkara_player(game_id, player, number):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f"""UPDATE bakkara_games SET {player}_result = '{number}' WHERE game_id = '{game_id}' """)
    db.commit()


def add_cards_to_bakkara_player(game_id, player, cards):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f"""UPDATE bakkara_games SET {player}_cards = '{cards}' WHERE game_id = '{game_id}' """)
    db.commit()


def delete_bakkara_game(game_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f"""DELETE FROM bakkara_games WHERE game_id = '{game_id}'""")
    db.commit()


def get_user_bakkara_game_win_amount(user_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT COUNT(winner) FROM games_logs WHERE winner = '{user_id}'
    AND game_name = 'bakkara' ''')
    row = cursor.fetchone()[0]
    return row


def get_user_bakkara_lose_amount(user_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT COUNT(loser) FROM games_logs WHERE loser = '{user_id}' 
    AND game_name = 'bakkara' ''')
    row = cursor.fetchone()[0]
    return row


def get_user_bakkara_game_win_sum(user_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT SUM(bank - profit) FROM games_logs WHERE winner = '{user_id}'
    AND game_name = 'bakkara' ''')
    row = cursor.fetchone()[0]
    return row


def get_user_bakkara_game_lose_sum(user_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT SUM((bank - profit)/2) FROM games_logs WHERE loser = '{user_id}'
    AND game_name = 'bakkara' ''')
    row = cursor.fetchone()[0]
    return row


def add_jackpot_bet(user_id, bet):
    if get_jackpot_bet(user_id) == None:
        if len(get_jackpot_bets()) == 1:
            update_jackpot_end_time(time.time() + 120)
        db = sqlite3.connect('data/database.db')
        cursor = db.cursor()
        bet = [user_id, bet]
        cursor.execute(f'''INSERT INTO jackpot_bets VALUES(?,?)''', bet)
        db.commit()
    else:
        db = sqlite3.connect('data/database.db')
        cursor = db.cursor()
        cursor.execute(f'''UPDATE jackpot_bets SET bet = bet + '{bet}' WHERE user_id = '{user_id}' ''')
        db.commit()


def get_jackpot_end_time():
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f"""SELECT * FROM jackpot_game """)
    row = cursor.fetchone()[0]
    return row


def update_jackpot_end_time(end_time):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''UPDATE jackpot_game SET end_time = '{end_time}' ''')
    db.commit()


def get_jackpot_bets():
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f"""SELECT * FROM jackpot_bets """)
    row = cursor.fetchall()
    return row


def get_jackpot_bet(user_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f"""SELECT * FROM jackpot_bets WHERE user_id = '{user_id}' """)
    row = cursor.fetchone()
    return row


def get_jackpot_bets_amount():
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT SUM(bet) FROM jackpot_bets ''')
    row = cursor.fetchone()[0]
    return row


def delete_jackpot_bets():
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''DELETE FROM jackpot_bets''')
    db.commit()


def get_user_jackpot_win_amount(user_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT COUNT(winner) FROM jackpot_logs WHERE winner = '{user_id}' ''')
    row = cursor.fetchone()[0]
    return row


def get_user_jackpot_win_sum(user_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT SUM(bank - profit) FROM jackpot_logs WHERE winner = '{user_id}' ''')
    row = cursor.fetchone()[0]
    return row


def get_user_slots_game_amount(user_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT COUNT(player) FROM slots_logs WHERE player = '{user_id}' ''')
    row = cursor.fetchone()[0]
    return row


def get_user_slots_game_bet_amount(user_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT SUM(bet) FROM slots_logs WHERE player = '{user_id}' ''')
    row = cursor.fetchone()[0]
    return row


def get_user_slots_win_sum(user_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT SUM(win_amount) FROM slots_logs WHERE player = '{user_id}' ''')
    row = cursor.fetchone()[0]
    return row


def get_user_slots_lose_sum(user_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f'''SELECT SUM(win_amount) FROM slots_logs WHERE player = '{user_id}' AND win_amount = 0 ''')
    row = cursor.fetchone()[0]
    return row


def add_chat_to_db(chat_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute('''SELECT COUNT(id) FROM chats WHERE chat_id = ?''',(chat_id,))
    count = cursor.fetchone()[0]
    if count == 0:
      cursor.execute('''INSERT INTO chats(chat_id) VALUES(?)''',(chat_id,))
      db.commit()


def get_chats():
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute('''SELECT chat_id FROM chats''')
    row = cursor.fetchall()
    return row


def delete_all_game():
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    try:
      cursor.execute("""DELETE FROM other_games""")
      cursor.execute("""DELETE FROM bakkara_games""")
      cursor.execute("""DELETE FROM blackjack_games""")
      db.commit()
      return False
    except Exception as e:
      return e
  

def get_mines(user_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute('''SELECT * FROM mines WHERE creator_id = ? AND status = 1''',(user_id,))
    row = cursor.fetchone()
    return row


def save_to_db(nums=0, user_id=0, colum=''):
    global field_list
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()

    if colum == 'create':   
      values = [user_id,str(mines_map).replace('mines:', '')]
      field_list[user_id] = []
      cursor.execute(
        '''INSERT INTO mines(creator_id,mines_map) VALUES(?,?)''', values)
    elif colum == 'nums':
      cursor.execute('''UPDATE mines SET mines_nums = ? WHERE creator_id = ?''',(nums, user_id,))
    elif colum == 'bet':
      cursor.execute('''UPDATE mines SET mine_bets = ? WHERE creator_id = ?''',(nums, user_id,))
    db.commit()
    
    
def set_status_game(game_status, user_id):
    db = sqlite3.connect('data/database.db')
    try:
      cursor = db.cursor()
      cursor.execute('''UPDATE mines SET status = ? WHERE creator_id = ?''',(game_status, user_id,))   
      db.commit()
    except Exception as e:
      print(f'SQL Error set_status_game {e}')


def update_mines_map(mines_map, user_id):
    db = sqlite3.connect('data/database.db')
    try:
      cursor = db.cursor()
      cursor.execute('''UPDATE mines SET mines_map = ? WHERE creator_id = ? AND status = 1''',(str(mines_map), user_id,))
      db.commit()
    except Exception as e:
      print(f'SQL Error update_mines_map {e}')


def update_mines_open(last_win, user_id):
    db = sqlite3.connect('data/database.db')
    try:
      cursor = db.cursor()
      cursor.execute('''UPDATE mines SET mines_open = (mines_open + 1), last_win = ? WHERE creator_id = ?''',(last_win, user_id,))   
      db.commit()
    except Exception as e:
      print(f'SQL Error update_mines_open {e}')


def update_mines_num(mines_nums, user_id):
    db = sqlite3.connect('data/database.db')
    try:
      cursor = db.cursor()
      cursor.execute('''UPDATE mines SET mines_nums = ? WHERE creator_id = ? AND status = 1''',(mines_nums, user_id,))   
      db.commit()
    except Exception as e:
      print(f'SQL Error update_mines_num {e}')


def update_mines_bets(bets, user_id):
    db = sqlite3.connect('data/database.db')
    try:
      cursor = db.cursor()
      cursor.execute('''UPDATE mines SET mine_bets = ? WHERE creator_id = ? AND status = 1''',(bets, user_id,))   
      db.commit()
    except Exception as e:
      print(f'SQL Error update_mines_bets {e}')


def update_mines_wins(wins, user_id):
    db = sqlite3.connect('data/database.db')
    try:
      cursor = db.cursor()
      cursor.execute('''UPDATE mines SET current_win = ? WHERE creator_id = ? AND status = 1''',(wins, user_id,))   
      db.commit()
    except Exception as e:
      print(f'SQL Error update_mines_bets {e}')


def get_mines_map(user_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    try:
      cursor.execute('''SELECT mines_map FROM mines WHERE creator_id = ? AND status = 1''',(user_id,))
      row = cursor.fetchone()[0]
      return row
    except Exception as e:
      print(f'SQL Error get_mines_map {e}')


def and_mine_game(user_id):
    global field_list
    field_list[user_id] = []
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    try:
      cursor.execute("""DELETE FROM mines WHERE creator_id = ?""",(user_id,))
      db.commit()
      return True
    except Exception as e:
      print(f'SQL Error and_mine_game {e}')
      return e
  
  
def add_open_field(field, user_id):
    if field not in field_list.get(user_id, []):
      field_list[user_id].append(field)
    else:
      field_list[user_id] = [field]

    db = sqlite3.connect('data/database.db')
    try:
      cursor = db.cursor()
      cursor.execute('''UPDATE mines SET open_fields = ? WHERE creator_id = ? AND status = 1''',(str(field_list[user_id]), user_id,))   
      db.commit()
    except Exception as e:
      print(f'SQL Error add_open_field {e}')
      
      
def get_open_field(user_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    if field_list.get(user_id) and len(field_list.get(user_id)) > 0:
      return field_list.get(user_id)
    
    try:
      cursor.execute('''SELECT open_fields FROM mines WHERE creator_id = ? AND status = 1''',(user_id,))
      row = cursor.fetchone()[0]
      if not field_list.get(user_id):
        field_list[user_id] = eval(row)
        return eval(row)
    except Exception as e:
      print(f'SQL Error get_open_field {e}')


def add_chat_dice_game_to_db(chat_id: int, player_id_1: int, player_name_1, emoji: str, bet: int):
    try:
      values = [chat_id, player_id_1, player_name_1.replace("@@", "@"), emoji, bet]
      db = sqlite3.connect('data/database.db')
      cursor = db.cursor()
      cursor.execute(
          '''INSERT INTO chat_dice_games(chat_id, player_id_1, player_name_1, emoji, bet) VALUES(?,?,?,?,?)''', values)
      db.commit()
      return True
    except Exception as e:
      print(e)
      return False

def get_chat_last_id_dice_game():
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute('''SELECT MAX(id) FROM chat_dice_games''')
    row = cursor.fetchone()
    
    cursor.execute('''SELECT * FROM chat_dice_games WHERE id = ?''', (row[0],))
    row = cursor.fetchone()
    
    return row
  

def get_chat_dice_game_by_id(game_id: int):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(
      '''SELECT * FROM chat_dice_games WHERE id = ?''', (game_id,))
    row = cursor.fetchone()
    return row
  
  
def chat_dice_game_add_player(message_id: int, game_id: int, player_2_id: int, player_2_name: str):
    db = sqlite3.connect('data/database.db')
    values = [message_id, player_2_id, player_2_name, game_id]
    cursor = db.cursor()
    cursor.execute(
      '''UPDATE chat_dice_games SET message_id = ?, player_id_2 = ?, player_name_2 = ? WHERE id = ?''', values)   
    db.commit()
    
    
def get_chat_by_msg_id_dice_game(chat_id: int, message_id: int):
    values = [message_id, chat_id]
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(
      '''SELECT * FROM chat_dice_games WHERE message_id = ? AND chat_id = ?''', values)
    row = cursor.fetchone()
    
    return row


def chat_dice_game_add_score(game_id: int, score: int, field: str):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(
      f'''UPDATE chat_dice_games SET {field} = ? WHERE id = ?''', (score, game_id,))   
    db.commit()
    
    
def chat_dice_game_close(game_id: int):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(
      f'''UPDATE chat_dice_games SET status = ? WHERE id = ?''', (0, game_id, ))   
    db.commit()
    
    
def list_all_dice_game(chat_id: int):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(
      '''SELECT * FROM chat_dice_games WHERE chat_id = ? AND status = ? AND player_id_2 = ?''', (chat_id, 1, 0))
    row = cursor.fetchall()
    
    return row

def delete_chat_game(game_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute(f"""DELETE FROM chat_dice_games WHERE id = '{game_id}'""")
    db.commit()


def createRefillTable():
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    try:
        cursor.execute(f"""create table refill
(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    user_id    bigint(20) default NULL,
    user_login TEXT       default NULL,
    user_name  TEXT       default NULL,
    comment    TEXT       default NULL,
    amount     TEXT       default NULL,
    receipt    TEXT       default NULL,
    way_pay    tinyint(1) default 0
);

""")
        db.commit()
    except Exception as e:
        print(e)
        pass


def create_order_aaio(tg_id, value):
    db = sqlite3.connect('data/database.db')

    db.execute('INSERT INTO orders (tg_id, value, reg_date) VALUES (?, ?, ?)', (tg_id, value, datetime.datetime.now()))
    db.commit()
    
    return get_orders_by_tg_id_aaio(tg_id)[::-1][0]

def get_orders_by_tg_id_aaio(tg_id):

    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute('SELECT * FROM orders WHERE tg_id = ?', (tg_id, ))
    return cursor.fetchall()

async def get_order_by_id_aaio(order_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id, ))
    return cursor.fetchone()

async def order_is_done_aaio(order_id):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()    
    cursor.execute('UPDATE orders SET is_done = 1 WHERE id = ?', (order_id, ))
    db.commit()

def addRefill(user_id, username, user_fName, code, amount):
    try:
        createRefillTable()
    except:
        pass
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute("""INSERT INTO `refill`(`user_id`, `user_login`, `user_name`, `comment`, `amount`, `way_pay`) 
VALUES (?, ?, ?, ?, ?, ?)""", (user_id, username, user_fName, code, amount, 0))
    payId = cursor.lastrowid
    db.commit()
    return payId


def getRefillById(pid):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM refill WHERE id = ?""", (pid,))
    return cursor.fetchone()

def updRefill(am_fact, pid):
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    cursor.execute("""UPDATE refill SET way_pay = 1, receipt = ? WHERE id = ?""", (am_fact, pid))
    db.commit()




async def create_fast_kon(chat_id: int = None, amount: int = None,):
	db = sqlite3.connect('data/database.db')
	cursor = db.cursor()
	create = cursor.execute("INSERT INTO fast(chat_id, amount) VALUES (?,?)", (chat_id, amount,))
	db.commit()
	return create.lastrowid

async def add_members(fast_id: int, user_id: int, name: str):
	db = sqlite3.connect('data/database.db')
	cursor = db.cursor()
	sql = "INSERT INTO members(fast_id, user_id, name) VALUES (?,?,?)"
	cursor.execute(sql, (fast_id, user_id, name,))
	db.commit()


async def get_members_user(fast_id: int, user_id:int, select: str = "*"):
	db = sqlite3.connect('data/database.db')
	cursor = db.cursor()
	sql = cursor.execute("SELECT ? FROM members WHERE fast_id = ? AND user_id = ?", (select, fast_id, user_id,))
	return sql.fetchall()
	
async def get_fast(fast_id: int):
	db = sqlite3.connect('data/database.db')
	cursor = db.cursor()
	sql = cursor.execute(f"SELECT * FROM fast WHERE id = '{fast_id}'")
	return sql.fetchone()

async def get_members(fast_id: int, select: str = "*"):
	db = sqlite3.connect('data/database.db')
	cursor = db.cursor()
	sql = cursor.execute(f"SELECT {select} FROM members WHERE fast_id = {fast_id}")
	return sql.fetchall()
