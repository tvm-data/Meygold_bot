import os
import re
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ توکن BOT پیدا نشد. لطفاً در Railway تنظیم کن.")

# ذخیره اطلاعات پست‌ها (chat_id, message_id) -> داده‌های وزن و درصدها
latest_data = {}

def extract_info(text):
    try:
        pattern = r"وزن[:\-]?\s*([\d\.,/]+).*?اجرت[:\-]?\s*(\d+).*?سود[:\-]?\s*(\d+).*?مالیات[:\-]?\s*(\d+)"
        match = re.search(pattern, text.replace("٫", ".").replace("،", ","), re.DOTALL)
        if not match:
            return None
        weight = float(match.group(1).replace("/", ".").replace(",", "."))
        wage = int(match.group(2))
        profit = int(match.group(3))
        tax = int(match.group(4))
        return {
            "weight": weight,
            "wage": wage,
            "profit": profit,
            "tax": tax
        }
    except:
        return None

def start(update: Update, context: CallbackContext):
    update.message.reply_text("سلام! پست‌هایی که شامل وزن، اجرت، سود و مالیات باشن رو همراه دکمه قیمت‌گذاری می‌کنم.")

def post_handler(update: Update, context: CallbackContext):
    text = update.message.caption or update.message.text
    data = extract_info(text)
    if not data:
        return
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    latest_data[(chat_id, message_id)] = data

    keyboard = [[InlineKeyboardButton("📲 محاسبه قیمت", callback_data=f"calc|{chat_id}|{message_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=chat_id, text="برای محاسبه قیمت نهایی دکمه زیر را بزنید 👇", reply_markup=reply_markup)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    try:
        _, chat_id, message_id = query.data.split("|")
        key = (int(chat_id), int(message_id))
        data = latest_data.get(key)
        if not data:
            query.edit_message_text("❌ اطلاعات مربوط به این پست پیدا نشد.")
            return

        res = requests.get("https://api.tgju.org/v1/market/summary")
        gold_data = res.json()
        price_str = gold_data["gold_18"]["p"].replace(",", "").strip()
        gold_price = int(price_str)

        weight = data["weight"]
        wage_percent = data["wage"]
        profit_percent = data["profit"]
        tax_percent = data["tax"]

        base = gold_price * weight
        wage = base * wage_percent / 100
        profit = (base + wage) * profit_percent / 100
        tax = (base + wage + profit) * tax_percent / 100
        final = base + wage + profit + tax

        msg = (
            f"📌 وزن: {weight} گرم\n"
            f"💰 قیمت هر گرم: {gold_price:,} تومان\n"
            f"🧾 اجرت: {wage_percent}% | سود: {profit_percent}% | مالیات: {tax_percent}%\n\n"
            f"✅ قیمت نهایی: {final:,.0f} تومان"
        )
        query.edit_message_text(msg)

    except Exception as e:
        query.edit_message_text(f"❌ خطا در محاسبه:\n{e}")

def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text | Filters.caption, post_handler))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
