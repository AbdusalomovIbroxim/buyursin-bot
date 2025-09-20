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
from datetime import datetime
import sys

logging.basicConfig(level=logging.INFO)

load_dotenv()

def check_single_instance():
    """Проверяет, что запущен только один экземпляр бота"""
    import socket
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', 8081))  # Порт для проверки
        print("[INFO] Бот запущен в единственном экземпляре")
        return True
    except OSError:
        print("[ERROR] Обнаружен другой экземпляр бота! Завершение...")
        return False


dis.include_router(commands.router)
dis.include_router(user.router)
dis.include_router(ad.router)
dis.include_router(admin.router)


async def on_startup():
    await db.init()
    # await db.drop_all()
    await db.create_all()


async def main():
    if not check_single_instance():
        print("[ERROR] Завершение работы бота")
        sys.exit(1)
    
    await on_startup()
    
    # threading.Thread(target=run_fake_server, daemon=True).start()

    print("[INFO] Bot started in polling mode (for dev/testing)")
    await dis.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
