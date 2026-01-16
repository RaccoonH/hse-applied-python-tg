from aiogram.fsm.state import State, StatesGroup


class ProfileForm(StatesGroup):
    name = State()
    age = State()
    weight = State()
    height = State()
    is_male = State()
    sport_time = State()
    city = State()


class WaterLogForm(StatesGroup):
    setting_water = State()


class WorkoutLogForm(StatesGroup):
    setting_workout = State()


class WorkoutAddForm(StatesGroup):
    setting_workout = State()


class FoodLogForm(StatesGroup):
    setting_food = State()


class AddFoodForm(StatesGroup):
    adding_food = State()
