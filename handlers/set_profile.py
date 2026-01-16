from aiogram.types import Message
from aiogram.filters import Command
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters.callback_data import CallbackData

import data.user_data as user_data
from handlers.states import ProfileForm
from handlers.weather import get_weather
import json

router = Router()


@router.message(Command("set_profile"))
async def start_profile(message: Message, state: FSMContext):
    user_data.remove_user(message.from_user.id)
    await message.reply("Как вас зовут?")
    await state.set_state(ProfileForm.name)


@router.message(ProfileForm.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply("Сколько вам лет?")
    await state.set_state(ProfileForm.age)


class GenderCallback(CallbackData, prefix="gender"):
    is_male: bool


@router.message(ProfileForm.age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.reply("Некорректный ввод возраста!")
        return

    await state.update_data(age=int(message.text))
    await message.reply("Какой у вас вес в кг?")
    await state.set_state(ProfileForm.weight)


@router.message(ProfileForm.weight)
async def process_weight(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.reply("Некорректный ввод веса!")
        return

    await state.update_data(weight=int(message.text))
    await message.reply("Какой у вас рост в см?")
    await state.set_state(ProfileForm.height)


@router.message(ProfileForm.height)
async def process_height(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.reply("Некорректный ввод роста!")
        return

    await state.update_data(height=int(message.text))
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Мужской", callback_data=GenderCallback(is_male="true").pack())],
        [InlineKeyboardButton(text="Женский", callback_data=GenderCallback(is_male="false").pack())]
    ])
    await message.reply("Укажите свой пол", reply_markup=keyboard)
    await state.set_state(ProfileForm.is_male)


@router.callback_query(ProfileForm.is_male, GenderCallback.filter())
async def choose_gender(callback: CallbackQuery, callback_data: GenderCallback, state: FSMContext):
    await state.update_data(is_male=callback_data.is_male)

    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.reply("Сколько минут активности у вас в день?")
    await state.set_state(ProfileForm.sport_time)


@router.message(ProfileForm.sport_time)
async def process_sport_time(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.reply("Некорректный ввод активности!")
        return

    await state.update_data(sport_time=int(message.text))
    await message.reply("В каком городе вы находитесь? (укажите на английском языке, например Moscow)")
    await state.set_state(ProfileForm.city)


@router.message(ProfileForm.city)
async def process_city(message: Message, state: FSMContext):
    res = get_weather(message.text)
    if res.status_code != 200:
        message.reply("Город не найден, проверьте что ввели корректное название. Попробуйте еще раз.")
        return

    await state.update_data(city=message.text)
    await message.reply("Регистрация завершена 🎉")

    data = await state.get_data()
    timezone = json.loads(res.text)["timezone"] / 3600

    user_data.add_user(message.from_user.id,
                       data.get('name'),
                       data.get('age'),
                       data.get('weight'),
                       data.get('height'),
                       data.get('is_male'),
                       data.get('sport_time'),
                       data.get('city'),
                       timezone)
    await state.clear()
