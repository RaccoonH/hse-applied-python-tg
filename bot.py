import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers import set_profile, main_commands
from middleware import CommandMiddleware

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.message.middleware(CommandMiddleware())
dp.include_routers(main_commands.router, set_profile.router)


async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
