import os
import logging
import telebot
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- Configuração ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

TOKEN = os.getenv('TELEGRAM_TOKEN')
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
# Rotas do Servidor Flask
# ==============================

# Rota para o Webhook do Telegram
# O Telegram vai enviar TODAS as mensagens para cá
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# Rota principal para verificar se o app está no ar
@app.route('/')
def index():
    return "Servidor do Bot está ativo e funcionando!"

# ==============================
# Funções do Bot do Telegram
# ==============================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    logging.info(f"Comando /start recebido de {message.chat.id}")
    
    # Mensagem divertida de "acordando"
    bot.send_message(message.chat.id, "Opa! Estou terminando uma partida, já venho te atender... 😉")
    
    markup = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton(f"{data['name']} — R${data['price']:.2f}", callback_data=key)
        for key, data in tournaments.items()
    ]
    markup.add(*buttons)
    
    # Envia o menu de botões logo em seguida
    bot.send_message(message.chat.id, "Pronto! Qual torneio você vai querer?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    tournament_key = call.data
    tournament = tournaments.get(tournament_key)
    chat_id = call.message.chat.id
    
    if tournament:
        logging.info(f"Botão '{tournament_key}' clicado por {chat_id}")
        bot.answer_callback_query(call.id) # Apenas confirma o clique
        
        confirmation_text = f"Beleza! Você escolheu o torneio *{tournament['name']}*. O próximo passo é o pagamento!"
        bot.edit_message_text(confirmation_text, chat_id, call.message.message_id, parse_mode='Markdown')
