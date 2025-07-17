import os
import requests
from bs4 import BeautifulSoup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# ✅ گرفتن توکن از متغیر محیطی Railway
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ توکن BOT پیدا نشد. لطفاً در Railway تنظیم کن.")

# ⚙️ اطلاعات طلا (قابل تغییر برای هر پست)
weight = 2.5             # وزن طلا (به گرم)
wage_percent = 11        # درصد اجرت
profit_percent = 7       # درصد سود
tax_percent = 0          # درصد مالیات

# ⬅️ شروع ربات
def start(update: Update, context: CallbackContext):
    update.message.reply_text("سلام! 👋 برای محاسبه قیمت، دستور /price رو بفرست.")

# ⬅️ دستور /price → دکمه برای محاسبه
def price(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("📲 محاسبه قیمت لحظه‌ای", callback_data="calculate")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("برای مشاهده قیمت نهایی، دکمه زیر را بزن:", reply_markup=reply_markup)

# ⬅️ وقتی کاربر روی دکمه کلیک می‌کنه
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    try:
        # دریافت قیمت از سایت مثقال
        html = requests.get("https://www.mesghal.com/").text
        soup = BeautifulSoup(html, "html.parser")
        price_element = soup.find("td", string="طلای 18 عیار").find_next("td")
        gold_price = int(price_element.text.replace(",", "").strip())
    except Exception as e:
        query.edit_message_text(f"❌ خطا در دریافت قیمت:\n{e}")
        return

    # محاسبه قیمت نهایی
    base = gold_price * weight
    wage = base * wage_percent / 100
    profit = (base + wage) * profit_percent / 100
    tax = (base + wage + profit) * tax_percent / 100
    final = base + wage + profit + tax

    msg = (
        f"📌 وزن طلا: {weight} گرم\n"
        f"💰 قیمت هر گرم: {gold_price:,} تومان\n"
        f"🧾 اجرت: {wage_percent}% | سود: {profit_percent}% | مالیات: {tax_percent}%\n\n"
        f"✅ قیمت نهایی: {final:,.0f} تومان"
    )
    query.edit_message_text(msg)

# ⬅️ اجرای ربات
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
