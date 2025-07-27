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

def run_fake_server():
    import http.server
    import socketserver

    port = int(os.environ.get("PORT", 8080))
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"Serving fake HTTP on port {port}")
        httpd.serve_forever()

# Функция для поддержания активности бота с настраиваемыми интервалами
async def keep_alive_advanced():
    """Отправляет сообщение с настраиваемыми интервалами для поддержания активности"""
    admin_id = 1501361138  # Ваш ID в Telegram
    
    # Настройки интервалов (в секундах)
    intervals = {
        "short": 300,    # 5 минут - для активного времени
        "medium": 900,   # 15 минут - для обычного времени  
        "long": 1800     # 30 минут - для ночного времени
    }
    
    current_interval = intervals["medium"]  # По умолчанию 15 минут
    message_count = 0
    
    while True:
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message_count += 1
            
            # Определяем интервал в зависимости от времени
            hour = datetime.now().hour
            if 8 <= hour <= 22:  # Дневное время
                current_interval = intervals["short"]
                time_status = "🌞 Дневное время"
            elif 22 <= hour or hour <= 6:  # Ночное время
                current_interval = intervals["long"]
                time_status = "🌙 Ночное время"
            else:
                current_interval = intervals["medium"]
                time_status = "🌅 Утреннее время"
            
            message = f"🤖 Бот активен! #{message_count}\n"
            message += f"⏰ Время: {current_time}\n"
            message += f"📊 Статус: {time_status}\n"
            message += f"⏱️ Следующее сообщение через {current_interval//60} мин\n"
            message += "✅ Все системы работают нормально"
            
            await bot.send_message(admin_id, message)
            print(f"[KEEP_ALIVE] Сообщение #{message_count} отправлено в {current_time}")
            
        except Exception as e:
            print(f"[KEEP_ALIVE] Ошибка отправки: {e}")
        
        # Ждем заданный интервал
        await asyncio.sleep(current_interval)

dis.include_router(commands.router)
dis.include_router(ad.router)
dis.include_router(user.router)
dis.include_router(admin.router)

async def on_startup():
    await db.init()
    await db.create_all()

async def main():
    await on_startup()
    
    # Запускаем фейковый HTTP сервер в отдельном потоке
    threading.Thread(target=run_fake_server, daemon=True).start()
    
    # Запускаем функцию поддержания активности
    asyncio.create_task(keep_alive_advanced())
    
    print("[INFO] Bot started in polling mode with keep-alive")
    await dis.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main()) 