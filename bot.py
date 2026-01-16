from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers import set_profile, main_commands
from middleware import CommandMiddleware
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web


if __name__ == "__main__":
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.message.middleware(CommandMiddleware())
    dp.include_routers(main_commands.router, set_profile.router)

    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(dp, bot)
    webhook_requests_handler.register(app, path="/webhook")
    setup_application(app, dp, bot=bot)

    print("Бот запущен!")
    web.run_app(app, host="0.0.0.0", port=10000)
