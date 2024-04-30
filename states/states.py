from aiogram.dispatcher.filters.state import StatesGroup, State

class create_promocode(StatesGroup):
    promocode_for_whom = State()
    promocode_name = State()
    promocode_summa = State()
    promocode_activations = State()
    
class get_promocode(StatesGroup):
    promocode = State()
    
class OtherGameState(StatesGroup):
    bet_amount = State()


class BlackjackGameState(StatesGroup):
    bet_amount = State()


class SlotsGameState(StatesGroup):
    bet_amount = State()


class AdminSearchUserState(StatesGroup):
    user_id = State()


class DepositQiwiState(StatesGroup):
    amount = State()


class BakkaraGameState(StatesGroup):
    bet_amount = State()


class OutputState(StatesGroup):
    amount = State()
    place = State()
    requesites = State()
    confirm = State()


class JackpotGameState(StatesGroup):
    bet_amount = State()


class AdminChangeBalance(StatesGroup):
    amount = State()
    confitm = State()


class AdminChangeComission(StatesGroup):
    percent = State()
    confitm = State()


class AdminPictureMailing(StatesGroup):
    text = State()
    picture = State()
    confirm = State()


class AdminWithoutPictureMailing(StatesGroup):
    text = State()
    confirm = State()


class balance_states(StatesGroup):
    BS1 = State()
    BS2 = State()
    BS3 = State()
    BS4 = State()
    BS5 = State()
    
    
class MinesStorage(StatesGroup):
    get_mines = State()
    bet = State()
    start = State()

class surprise_states(StatesGroup):
    id_amount = State()