import asyncio
import os

import requests
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise SystemExit("Не найден BOT_TOKEN. Проверьте файл .env")

url = "https://www.cbr-xml-daily.ru/daily_json.js"

bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_rates():
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    usd = data["Valute"]["USD"]["Value"]
    eur = data["Valute"]["EUR"]["Value"]
    return usd, eur

@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Привет! Напиши /rate, чтобы узнать текущий курс валют.")
@dp.message(Command("rate"))
async def cmd_rate(message: Message):
    try:
        usd, eur = get_rates()
        await message.answer(f"Курс валют:\nUSD: {usd:.2f} руб.\nEUR: {eur:.2f} руб.")
    except requests.RequestException:
        await message.answer("Ошибка сети или недоступность сервера. Пожалуйста, проверьте подключение к интернету и попробуйте снова.")
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())