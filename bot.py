import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Tokens desde Railway
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

HF_API = "https://api-inference.huggingface.co/models/google/flan-t5-small"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hola. Soy Samanta.\n"
        "Puedes llamarme Sam o Samanta.\n"
        "Estoy activa y aprendiendo."
    )

# Nuevo comando /ia (Hugging Face)
async def ia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.replace("/ia", "").strip()
    response = requests.post(HF_API, headers=headers, json={"inputs": user_text})
    data = response.json()
    if isinstance(data, list) and "generated_text" in data[0]:
        reply = data[0]["generated_text"]
    else:
        reply = "No pude generar respuesta 😅"
    await update.message.reply_text(reply)

# Respuesta general
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "sam" in text or "samanta" in text:
        await update.message.reply_text("Te escucho. Dime qué necesitas.")
    else:
        await update.message.reply_text("Mensaje recibido. Estoy observando.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ia", ia))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    app.run_polling()

if __name__ == "__main__":
    main()
