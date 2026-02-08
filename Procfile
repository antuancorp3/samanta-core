worker: python bot.py
import os, requests, telebot

# Token de Telegram desde variables de Railway
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Token de Hugging Face (IA de texto)
HF_TOKEN = os.getenv("HF_TOKEN")
HF_API = "https://api-inference.huggingface.co/models/google/flan-t5-small"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "¡Hola! Tu bot ya está vivo en Railway 🚀")

# Nuevo comando para usar IA de texto
@bot.message_handler(commands=['ia'])
def ia(message):
    user_text = message.text.replace("/ia", "").strip()
    response = requests.post(HF_API, headers=headers, json={"inputs": user_text})
    data = response.json()
    if isinstance(data, list) and "generated_text" in data[0]:
        reply = data[0]["generated_text"]
    else:
        reply = "No pude generar respuesta 😅"
    bot.reply_to(message, reply)

# Handler general (eco)
@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.reply_to(message, f"Me dijiste: {message.text}")

print("Bot iniciado...")
bot.polling()
