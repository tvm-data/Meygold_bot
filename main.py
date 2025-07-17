import os
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# 🟢 توکن ربات تلگرام از محیط Railway یا فایل env
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("توکن ربات پیدا نشد! لطفا BOT_TOKEN رو تنظیم کن.")

# 🟡 مشخصات طلا (مقدار قابل تغییر برای هر محصول)
weight = 2.5  # وزن طلای این پست به گرم
wage_percent = 11  # درصد اجرت
profit_percent = 7  # درصد سود
tax_percent = 0     # درصد مالیات (در صورت نیاز)

# 🔵 آدرس API برای گرفتن قیمت گرم ۱۸ از Nerkh-API
API_URL = "http://nerkh-api.ir/api//gold/"

# 🟠 وقتی کاربر /start رو می‌فرسته
def start(update: Update, context: CallbackContext):
    update.message.reply_text("سلام! من ربات محاسبه قیمت لحظه‌ای طلا هستم.\nبرای محاسبه قیمت، دستور /price رو بفرست.")

# 🟠 وقتی کاربر /price رو می‌فرسته
def price(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("📲 محاسبه قیمت لحظه‌ای", callback_data="calculate")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("برای دیدن قیمت نهایی، دکمه زیر را فشار بده:", reply_markup=reply_markup)

# 🟠 وقتی کاربر روی دکمه کلیک می‌کنه
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data != "calculate":
        return

    try:
        res = requests.get(API_URL, timeout=10).json()
        gold_price = float(res["data"]["prices"]["geram18"]["current"])
    except Exception as e:
        query.edit_message_text(f"❌ خطا در دریافت قیمت طلا: {e}")
        return

    base = gold_price * weight
    wage = base * wage_percent / 100
    profit = (base + wage) * profit_percent / 100
    tax = (base + wage + profit) * tax_percent / 100
    final = base + wage + profit + tax

    msg = (
        f"🔖 وزن: {weight} گرم\n"
        f"💰 قیمت هر گرم طلا ۱۸ عیار: {gold_price:,.0f} تومان\n"
        f"🧾 اجرت: {wage_percent}% | سود: {profit_percent}% | مالیات: {tax_percent}%\n\n"
        f"✅ قیمت نهایی: {final:,.0f} تومان"
    )
    query.edit_message_text(msg)

# 🟣 شروع ربات
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
