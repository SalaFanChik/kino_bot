from aiogram.dispatcher.filters.state import StatesGroup, State
class MySG(StatesGroup):
    main = State()
    video = State()

class YouSG(StatesGroup):
    main = State()
    video = State()
