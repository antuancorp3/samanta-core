import os
import requests
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Configurar logging para ver errores
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Tokens desde Railway
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

HF_API = "https://api-inference.huggingface.co/models/google/flan-t5-small"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

print(f"TOKEN cargado: {'Sí' if BOT_TOKEN else 'No'}")
print(">>> Iniciando Samanta con Hugging Face integrado <<<")

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hola. Soy Samanta.\n"
        "Puedes llamarme Sam o Samanta.\n"
        "Estoy activa y aprendiendo.\n\n"
        "Usa /ia seguido de tu pregunta para usar el modelo de IA."
    )

# Comando /ia (Hugging Face)
async def ia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = " ".join(context.args) if context.args else ""
    
    if not user_text:
        await update.message.reply_text("Por favor, escribe tu pregunta después de /ia\nEjemplo: /ia ¿Cómo funciona el universo?")
        return
    
    try:
        # Añadir un indicador de que está procesando
        processing_msg = await update.message.reply_text("🤔 Procesando tu pregunta...")
        
        response = requests.post(HF_API, headers=headers, json={"inputs": user_text}, timeout=30)
        
        if response.status_code != 200:
            await processing_msg.edit_text(f"Error en la API: {response.status_code}")
            return
        
        data = response.json()
        
        # Manejar diferentes formatos de respuesta de Hugging Face
        if isinstance(data, list):
            if len(data) > 0:
                if isinstance(data[0], dict) and "generated_text" in data[0]:
                    reply = data[0]["generated_text"]
                elif isinstance(data[0], str):
                    reply = data[0]
                else:
                    reply = str(data[0])
            else:
                reply = "No obtuve respuesta del modelo 😅"
        elif isinstance(data, dict):
            if "generated_text" in data:
                reply = data["generated_text"]
            elif "error" in data:
                reply = f"Error del modelo: {data['error']}"
            else:
                reply = str(data)
        else:
            reply = str(data)
        
        await processing_msg.edit_text(f"🧠 **Respuesta:**\n{reply}")
        
    except requests.exceptions.Timeout:
        await update.message.reply_text("⏰ El modelo tardó demasiado en responder. Intenta con una pregunta más corta.")
    except Exception as e:
        logger.error(f"Error en /ia: {e}")
        await update.message.reply_text(f"❌ Error técnico: {str(e)}")

# Respuesta general a mensajes
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    # Evitar que responda a sus propios mensajes o a comandos
    if update.message.from_user.is_bot:
        return
    
    if "sam" in text or "samanta" in text:
        responses = [
            "Te escucho. Dime qué necesitas.",
            "¡Hola! ¿En qué puedo ayudarte?",
            "Sí, estoy aquí. ¿Qué pasa?",
            "Me llamaste. ¿Qué necesitas?"
        ]
        import random
        await update.message.reply_text(random.choice(responses))
    else:
        # En lugar de responder siempre, puedes optar por no responder
        # o usar el modelo de IA para responder conversaciones normales
        try:
            # Opción 1: No responder a mensajes aleatorios
            # pass
            
            # Opción 2: Usar IA para conversaciones normales
            response = requests.post(HF_API, headers=headers, json={"inputs": text}, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    if "generated_text" in data[0]:
                        reply = data[0]["generated_text"]
                        await update.message.reply_text(reply)
                        return
            
            # Opción 3: Respuesta por defecto
            await update.message.reply_text("No entendí eso. ¿Podrías reformularlo? O usa /ia para preguntarme algo específico.")
            
        except Exception as e:
            logger.error(f"Error en respuesta general: {e}")
            await update.message.reply_text("Ocurrió un error al procesar tu mensaje.")

def main():
    if not BOT_TOKEN:
        raise ValueError("No se encontró TELEGRAM_BOT_TOKEN en variables de entorno")
    
    if not HF_TOKEN:
        print("⚠️ Advertencia: HF_TOKEN no encontrado. El comando /ia no funcionará.")
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Añadir handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ia", ia))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    
    print("🤖 Bot iniciado... Esperando mensajes")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
