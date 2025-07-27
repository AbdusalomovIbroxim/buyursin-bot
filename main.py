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

# Функция для поддержания активности бота
async def keep_alive():
    """Отправляет сообщение каждую минуту для поддержания активности"""
    admin_id = 1501361138  # Ваш ID в Telegram
    while True:
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"🤖 Бот активен! Время: {current_time}\n✅ Все системы работают нормально"
            await bot.send_message(admin_id, message)
            print(f"[KEEP_ALIVE] Сообщение отправлено в {current_time}")
        except Exception as e:
            print(f"[KEEP_ALIVE] Ошибка отправки: {e}")
        
        # Ждем 60 секунд (1 минуту)
        await asyncio.sleep(60)


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
    
    # Запускаем фейковый HTTP сервер в отдельном потоке
    threading.Thread(target=run_fake_server, daemon=True).start()
    
    # Запускаем функцию поддержания активности
    asyncio.create_task(keep_alive())
    
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
