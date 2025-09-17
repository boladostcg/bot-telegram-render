import os
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.request import HTTPXRequest

# --- Configuração ---
TOKEN = os.getenv('TELEGRAM_TOKEN')
app = Flask(__name__)

# Configuração de timeout para aguentar o "acordar" do Render
httpx_request = HTTPXRequest(connect_timeout=40.0, pool_timeout=40.0)
application = Application.builder().token(TOKEN).request(httpx_request).build()

# --- Dados dos Torneios ---
tournaments = {
    "3v3": {"name": "3v3", "price": 59.90},
    "standard": {"name": "Standard", "price": 9.90},
    "no-ex": {"name": "NO-EX", "price": 4.90},
    "teste": {"name": "Teste", "price": 1.00},
}

# ==============================
# Funções do Bot (Handlers)
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde ao comando /start com uma mensagem de espera e o menu."""
    chat_id = update.message.chat_id
    print(f"Comando /start recebido do chat ID: {chat_id}")
    
    # SUA IDEIA EM AÇÃO: Enviando uma mensagem de "acordando" primeiro.
    await context.bot.send_message(chat_id=chat_id, text="Opa! Só um segundo, estou acordando aqui... 🤖")
    
    keyboard = [
        [InlineKeyboardButton(f"{data['name']} — R${data['price']:.2f}", callback_data=key)]
        for key, data in tournaments.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Pronto! Escolha seu torneio:", reply_markup=reply_markup)
    print(f"Menu enviado para {chat_id}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde ao clique no botão."""
    query = update.callback_query
    await query.answer()
    tournament_key = query.data
    tournament = tournaments.get(tournament_key)
    
    if tournament:
        print(f"Botão '{tournament_key}' clicado.")
        confirmation_text = f"✅ Beleza! Você selecionou o torneio *{tournament['name']}*."
        await query.edit_message_text(text=confirmation_text, parse_mode='Markdown')

# --- Registrando Handlers ---
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_callback))

# ==============================
# Rotas do Servidor
# ==============================
@app.route("/telegram_webhook", methods=["POST"])
async def telegram_webhook():
    """Recebe as mensagens do Telegram."""
    # Inicialização "preguiçosa" para garantir que o bot esteja pronto
    if not application.post_init:
        await application.initialize()
        await application.post_init()
        
    update_data = request.get_json(force=True)
    update = Update.de_json(update_data, application.bot)
    await application.process_update(update)
    return "ok", 200

@app.route('/')
def index():
    return "Servidor estável do Bot de Torneios está no ar!"
