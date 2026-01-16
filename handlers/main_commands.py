from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from plots import draw_hbar

from handlers.states import WaterLogForm, WorkoutLogForm, FoodLogForm, AddFoodForm, WorkoutAddForm
from handlers.weather import get_weather_temp

import data.user_data as user_data
import data.workouts as workouts
import data.food as food

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply("Добро пожаловать, я помогу вам контролировать питание, тренировки и ежедневные нормы для поддержания здорового образа жизни.")
    if user_data.find_user(message.from_user.id):
        await message.answer(f"Привет {user_data.get_user(message.from_user.id).name}! 👋")
    else:
        await message.answer("К сожалению ваш аккаунт не был найден в базе данных, начните регистрацию используя комманду /set_profile")


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply(
        "Доступные команды:\n"
        "/start - Начало работы.\n"
        "/log_water <количество> - Добавление информации о выпитой воды.\n"
        "/log_workout <тип тренировки> <время (мин)> - Добавление информации о тренировке.\n"
        "/add_workout <название тренировки> <MET> - Добавление типа тренировка.\n"
        "/help_workout - Вывод типов тренировки.\n"
        "/log_food <название продукта> <вес> - Добавление съеденой еды.\n"
        "/add_food <название продукта> <калории на 100г> - Добавление собственной еды.\n"
        "/check_progress - Просмотр прогресса.\n"
        "/set_profile - Настройка пользователя.\n"
        "/help - Помощь.\n"
    )


@router.message(Command("help_workout"))
async def cmd_help_workout(message: Message):
    av_workouts = workouts.get_available_workouts(message.from_user.id)
    workouts_str = "\n".join(f"{work}: {met} MET" for work, met in av_workouts.items())
    await message.reply(f"Доступные тренировки:\n{workouts_str}")


async def set_water(message, water):
    if not water.isdigit() or int(water) == 0:
        await message.reply("❌ Некорректное значение для воды!")
        return

    user_id = message.from_user.id
    water_curr = user_data.log_water(user_id, int(water))
    water_intake = user_data.get_water_goal(user_id)
    weather_temp = get_weather_temp(user_data.get_user(user_id).city)
    if weather_temp > 25:
        water_intake += 500
    await message.reply(f"🥤 Выпито {water_curr} мл из {water_intake} мл")
    return


@router.message(Command("log_water"))
async def log_water(message: Message, state: FSMContext):
    spl = message.text.split()
    if len(spl) == 1:
        await message.reply("Введите количество выпитой воды в миллилитрах")
        await state.set_state(WaterLogForm.setting_water)
    elif len(spl) == 2:
        await set_water(message, spl[1])
    else:
        await message.reply("❌ Некорректный ввод команды!\nПример: /log_water 100")


@router.message(WaterLogForm.setting_water)
async def log_set_water(message: Message, state: FSMContext):
    await set_water(message, message.text)
    await state.clear()


async def add_workout(message, workout, met):
    try:
        float(met)
    except ValueError:
        await message.reply("❌ Некорректное значение для MET!")
        return
    workouts.add_workout(message.from_user.id, workout, float(met))
    await message.reply(f"💪 Добавлено {workout}, MET {met}")


@router.message(Command("add_workout"))
async def add_workout_cmd(message: Message, state: FSMContext):
    spl = message.text.split()
    if len(spl) == 1:
        await message.reply("Введите название тренировки и MET (metabolic equivalent of task)")
        await state.set_state(WorkoutAddForm.setting_workout)
    elif len(spl) >= 3:
        workout = " ".join(spl[1:-1])
        await add_workout(message, workout, spl[-1])
    else:
        await message.reply("❌ Некорректный ввод команды!\nПример: /add_workout анжуманя 5.0")


@router.message(WorkoutAddForm.setting_workout)
async def add_workout_cmd2(message: Message, state: FSMContext):
    spl = message.text.split()
    if len(spl) < 2:
        await message.reply("❌ Некорректный ввод команды!\nПример: /add_workout анжуманя 5.0")
        await state.clear()
        return

    workout = " ".join(spl[:-1])
    await add_workout(message, workout, spl[1])
    await state.clear()


