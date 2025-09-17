import os
import telebot
from flask import Flask, request

# --- Configuração ---
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
print("--> Bot de Teste 'OI' v2 (send_message) inicializado.")

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
# Handler Mínimo (Pega TUDO)
# ==============================
@bot.message_handler(func=lambda message: True)
def send_oi(message):
    chat_id = message.chat.id
    print(f"--> Tentando enviar 'oi' para o chat ID: {chat_id}")
    try:
        # MUDANÇA: Usando send_message em vez de reply_to
        bot.send_message(chat_id, "oi")
        print(f"--> 'oi' enviado com sucesso.")
    except Exception as e:
        print(f"--> ERRO AO TENTAR ENVIAR 'oi': {e}")

# Rota para checar se o servidor está no ar
@app.route('/')
def index():
    return "Servidor de teste 'OI' v2 está ativo!"
