import os
import requests
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Configurar logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Tokens
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

# Modelo de Hugging Face (más conversacional)
HF_API = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-small"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

print(f"TOKEN cargado: {'Sí' if BOT_TOKEN else 'No'}")
print(">>> Iniciando Samanta <<<")

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hola, soy Samanta 🤖\n"
        "Usa /ia <tu pregunta> para hablar con la IA\n"
        "O simplemente dime 'Samanta' para una conversación básica."
    )

# Comando /ia - SOLO para preguntas directas
async def ia_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Escribe algo después de /ia\nEjemplo: /ia ¿Qué es la inteligencia artificial?")
        return
    
    user_text = " ".join(context.args)
    
    try:
        processing_msg = await update.message.reply_text("🤔 Pensando...")
        
        # Configurar prompt para evitar repeticiones
        prompt = f"Responde a esto como asistente: {user_text}"
        
        response = requests.post(
            HF_API, 
            headers=headers, 
            json={
                "inputs": prompt,
                "parameters": {
                    "max_length": 150,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }, 
            timeout=30
        )
        
        if response.status_code != 200:
            await processing_msg.edit_text(f"Error {response.status_code}. Intenta de nuevo.")
            return
        
        data = response.json()
        
        # Extraer respuesta del modelo
        reply = "No pude generar una respuesta."
        if isinstance(data, list) and len(data) > 0:
            if isinstance(data[0], dict):
                if "generated_text" in data[0]:
                    reply = data[0]["generated_text"].strip()
                elif "response" in data[0]:
                    reply = data[0]["response"].strip()
            elif isinstance(data[0], str):
                reply = data[0].strip()
        
        # Limpiar la respuesta si es muy similar al input
        if reply.lower().startswith(user_text.lower()[:20]):
            # Si la respuesta empieza igual que la pregunta, cortarla
            reply = reply[len(user_text):].strip()
        
        if not reply or len(reply) < 2:
            reply = "Recibí tu mensaje pero no pude generar una respuesta significativa."
        
        await processing_msg.edit_text(f"🧠 **Respuesta:**\n{reply}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Error de conexión. Intenta más tarde.")

# Handler para mensajes NORMALES - SOLO responde a saludos/menciones
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()
    
    # NO usar IA para mensajes generales - solo respuestas predefinidas
    if any(word in text for word in ["hola", "hello", "hi", "buenos días", "buenas"]):
        await update.message.reply_text("¡Hola! 👋 ¿Cómo estás?")
    
    elif "sam" in text or "samanta" in text:
        responses = [
            "¿Sí? Dime en qué puedo ayudarte.",
            "¡Aquí estoy! ¿Qué necesitas?",
            "Te escucho, ¿qué pasa?",
            "Hola, soy Samanta. ¿En qué puedo asistirte?"
        ]
        import random
        await update.message.reply_text(random.choice(responses))
    
    elif any(word in text for word in ["cómo estás", "qué tal", "como estas"]):
        await update.message.reply_text("¡Estoy bien, gracias por preguntar! ¿Y tú?")
    
    elif any(word in text for word in ["adiós", "bye", "chao", "nos vemos"]):
        await update.message.reply_text("¡Adiós! 👋 Fue un gusto hablar contigo.")
    
    elif "gracias" in text:
        await update.message.reply_text("¡De nada! 😊")
    
    else:
        # Para otros mensajes, NO RESPONDER automáticamente
        # O puedes dar una sugerencia
        await update.message.reply_text(
            "No estoy segura de cómo responder a eso.\n"
            "Puedes:\n"
            "1. Saludarme o mencionar mi nombre\n"
            "2. Usar /ia seguido de tu pregunta\n"
            "3. Preguntarme algo específico"
        )

def main():
    if not BOT_TOKEN:
        raise ValueError("❌ No se encontró TELEGRAM_BOT_TOKEN")
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ia", ia_command))
    
    # IMPORTANTE: Solo responder a mensajes de texto que NO sean comandos
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot iniciado correctamente")
    print("📝 Comandos disponibles: /start, /ia")
    print("💬 El bot SOLO responderá a saludos o cuando digas 'Samanta'")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
