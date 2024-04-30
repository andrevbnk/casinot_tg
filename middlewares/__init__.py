from aiogram import Dispatcher

from .throttling import ThrottlingMiddleware
from .usersend import ReadUser

def setup(dp: Dispatcher):
    dp.middleware.setup(ThrottlingMiddleware())
    dp.middleware.setup(ReadUser())
