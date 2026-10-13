import asyncio
import os

import requests
from aiogram import Bot, Dispatcher
from aiogram import F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup,CallbackQuery 
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
def get_all_rates():
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    rates = {}
    for code, info in data["Valute"].items():
        rates[code] = info["Value"] / info["Nominal"]
    return rates

def parse_convert(text):
    parts = text.split()

    if len(parts) != 3:
        return None
    try:
        amount = float(parts[1])
    except ValueError:
        return None

    code = parts[2].upper()
    return amount, code

def convert(text):
    parsed = parse_convert(text)
    if parsed is None:
        return "Формат: /convert 100 USD"
    amount, code = parsed
    if amount <= 0:
        return "Сумма должна быть больше нуля"
    rates = get_all_rates()
    if code not in rates:
        return f"Валюта {code} не найдена"

    result = amount * rates[code]
    return f"{amount:.2f} {code} = {result:.2f} руб."

def rates_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="USD", callback_data="rate_USD"),
            InlineKeyboardButton(text="EUR", callback_data="rate_EUR"),
            InlineKeyboardButton(text="CNY", callback_data="rate_CNY")
        ]
    ])

@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Привет! Нажми на кнопку, чтобы узнать курс, или напиши /convert 100 USD.", reply_markup=rates_keyboard())
@dp.callback_query(F.data.startswith("rate_"))
async def on_rate_button(callback: CallbackQuery):
    code = callback.data.split("_")[1]

    try:
        rates = await asyncio.to_thread(get_all_rates)
    except requests.RequestException:
        await callback.message.answer("Не удалось получить курс. Попробуйте позже")
        await callback.answer()
        return
    await callback.message.answer(f"{code}: {rates[code]:.2f} руб.")
    await callback.answer()
@dp.message(Command("rate"))
async def cmd_rate(message: Message):
    try:
        usd, eur = get_rates()
        await message.answer(f"Курс валют:\nUSD: {usd:.2f} руб.\nEUR: {eur:.2f} руб.")
    except requests.RequestException:
        await message.answer("Ошибка сети или недоступность сервера. Пожалуйста, проверьте подключение к интернету и попробуйте снова.")
@dp.message(Command("convert"))
async def cmd_convert(message: Message):
    try:
        answer = await asyncio.to_thread(convert, message.text)
    except requests.RequestException:
        await message.answer("Не удалось получить курс. Пробуйте позже")
        return
    await message.answer(answer)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())