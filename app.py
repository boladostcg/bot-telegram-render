import os
import telebot
from flask import Flask, request

# --- Configuração ---
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
print("--> Bot e Flask (versão síncrona) inicializados.")

# --- Dados dos Torneios ---
tournaments = {
    "3v3": {"name": "3v3", "price": 59.90},
    "standard": {"name": "Standard", "price": 9.90},
    "no-ex": {"name": "NO-EX", "price": 4.90},
    "teste": {"name": "Teste", "price": 1.00},
}

# ==============================
# Rota do Webhook
# ==============================
@app.route('/webhook', methods=['POST'])
def webhook():
    print("--> Rota /webhook foi chamada!")
    try:
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    except Exception as e:
        print(f"--> ERRO no webhook: {e}")
        return "Erro", 500

# ==============================
# Funções do Bot (Handlers)
# ==============================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    print(f"--> Handler @start foi acionado para o chat: {message.chat.id}")
    
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        telebot.types.InlineKeyboardButton(f"{data['name']} — R${data['price']:.2f}", callback_data=key)
        for key, data in tournaments.items()
    ]
    markup.add(*buttons)
    
    bot.reply_to(message, "Escolha seu torneio:", reply_markup=markup)
    print(f"--> Menu enviado para: {message.chat.id}")

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    print(f"--> Handler de botão foi acionado para a escolha: {call.data}")
    tournament_key = call.data
    tournament = tournaments.get(tournament_key)
    
    if tournament:
        bot.answer_callback_query(call.id)
        
        confirmation_text = f"Beleza! Você escolheu o torneio *{tournament['name']}*."
        bot.edit_message_text(
            confirmation_text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )

# Rota para checar se o servidor está no ar
@app.route('/')
def index():
    return "Servidor do Bot está ativo!"