async def set_workout(message, workout, duration):
    if not duration.isdigit() or int(duration) == 0:
        await message.reply("❌ Некорректное число для длительности!")
        return
    if not workouts.is_workout_available(message.from_user.id, workout):
        await message.reply(f"❌ Неизвестная тренировка {workout}! Чтобы посмотреть список доступных тренировок введите /help_workout")
        return

    user_id = message.from_user.id
    calories_burned = user_data.log_workout(user_id, workout, int(duration))

    water_intake = round((int(duration) // 30) * 200)
    water_intake_str = ""
    if water_intake > 0:
        water_intake_str = f" Дополнительно: выпейте {water_intake} мл воды."
    await message.reply(f"💪 {workout} {duration} минут - {calories_burned} ккал.{water_intake_str}")


@router.message(Command("log_workout"))
async def log_workout(message: Message, state: FSMContext):
    spl = message.text.split()
    if len(spl) == 1:
        await message.reply("Введите название тренировки и ее длительность в минутах")
        await state.set_state(WorkoutLogForm.setting_workout)
    elif len(spl) >= 3:
        workout = " ".join(spl[1:-1])
        await set_workout(message, workout, spl[-1])
    else:
        await message.reply("❌ Некорректный ввод команды!\nПример: /log_workout бег 30")


@router.message(WorkoutLogForm.setting_workout)
async def log_set_workout(message: Message, state: FSMContext):
    spl = message.text.split()
    if len(spl) < 2:
        await message.reply("❌ Некорректный ввод команды!\nПример: /log_workout бег 30")
        await state.clear()
        return

    workout = " ".join(spl[:-1])
    await set_workout(message, workout, spl[1])
    await state.clear()


class FoodListCallback(CallbackData, prefix="food_list"):
    food_id: int
    page: int
    select: bool


ITEMS_PER_PAGE = 5
def food_list_keyboard(food_list, page) -> InlineKeyboardMarkup:
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_food = food_list.iloc[start:end]

    keyboard = []

    counter = 0
    for i, product in page_food["product_name"].items():
        counter += 1
        keyboard.append([
            InlineKeyboardButton(
                text=f"[{start + counter}] {product}",
                callback_data=FoodListCallback(
                    select=True,
                    page=page,
                    food_id=i,
                ).pack()
            )
        ])

    nav_buttons = []

    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=FoodListCallback(
                    select=False,
                    page=page - 1,
                    food_id=0,
                ).pack()
            )
        )

    if end < len(food_list):
        nav_buttons.append(
            InlineKeyboardButton(
                text="➡️ Далее",
                callback_data=FoodListCallback(
                    select=False,
                    page=page + 1,
                    food_id=0,
                ).pack()
            )
        )

    if nav_buttons:
        keyboard.append(nav_buttons)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.callback_query(FoodListCallback.filter())
async def food_list_callback(callback, callback_data, state: FSMContext):
    data = await state.get_data()
    if callback_data.select:
        food_info = food.get_food_by_id(callback.from_user.id, callback_data.food_id)
        food_weight = int(data.get("weight"))
        calories = food_info['energy-kcal_100g'] * (food_weight / 100)
        eaten_calories = user_data.log_food(callback.from_user.id, calories)
        standard_calories = user_data.get_calories_goal(callback.from_user.id)
        await callback.message.edit_text(
            f"🍎 Съедено {calories:.2f} ккал. Потреблено {eaten_calories:.2f} ккал из {standard_calories:.2f} ккал."
        )
        await state.clear()
    else:
        await callback.message.edit_reply_markup(
            reply_markup=food_list_keyboard(data.get('list'), page=callback_data.page)
        )
    await callback.answer()


