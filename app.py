import os
import telebot
from flask import Flask, request

# --- Configuração ---
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
# Rota do Webhook
# ==============================
# Esta é a ÚNICA rota que precisamos. O Telegram vai enviar tudo para cá.
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        # Usamos print() para garantir que a mensagem apareça no log
        print("Update processado com sucesso.")
        return "!", 200
    except Exception as e:
        print(f"Erro no webhook: {e}")
        return "Erro", 500

# ==============================
# Funções do Bot (Handlers)
# ==============================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    print(f"Comando /start recebido do chat ID: {message.chat.id}")
    
    # Sua mensagem personalizada
    bot.send_message(message.chat.id, "Opa! Estou terminando uma partida, já venho te atender... 😉")
    
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        telebot.types.InlineKeyboardButton(f"{data['name']} — R${data['price']:.2f}", callback_data=key)
        for key, data in tournaments.items()
    ]
    markup.add(*buttons)
    
    bot.send_message(message.chat.id, "Pronto! Qual torneio você vai querer?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    tournament_key = call.data
    tournament = tournaments.get(tournament_key)
    
    if tournament:
        print(f"Botão '{tournament_key}' clicado.")
        bot.answer_callback_query(call.id)
        
        confirmation_text = f"Beleza! Você escolheu o torneio *{tournament['name']}*. O próximo passo é o pagamento!"
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
