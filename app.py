import os
import logging
import asyncio

from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.request import HTTPXRequest

# --- Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# --- Variáveis de ambiente ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# --- Flask ---
app = Flask(__name__)

# --- Telegram Application ---
httpx_request = HTTPXRequest(connect_timeout=30.0, pool_timeout=30.0)
application = Application.builder().token(TELEGRAM_TOKEN).request(httpx_request).build()

# --- Torneios ---
tournaments = {
    "3v3": {"name": "3v3", "price": 59.90},
    "standard": {"name": "Standard", "price": 9.90},
    "no-ex": {"name": "NO-EX", "price": 4.90},
    "teste": {"name": "Teste", "price": 1.00},
}

# ==============================
# Funções do Bot
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envia mensagem inicial de aguarde e depois mostra os botões."""
    logging.info(f"/start recebido do chat {update.message.chat_id}")

    # Mensagem inicial de "aguarde"
    message = await update.message.reply_text("🎮 Terminando uma partida, já vou te atender...")

    # Agora monta os botões
    keyboard = [
        [InlineKeyboardButton(f"{data['name']} — R${data['price']:.2f}", callback_data=key)]
        for key, data in tournaments.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Edita a mensagem inicial para mostrar os botões
    await asyncio.sleep(2)  # espera 2s só para simular "processando"
    await message.edit_text("Escolha seu torneio:", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde quando o usuário clica em um botão."""
    query = update.callback_query
    await query.answer()
    tournament = tournaments.get(query.data)
    if tournament:
        msg = f"✅ Seleção confirmada: *{tournament['name']}*.\n(Teste OK!)"
        await query.edit_message_text(text=msg, parse_mode="Markdown")

# --- Handlers ---
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_callback))

# ==============================
# Rotas do Servidor Flask
# ==============================

@app.route("/")
def home():
    return "Servidor do Bot está ativo!"

@app.route("/telegram_webhook", methods=["POST"])
async def telegram_webhook():
    try:
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, application.bot)
        await application.process_update(update)
    except Exception as e:
        logging.error(f"Erro no webhook do Telegram: {e}")
    return "ok", 200

# --- Inicialização ---
async def main():
    await application.initialize()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    asyncio.run(main())
    app.run(host="0.0.0.0", port=port)
