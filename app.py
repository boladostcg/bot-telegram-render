import os
import logging
import asyncio

from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.request import HTTPXRequest

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# --- Initialization ---
app = Flask(__name__)

# Timeout configuration for Render
httpx_request = HTTPXRequest(connect_timeout=30.0, pool_timeout=30.0)
application = Application.builder().token(TELEGRAM_TOKEN).request(httpx_request).build()

# --- Tournament Data ---
tournaments = {
    "3v3": {"name": "3v3", "price": 59.90},
    "standard": {"name": "Standard", "price": 9.90},
    "no-ex": {"name": "NO-EX", "price": 4.90},
    "teste": {"name": "Teste", "price": 1.00},
}

# ==============================
# Telegram Bot Functions
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responds to the /start command with a button menu."""
    logging.info(f"Received /start command from chat ID: {update.message.chat_id}")
    keyboard = [
        [InlineKeyboardButton(f"{data['name']} — R${data['price']:.2f}", callback_data=key)]
        for key, data in tournaments.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose your tournament:", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responds to a button click."""
    query = update.callback_query
    await query.answer()
    tournament_key = query.data
    tournament = tournaments.get(tournament_key)
    logging.info(f"Button '{tournament_key}' clicked by {query.from_user.id}.")
    
    if tournament:
        confirmation_text = f"✅ Selection confirmed: *{tournament['name']}*.\n(Stable communication!)"
        await query.edit_message_text(text=confirmation_text, parse_mode='Markdown')

# --- Registering functions with the bot ---
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_callback))

# ==============================
# Flask Server Routes
# ==============================

@app.route("/")
def home():
    """Main route to check if the app is live."""
    return "Bot server is active and stable!"

@app.route("/telegram_webhook", methods=["POST"])
async def telegram_webhook():
    """Receives messages from Telegram."""
    # THIS IS THE FINAL AND MOST IMPORTANT FIX
    # Initialize the bot only on the first request to ensure the "engine" is on
    if not application.post_init:
        await application.initialize()
        await application.post_init() # This is the corrected part

    try:
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, application.bot)
        await application.process_update(update)
    except Exception as e:
        logging.error(f"Error in Telegram webhook: {e}")
    return "ok", 200
