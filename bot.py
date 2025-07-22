
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import math
import os

API_TOKEN = os.getenv("BOT_TOKEN") or "8138873257:AAFrhH5LJyFZTtfuKXlAz74wUUM5PeS28Y4"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_data = {}

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_data[message.from_user.id] = {}
    await message.answer("Привет! Давайте рассчитаем лизинг.
Введите стоимость техники в рублях (например: 1300000):")

@dp.message_handler(lambda message: message.text.isdigit() and 'price' not in user_data.get(message.from_user.id, {}))
async def price_handler(message: types.Message):
    user_data[message.from_user.id]['price'] = int(message.text)
    await message.answer("Введите срок лизинга в годах (1–5):")

@dp.message_handler(lambda message: message.text.isdigit() and 'term' not in user_data.get(message.from_user.id, {}))
async def term_handler(message: types.Message):
    term = int(message.text)
    if term < 1 or term > 5:
        await message.answer("Введите срок от 1 до 5 лет.")
        return
    user_data[message.from_user.id]['term'] = term
    await message.answer("Введите удорожание (% годовых), например: 10")

@dp.message_handler(lambda message: message.text.replace('.', '', 1).isdigit() and 'rate' not in user_data.get(message.from_user.id, {}))
async def rate_handler(message: types.Message):
    user_data[message.from_user.id]['rate'] = float(message.text)
    await message.answer("Введите первоначальный взнос (% от стоимости), например: 20")

@dp.message_handler(lambda message: message.text.replace('.', '', 1).isdigit() and 'advance' not in user_data.get(message.from_user.id, {}))
async def advance_handler(message: types.Message):
    uid = message.from_user.id
    user_data[uid]['advance'] = float(message.text)
    
    price = user_data[uid]['price']
    term = user_data[uid]['term']
    rate = user_data[uid]['rate']
    advance_percent = user_data[uid]['advance']

    advance = price * advance_percent / 100
    financed = price - advance
    total_with_interest = financed * math.pow(1 + rate / 100, term)
    yearly_payment = total_with_interest / term
    monthly_payment = yearly_payment / 12

    result = f"""📊 Расчёт по лизингу:

Стоимость техники: {price:,.0f} ₽
Аванс ({advance_percent:.0f}%): {advance:,.0f} ₽
Срок: {term} лет
Удорожание: {rate:.1f}% в год

Финансируемая сумма: {financed:,.0f} ₽
Итог с переплатой: {total_with_interest:,.0f} ₽

📅 Годовые платежи:
"""

    for year in range(1, term + 1):
        result += f"• Год {year}: {yearly_payment:,.0f} ₽\n"

    result += f"\n💬 Примерно {monthly_payment:,.0f} ₽ в месяц"

    await message.answer(result)

@dp.message_handler()
async def fallback_handler(message: types.Message):
    await message.answer("Пожалуйста, следуйте шагам и вводите только цифры. Начните с /start.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
