import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import requests

TOKEN = os.getenv("BOT_TOKEN")

gold_api_url = "https://api.tgju.org/v1/json"

def start(update, context):
    update.message.reply_text("سلام! من ربات محاسبه قیمت لحظه‌ای طلا هستم.")

def calculate_price(update, context):
    # نمونه ساده: فقط عدد ثابت وزن
    weight = 2.5  # گرم
    wage_percent = 11
    profit_percent = 7
    tax_percent = 0

    res = requests.get(gold_api_url).json()
    gold_price = int(res["gold"]["price"])
    
    base = gold_price * weight
    wage = base * wage_percent / 100
    profit = (base + wage) * profit_percent / 100
    tax = (base + wage + profit) * tax_percent / 100
    final = base + wage + profit + tax

    msg = f"💎 قیمت نهایی:\nوزن: {weight} گرم\nقیمت طلا: {gold_price:,} تومان\n\n💰 قیمت نهایی: {final:,.0f} تومان"
    update.message.reply_text(msg)

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("price", calculate_price))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
