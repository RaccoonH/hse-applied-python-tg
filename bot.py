import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN, WEBHOOK
from handlers import set_profile, main_commands
from middleware import CommandMiddleware
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web


async def main():
    if WEBHOOK:
        bot = Bot(token=TOKEN)
        dp = Dispatcher()
        dp.message.middleware(CommandMiddleware())
        dp.include_routers(main_commands.router, set_profile.router)

        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(dp, bot)
        webhook_requests_handler.register(app, path="/webhook")
        setup_application(app, dp, bot=bot)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 10000)
        await site.start()

        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(url=WEBHOOK)

        print("Бот запущен!")
        await asyncio.Event().wait()
        await runner.cleanup()
    else:
        bot = Bot(token=TOKEN)
        dp = Dispatcher()
        dp.message.middleware(CommandMiddleware())
        dp.include_routers(main_commands.router, set_profile.router)
        print("Бот запущен!")
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
