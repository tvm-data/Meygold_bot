import os
import re
import requests
from bs4 import BeautifulSoup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN") or "توکن رباتت اینجا بذار"

# --- تابع استخراج قیمت لحظه‌ای طلا از سایت مثقال
def get_gold_price():
    url = "https://www.mesghal.ir"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    try:
        gold_element = soup.find("span", string=re.compile("طلا 18 عیار"))
        price_tag = gold_element.find_next("span")
        price_text = price_tag.text.strip().replace(",", "")
        return int(price_text)
    except Exception as e:
        print("❌ خطا در دریافت قیمت:", e)
        return None

# --- استخراج داده از کپشن
def extract_values(text):
    try:
        weight = float(re.search(r"وزن[:\- ]?([۰-۹0-9/.]+)", text).group(1).replace("٫", ".").replace("،", "."))
        wage = float(re.search(r"اجرت[:\- ]?([۰-۹0-9/.]+)", text).group(1).replace("٫", "."))
        profit = float(re.search(r"سود[:\- ]?([۰-۹0-9/.]+)", text).group(1).replace("٫", "."))
        tax = float(re.search(r"مالیات[:\- ]?([۰-۹0-9/.]+)", text).group(1).replace("٫", "."))
        return weight, wage, profit, tax
    except Exception as e:
        print("❌ خطا در استخراج داده:", e)
        return None

# --- وقتی کاربر دکمه قیمت رو فشار بده
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not query.message.caption:
        await query.edit_message_text("❌ خطا: توضیحات (caption) یافت نشد.")
        return

    values = extract_values(query.message.caption)
    if not values:
        await query.edit_message_text("❌ خطا در استخراج وزن یا اجرت یا سود یا مالیات.")
        return

    weight, wage, profit, tax = values
    gold_price = get_gold_price()

    if not gold_price:
        await query.edit_message_text("❌ خطا در دریافت قیمت لحظه‌ای طلا.")
        return

    base = gold_price * weight
    wage_amt = base * wage / 100
    profit_amt = (base + wage_amt) * profit / 100
    tax_amt = (base + wage_amt + profit_amt) * tax / 100
    total = base + wage_amt + profit_amt + tax_amt

    msg = f"""💎 قیمت نهایی:
وزن: {weight} گرم
قیمت طلا: {gold_price:,} تومان

اجرت: {wage}٪
سود: {profit}٪
مالیات: {tax}٪

💰 قیمت نهایی: {int(total):,} تومان"""
    await query.edit_message_text(msg)

# --- وقتی کاربر پست بفرسته
async def handle_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.caption:
        keyboard = [[InlineKeyboardButton("📌 محاسبه قیمت", callback_data="calc")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("برای مشاهده قیمت نهایی، دکمه زیر را بزنید 👇", reply_markup=reply_markup)

# --- استارت ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات آماده است. پست‌هایی که شامل وزن، اجرت، سود و مالیات باشن رو همراه دکمه قیمت‌گذاری می‌کنم.")

# --- اجرای ربات
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.PHOTO & filters.Caption(True), handle_post))

    print("🤖 ربات فعال شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
