import os, re, requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN پیدا نشد. لطفاً در Railway تنظیم کن.")

latest_data = {}

def extract_info(text):
    pattern = r"وزن[:\-]?\s*([\d\.,/]+).*?اجرت[:\-]?\s*(\d+).*?سود[:\-]?\s*(\d+).*?مالیات[:\-]?\s*(\d+)"
    match = re.search(pattern, text.replace("٫", ".").replace("،", ","), re.DOTALL)
    if not match:
        return None
    weight = float(match.group(1).replace("/", ".").replace(",", "."))
    return {
        "weight": weight,
        "wage": int(match.group(2)),
        "profit": int(match.group(3)),
        "tax": int(match.group(4))
    }

def start(update: Update, context: CallbackContext):
    update.message.reply_text("سلام! پست‌هایی با وزن، اجرت، سود و مالیات دارن رو تشخیص میدم و دکمه محاسبه می‌فرستم.")

def post_handler(update: Update, context: CallbackContext):
    text = update.message.caption or update.message.text
    data = extract_info(text)
    if not data:
        return
    key = (update.message.chat_id, update.message.message_id)
    latest_data[key] = data
    keyboard = [[InlineKeyboardButton("📲 محاسبه قیمت", callback_data=f"calc|{key[0]}|{key[1]}")]]
    context.bot.send_message(chat_id=key[0], text="برای محاسبه قیمت دکمه رو بزن 👇", reply_markup=InlineKeyboardMarkup(keyboard))

def button(update: Update, context: CallbackContext):
    query = update.callback_query; query.answer()
    try:
        _, chat_id, message_id = query.data.split("|")
        data = latest_data.get((int(chat_id), int(message_id)))
        if not data:
            query.edit_message_text("❌ اطلاعات آموزشی پست موجود نیست.")
            return

        resp = requests.get("https://api.tgju.org/v1/market/summary")
        obj = resp.json()
        price = int(obj["gold_18"]["p"].replace(",", "").strip())

        w, wp, pp, tp = data["weight"], data["wage"], data["profit"], data["tax"]
        base = price * w
        wage = base * wp / 100
        profit = (base + wage) * pp / 100
        tax = (base + wage + profit) * tp / 100
        final = base + wage + profit + tax

        msg = (
            f"📌 وزن: {w} گرم\n"
            f"💰 قیمت طلا: {price:,} تومان\n"
            f"🧾 اجرت: {wp}% | سود: {pp}% | مالیات: {tp}%\n\n"
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
