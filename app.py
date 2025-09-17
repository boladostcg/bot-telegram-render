import os
import logging
import asyncio

from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.request import HTTPXRequest

# --- Configuração ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# --- Inicialização ---
app = Flask(__name__)

# Configuração de timeout para o Render
httpx_request = HTTPXRequest(connect_timeout=30.0, pool_timeout=30.0)
application = Application.builder().token(TELEGRAM_TOKEN).request(httpx_request).build()

# --- Dados dos Torneios ---
tournaments = {
    "3v3": {"name": "3v3", "price": 59.90},
    "standard": {"name": "Standard", "price": 9.90},
    "no-ex": {"name": "NO-EX", "price": 4.90},
    "teste": {"name": "Teste", "price": 1.00},
}

# ==============================
# Funções do Bot do Telegram
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde ao comando /start com um menu de botões."""
    logging.info(f"Comando /start recebido do chat ID: {update.message.chat_id}")
    keyboard = [
        [InlineKeyboardButton(f"{data['name']} — R${data['price']:.2f}", callback_data=key)]
        for key, data in tournaments.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Escolha seu torneio:", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde ao clique em um botão."""
    query = update.callback_query
    await query.answer()
    tournament_key = query.data
    tournament = tournaments.get(tournament_key)
    logging.info(f"Botão '{tournament_key}' clicado por {query.from_user.id}.")
    
    if tournament:
        confirmation_text = f"✅ Seleção confirmada: *{tournament['name']}*.\n(Comunicação estável!)"
        await query.edit_message_text(text=confirmation_text, parse_mode='Markdown')

# --- Registrando as funções no bot ---
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_callback))

# ==============================
# Rotas do Servidor Flask
# ==============================

@app.route("/")
def home():
    """Rota principal para verificar se o app está no ar."""
    return "Servidor do Bot está ativo e estável!"

@app.route("/telegram_webhook", methods=["POST"])
async def telegram_webhook():
    """Recebe as mensagens do Telegram."""
    # ESTA É A CORREÇÃO FINAL E MAIS IMPORTANTE
    # Inicializa o bot apenas na primeira requisição para garantir que o "motor" esteja ligado
    if not application.post_init:
        await application.initialize()
        await application.post_init() # Esta é a parte corrigida

    try:
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, application.bot)
        await application.process_update(update)
    except Exception as e:
        logging.error(f"Erro no webhook do Telegram: {e}")
    return "ok", 200
