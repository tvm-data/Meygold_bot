import os
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# گرفتن توکن ربات از متغیر محیطی
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("توکن ربات پیدا نشد! لطفا BOT_TOKEN رو تنظیم کن.")

gold_api_url = "https://api.tgju.org/v1/json"

# داده‌های پیش‌فرض وزن و درصدها
weight = 2.5  # گرم
wage_percent = 11
profit_percent = 7
tax_percent = 0

def start(update: Update, context: CallbackContext):
    update.message.reply_text("سلام! من ربات محاسبه قیمت لحظه‌ای طلا هستم.\nبرای محاسبه قیمت، دستور /price را بفرستید.")

def price(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("محاسبه قیمت لحظه‌ای", callback_data="calculate")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("برای دیدن قیمت نهایی روی دکمه زیر بزنید:", reply_markup=reply_markup)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "calculate":
        try:
            res = requests.get(gold_api_url).json()
            gold_price = int(res["gold"]["price"])

            base = gold_price * weight
            wage = base * wage_percent / 100
            profit = (base + wage) * profit_percent / 100
            tax = (base + wage + profit) * tax_percent / 100
            final = base + wage + profit + tax

            msg = (
                f"💎 قیمت نهایی:\n"
                f"وزن: {weight} گرم\n"
                f"قیمت طلا: {gold_price:,} تومان\n\n"
                f"💰 قیمت نهایی: {final:,.0f} تومان"
            )
            query.edit_message_text(msg)
        except Exception as e:
            query.edit_message_text(f"خطا در دریافت قیمت: {e}")

def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("price", price))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
