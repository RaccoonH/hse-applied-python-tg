from aiogram import BaseMiddleware
from aiogram.types import Message

from data.user_data import find_user, update_user_daily_info


class CommandMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        print(f"Получено сообщение: {event.text}")

        avaliable_cmds = ["/start", "/set_profile", "/help", "/help_workout"]
        if event.text in avaliable_cmds:
            return await handler(event, data)

        after_registration_avaliable_cmd = ("/log_water", "/log_workout", "/log_food", "/add_food", "/check_progress", "/add_workout")
        daily_cmds = ("/log_water", "/log_workout", "/log_food", "/check_progress")
        if event.text.startswith(after_registration_avaliable_cmd):
            if not find_user(event.from_user.id):
                await event.answer("Данная комманда доступна после регистрации!")
                return

        if event.text.startswith(daily_cmds):
            update_user_daily_info(event.from_user.id)

        return await handler(event, data)