async def set_food(message, food_name, weight, state):
    if not weight.isdigit() or int(weight) == 0:
        await message.reply("❌ Некорректное число для веса продукта!")
        return

    found_food = food.find_food(message.from_user.id, food_name)
    len_found_food = len(found_food)
    if len_found_food == 0:
        await message.reply(f'❌ Не удалось найти продукт с названием "{food_name}"!')
        return
    elif len_found_food > 1:
        await state.update_data(list=found_food)
        await state.update_data(weight=weight)
        await message.answer(f"Найдено {len_found_food} продуктов.\nВыберите продукт:", reply_markup=food_list_keyboard(found_food, 0))
        return

    food_info = found_food.iloc[0]
    calories = food_info['energy-kcal_100g'] * (int(weight) / 100)
    eaten_calories = user_data.log_food(message.from_user.id, calories)
    standard_calories = user_data.get_calories_goal(message.from_user.id)
    await message.reply(
        f"🍎 Съедено {calories:.2f} ккал. Потреблено {eaten_calories:.2f} ккал из {standard_calories:.2f} ккал."
    )
    await state.clear()


@router.message(Command("log_food"))
async def log_food(message: Message, state: FSMContext):
    spl = message.text.split()
    if len(spl) == 1:
        await message.reply("Введите название продукта и его вес")
        await state.set_state(FoodLogForm.setting_food)
    elif len(spl) >= 3:
        food_name = " ".join(spl[1:-1])
        await set_food(message, food_name, spl[-1], state)
    else:
        await message.reply("❌ Некорректный ввод команды!\nПример: /log_food цуккини 50")


@router.message(FoodLogForm.setting_food)
async def log_set_food(message: Message, state: FSMContext):
    spl = message.text.split()
    if len(spl) < 2:
        await message.reply("❌ Некорректный ввод команды!\nПример: /log_food цуккини 50")
        await state.clear()
        return

    food_name = " ".join(spl[:-1])
    await set_food(message, food_name, spl[-1], state)


async def add_food_to_db(message, food_name, calories):
    try:
        calories = float(calories)
    except ValueError:
        await message.reply("❌ Некорректное число для калорий!")
        return

    food.add_user_food(message.from_user.id, food_name, calories)
    await message.reply(
        f"🍎 Добавлен {food_name}, калории за 100г: {calories:.2f}"
    )


@router.message(Command("add_food"))
async def add_food(message: Message, state: FSMContext):
    spl = message.text.split()
    if len(spl) == 1:
        await message.reply("Введите название продукта и калорийность")
        await state.set_state(AddFoodForm.adding_food)
    elif len(spl) >= 3:
        food_name = " ".join(spl[1:-1])
        await add_food_to_db(message, food_name, spl[-1])
    else:
        await message.reply("❌ Некорректный ввод команды!\nПример: /add_food мой любимый шоколад 50")


@router.message(AddFoodForm.adding_food)
async def add_food_form(message: Message, state: FSMContext):
    spl = message.text.split()
    if len(spl) < 2:
        await message.reply("❌ Некорректный ввод команды!\nПример: /add_food мой любимый шоколад 50")
        await state.clear()
        return

    food_name = " ".join(spl[:-1])
    await add_food_to_db(message, food_name, spl[-1])


@router.message(Command("check_progress"))
async def check_progress(message: Message):
    progress = user_data.get_progress(message.from_user.id)

    water_progress = f'Вода:\n- Выпито: {progress.water_curr} мл из {progress.water_intake} мл.'
    water_balance = progress.water_intake - progress.water_curr
    if water_balance > 0:
        water_progress += f"\n- Осталось {water_balance} мл."

    calories_progress = f'''Калории:
- Потреблено: {progress.calories_eaten:.2f} ккал из {progress.calories_standard:.2f} ккал.
- Сожжено: {progress.calories_burned:.2f} ккал.
- Баланс: {(progress.calories_eaten - progress.calories_burned):.2f} ккал.
    '''

    items_for_plot = {
        "Вода": (progress.water_curr, progress.water_intake),
        "Калории": (progress.calories_eaten, progress.calories_standard)
    }
    plot = draw_hbar(items_for_plot, message.from_user.id)
    await message.answer_photo(
        photo=FSInputFile(plot),
        caption=f'📊 Прогресс:\n{water_progress}\n\n{calories_progress}'
    )
