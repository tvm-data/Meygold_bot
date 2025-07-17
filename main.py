import os
import re
import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    MessageHandler, CallbackQueryHandler,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@meygold_gallery"  # ← آیدی کانال خودت اینجا بذار

# تابع گرفتن قیمت طلا از مثقال
def get_gold_price():
    try:
        response = requests.get("https://mesghal.ir/")
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", class_="table-price")
        rows = table.find_all("tr")
        for row in rows:
            if "طلا 18 عیار" in row.text:
                price_text = row.find_all("td")[1].text.strip().replace(",", "")
                return int(price_text)
    except Exception as e:
        print("❌ خطا در دریافت قیمت:", e)
        return None

# استخراج اعداد از کپشن پست
def extract_data_from_caption(caption):
    try:
        weight = float(re.search(r"وزن[:\-]?\s*([\d.]+)", caption).group(1))
        wage = float(re.search(r"اجرت[:\-]?\s*([\d.]+)", caption).group(1))
        profit = float(re.search(r"سود[:\-]?\s*([\d.]+)", caption).group(1))
        tax = float(re.search(r"مالیات[:\-]?\s*([\d.]+)", caption).group(1))
        return weight, wage, profit, tax
    except:
        return None

# محاسبه قیمت نهایی
def calculate_price(gold_price, weight, wage, profit, tax):
    base = gold_price * weight
    wage_amount = base * wage / 100
    profit_amount = (base + wage_amount) * profit / 100
    tax_amount = (base + wage_amount + profit_amount) * tax / 100
    final_price = base + wage_amount + profit_amount + tax_amount
    return round(final_price)

# هندل کردن پست جدید در کانال
async def handle_new_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post and update.channel_post.chat.username == CHANNEL_USERNAME[1:]:
        caption = update.channel_post.caption
        if not caption:
            return
        data = extract_data_from_caption(caption)
        if not data:
            return

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 محاسبه قیمت", callback_data=f"calc_{update.channel_post.message_id}")]
        ])
        await context.bot.edit_message_reply_markup(
            chat_id=update.channel_post.chat.id,
            message_id=update.channel_post.message_id,
            reply_markup=keyboard
        )

# وقتی دکمه «محاسبه قیمت» زده میشه
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    msg = await context.bot.get_chat(CHANNEL_USERNAME).get_message(int(query.data.split("_")[1]))
    caption = msg.caption
    data = extract_data_from_caption(caption)
    if not data:
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("❌ خطا در استخراج اطلاعات از کپشن!")
        return

    weight, wage, profit, tax = data
    gold_price = get_gold_price()
    if not gold_price:
        await query.message.reply_text("❌ خطا در دریافت قیمت طلا.")
        return

    final = calculate_price(gold_price, weight, wage, profit, tax)

    text = (
        f"📊 **محاسبه قیمت نهایی:**\n"
        f"وزن: {weight} گرم\n"
        f"اجرت: {wage}%\n"
        f"سود: {profit}%\n"
        f"مالیات: {tax}%\n"
        f"قیمت لحظه‌ای طلا: {gold_price:,} تومان\n\n"
        f"💰 **قیمت نهایی:** {final:,.0f} تومان"
    )

    await query.message.reply_text(text, parse_mode="Markdown")

# شروع ربات
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.Chat(username=CHANNEL_USERNAME) & filters.UpdateType.CHANNEL_POST, handle_new_post))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
