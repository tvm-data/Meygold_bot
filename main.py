import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
import requests
from bs4 import BeautifulSoup

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@meygoldchannel"  # ← آیدی کانالت (با @)

async def extract_price():
    try:
        response = requests.get("https://www.tgju.org/profile/geram18")
        soup = BeautifulSoup(response.text, "html.parser")
        price_div = soup.find("td", {"class": "nf", "data-col-seq": "2"})
        if price_div:
            return int(price_div.text.replace(",", ""))
    except Exception as e:
        print("❌ خطا در دریافت قیمت:", e)
    return None

def parse_caption(text):
    try:
        weight = float(re.search(r"وزن[:\-–\s]*([\d./]+)", text).group(1).replace("/", "."))
        wage = float(re.search(r"اجرت[:\-–\s]*([\d.]+)", text).group(1))
        profit = float(re.search(r"سود[:\-–\s]*([\d.]+)", text).group(1))
        tax = float(re.search(r"مالیات[:\-–\s]*([\d.]+)", text).group(1))
        return weight, wage, profit, tax
    except Exception as e:
        print("❌ خطا در خواندن متن:", e)
        return None

async def handle_new_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post and update.channel_post.caption:
        data = parse_caption(update.channel_post.caption)
        if data:
            button = InlineKeyboardMarkup([
                [InlineKeyboardButton("📌 محاسبه قیمت", callback_data=f"calc:{update.channel_post.message_id}")]
            ])
            await context.bot.edit_message_reply_markup(
                chat_id=update.channel_post.chat_id,
                message_id=update.channel_post.message_id,
                reply_markup=button
            )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    message = query.message
    data = parse_caption(message.caption or "")
    if not data:
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("❌ خطا در خواندن اطلاعات.")
        return

    weight, wage, profit, tax = data
    gold_price = await extract_price()
    if not gold_price:
        await query.message.reply_text("❌ خطا در دریافت قیمت لحظه‌ای.")
        return

    base = gold_price * weight
    wage_amount = base * wage / 100
    profit_amount = (base + wage_amount) * profit / 100
    tax_amount = (base + wage_amount + profit_amount) * tax / 100
    total = base + wage_amount + profit_amount + tax_amount

    msg = (
        f"🔹 وزن: {weight} گرم\n"
        f"🔸 قیمت لحظه‌ای: {gold_price:,.0f} تومان\n\n"
        f"💰 قیمت نهایی: {total:,.0f} تومان"
    )
    await query.message.reply_text(msg)

async def start_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_new_post))
    app.add_handler(CallbackQueryHandler(handle_button))
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(start_bot())
