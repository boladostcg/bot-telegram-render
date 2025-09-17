import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.request import HTTPXRequest

# --- Configurações do Bot ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("❌ Variável de ambiente TELEGRAM_TOKEN não encontrada!")

app = Flask(__name__)

# Configuração de timeout para aguentar o "acordar" do Render
httpx_request = HTTPXRequest(connect_timeout=40.0, pool_timeout=40.0)
application = Application.builder().token(TELEGRAM_TOKEN).request(httpx_request).build()

# --- Handlers do Telegram ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start mostra os torneios disponíveis"""
    chat_id = update.message.chat_id
    print(f"Comando /start recebido de {chat_id}")

    await context.bot.send_message(chat_id=chat_id, text="Processando... só um segundo. 🤖")

    keyboard = [
        [InlineKeyboardButton("3v3 — R$59,90", callback_data="3v3")],
        [InlineKeyboardButton("Standard — R$9,90", callback_data="standard")],
        [InlineKeyboardButton("NO-EX — R$4,90", callback_data="noex")],
        [InlineKeyboardButton("Teste — R$1,00", callback_data="teste")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Escolha seu torneio:", reply_markup=reply_markup)
    print(f"Menu enviado para {chat_id}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com o clique no botão."""
    query = update.callback_query
    await query.answer()
    tournament_key = query.data
    print(f"Botão '{tournament_key}' clicado.")
    await query.edit_message_text(
        text=f"✅ Seleção confirmada: *{tournament_key}*.",
        parse_mode='Markdown'
    )

# Registrando os Handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_callback))

# --- Rotas Flask ---
@app.route("/")
def home():
    return "🤖 Bot BoladosTCG está rodando no Render!"

@app.route("/telegram_webhook", methods=["POST"])
async def telegram_webhook():
    """Recebe updates do Telegram via webhook"""
    try:
        if not application.post_init:
            await application.initialize()
            await application.post_init()

        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.process_update(update)
        return "ok"
    except Exception as e:
        print(f"❌ Erro no webhook: {e}")
        return "erro", 500
