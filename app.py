import os
import logging
import telebot
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- Configuração ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

TOKEN = os.getenv('TELEGRAM_TOKEN')
APP_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}" # Pega a URL do Render automaticamente

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

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

# Lida com o comando /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    logging.info(f"Comando /start recebido de {message.chat.id}")
    markup = InlineKeyboardMarkup(row_width=1)
    
    buttons = [
        InlineKeyboardButton(f"{data['name']} — R${data['price']:.2f}", callback_data=key)
        for key, data in tournaments.items()
    ]
    markup.add(*buttons)
    
    bot.send_message(message.chat.id, "Escolha seu torneio:", reply_markup=markup)

# Lida com o clique nos botões
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    tournament_key = call.data
    tournament = tournaments.get(tournament_key)
    chat_id = call.message.chat.id
    
    if tournament:
        logging.info(f"Botão '{tournament_key}' clicado por {chat_id}")
        
        # Sua ideia é excelente! Vamos avisar o usuário.
        bot.answer_callback_query(call.id, f"Processando sua escolha: {tournament['name']}")
        
        # Simula um "despertar" e prepara para o próximo passo
        confirmation_text = f"✅ Seleção confirmada: *{tournament['name']}*.\n\nPronto para gerar o pagamento!"
        bot.edit_message_text(confirmation_text, chat_id, call.message.message_id, parse_mode='Markdown')

# ==============================
# Rotas do Servidor Flask
# ==============================

@app.route("/")
def home():
    return "Servidor do Bot está ativo com pyTelegramBotAPI!"

# Configura o webhook quando o servidor inicia
@app.route(f'/{TOKEN}', methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# Esta função é chamada uma vez quando o app inicia no Render
if __name__ != "__main__":
    bot.remove_webhook()
    # Espera um pouco para garantir que o app está no ar antes de configurar o webhook
    import time
    time.sleep(0.5)
    bot.set_webhook(url=f"{APP_URL}/{TOKEN}")
    logging.info(f"Webhook configurado para: {APP_URL}/{TOKEN}")
