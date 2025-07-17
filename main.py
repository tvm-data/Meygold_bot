import os
from telegram.ext import Updater, CommandHandler

# ۱. گرفتن توکن ربات از متغیر محیطی
TOKEN = os.getenv("BOT_TOKEN")

# اگر توکن موجود نبود، ارور بده
if not TOKEN:
    raise ValueError("توکن ربات پیدا نشد! لطفا BOT_TOKEN رو تنظیم کن.")

# ۲. تابعی که موقع ارسال دستور /start اجرا میشه
def start(update, context):
    update.message.reply_text("سلام! ربات آماده است.")

# ۳. تابع اصلی که ربات رو راه‌اندازی می‌کنه
def main():
    # ساختن Updater با توکن (اینجا ربات شروع به کار می‌کنه)
    updater = Updater(token=TOKEN, use_context=True)

    # گرفتن دیسپچر برای مدیریت فرمان‌ها
    dp = updater.dispatcher

    # ثبت فرمان /start
    dp.add_handler(CommandHandler("start", start))

    # شروع گرفتن پیام‌ها از تلگرام (ربات آنلاین می‌شه)
    updater.start_polling()

    # برنامه تا وقتی متوقف نشه، در حال اجرا می‌مونه
    updater.idle()

# ۴. اگر این فایل مستقیم اجرا بشه، تابع main رو اجرا کن
if __name__ == "__main__":
    main()
