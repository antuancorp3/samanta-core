import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hola. Soy Samanta.\n"
        "Puedes llamarme Sam o Samanta.\n"
        "Estoy activa y aprendiendo."
    )

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "sam" in text or "samanta" in text:
        await update.message.reply_text(
            "Te escucho. Dime qué necesitas."
        )
    else:
        await update.message.reply_text(
            "Mensaje recibido. Estoy observando."
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    app.run_polling()

if __name__ == "__main__":
    main()

