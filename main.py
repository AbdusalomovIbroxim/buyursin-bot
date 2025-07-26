from dotenv import load_dotenv
import aiobot.handlers.commands as commands
import aiobot.handlers.user as user
import aiobot.handlers.ad as ad
import aiobot.handlers.admin as admin
import asyncio
import logging
from dispatcher.dispatcher import dis, bot
from aiobot.database import db
import threading
import os

logging.basicConfig(level=logging.INFO)

load_dotenv()

# Простой способ загрузки .env без python-dotenv
# import os
# try:
#     with open('.env', 'r') as f:
#         for line in f:
#             if '=' in line and not line.startswith('#'):
#                 key, value = line.strip().split('=', 1)
#                 os.environ[key] = value.strip('"').strip("'")
# except FileNotFoundError:
#     pass
def run_fake_server():
    import http.server
    import socketserver

    port = int(os.environ.get("PORT", 8080))
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"Serving fake HTTP on port {port}")
        httpd.serve_forever()


dis.include_router(commands.router)
dis.include_router(ad.router)
dis.include_router(user.router)
dis.include_router(admin.router)


async def on_startup():
    await db.init()
    # await db.drop_all()
    await db.create_all()


async def main():
    await on_startup()
    # Для высокой нагрузки используйте webhook (см. комментарии ниже)
    # await dis.start_webhook(
    #     bot,
    #     webhook_path="/webhook",
    #     webhook_url="https://yourdomain.com/webhook",
    # )
    print("[INFO] Bot started in polling mode (for dev/testing)")
    await dis.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
