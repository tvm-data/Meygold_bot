import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

API_URL = "https://www.tgju.org"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات قیمت‌گذاری طلا فعاله. لطفاً یک پست با وزن، اجرت، سود و مالیات بفرست.")

def extract_price_info(text):
    import re
    try:
        weight = float(re.search(r'وزن[:\s]+([\d/.]+)', text).group(1).replace(',', '.'))
        wage = float(re.search(r'اجرت[:\s]+([\d/.]+)', text).group(1).replace(',', '.'))
        profit = float(re.search(r'سود[:\s]+([\d/.]+)', text).group(1).replace(',', '.'))
        tax = float(re.search(r'مالیات[:\s]+([\d/.]+)', text).group(1).replace(',', '.'))
        return weight, wage, profit, tax
    except:
        return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    data = extract_price_info(text)
    if data:
        keyboard = [[InlineKeyboardButton("📌 محاسبه قیمت", callback_data=text)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("برای محاسبه قیمت روی دکمه زیر بزنید:", reply_markup=reply_markup)

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = query.data
    data = extract_price_info(text)
    if not data:
        await query.edit_message_text("❌ خطا در دریافت اطلاعات از متن.")
        return

    weight, wage_percent, profit_percent, tax_percent = data

    try:
        html = requests.get(API_URL).text
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        gold_tag = soup.find("td", string="طلای 18 عیار").find_next("td")
        gold_price = int(gold_tag.text.replace(',', ''))
    except:
        await query.edit_message_text("❌ خطا در دریافت قیمت طلا از سایت.")
        return

    base = gold_price * weight
    wage = base * wage_percent / 100
    profit = (base + wage) * profit_percent / 100
    tax = (base + wage + profit) * tax_percent / 100
    final = base + wage + profit + tax

    msg = f"""
💎 قیمت لحظه‌ای طلای ۱۸ عیار: {gold_price:,} تومان

📦 جزئیات:
وزن: {weight} گرم
اجرت: {wage_percent}٪
سود: {profit_percent}٪
مالیات: {tax_percent}٪

💰 قیمت نهایی: {final:,.0f} تومان
"""
    await query.edit_message_text(msg)

def main():
    token = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_button))

    app.run_polling()

if __name__ == "__main__":
    main()
