from aiogram.fsm.state import State, StatesGroup

class ElonState(StatesGroup):
    choosing_region = State()  # Viloyat tanlash bosqichi
    viewing_elons = State()    # E'lonlarni ko'rish bosqichi
    select_route = State()
    b_route = State() # Yunalishlarni tanlash
    viewing_route_elons = State()