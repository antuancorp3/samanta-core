import os
import requests
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import subprocess

# Configurar logging para ver errores
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Obtener tokens desde variables de entorno
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

# Reemplaza con TU ID de Telegram (obténlo de @userinfobot)
YOUR_TELEGRAM_ID = 123456789  # ⚠️ CAMBIA ESTO

# Verificar tokens
print("🔧 Verificando configuración...")
print(f"Bot Token: {'✅' if BOT_TOKEN else '❌ No encontrado'}")
print(f"HF Token: {'✅' if HF_TOKEN else '❌ No encontrado'}")

# APIs gratuitas de Hugging Face
APIS = {
    "chat": {
        "url": "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
        "token": HF_TOKEN
    },
    "code": {
        "url": "https://api-inference.huggingface.co/models/microsoft/CodeGPT-small-py",
        "token": HF_TOKEN
    },
    "image": {
        "url": "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1",
        "token": HF_TOKEN
    }
}

class MultiAIAssistant:
    def __init__(self):
        self.conversation_history = []
    
    async def ask_huggingface(self, api_type, prompt):
        """Preguntar a cualquier API de Hugging Face"""
        if api_type not in APIS:
            return "❌ Tipo de API no válido"
        
        api = APIS[api_type]
        headers = {"Authorization": f"Bearer {api['token']}"}
        
        try:
            # Preparar prompt según el tipo
            if api_type == "chat":
                formatted_prompt = f"<s>[INST] Eres Samanta, un asistente personal útil. Responde: {prompt} [/INST]"
                data = {"inputs": formatted_prompt, "parameters": {"max_length": 300}}
            elif api_type == "code":
                formatted_prompt = f"# {prompt}\n# Escribe el código:\n"
                data = {"inputs": formatted_prompt, "parameters": {"max_length": 400}}
            elif api_type == "image":
                data = {"inputs": prompt}
            
            # Enviar solicitud
            response = requests.post(api['url'], headers=headers, json=data, timeout=60)
            
            if response.status_code != 200:
                return f"❌ Error API: {response.status_code}"
            
            result = response.json()
            
            # Procesar respuesta según el formato
            if api_type == "image":
                # Guardar imagen temporalmente
                with open("temp_image.jpg", "wb") as f:
                    f.write(response.content)
                return "temp_image.jpg"  # Retorna nombre del archivo
            
            elif isinstance(result, list):
                if api_type == "chat":
                    text = result[0].get('generated_text', str(result[0]))
                    # Extraer solo la respuesta
                    if '[/INST]' in text:
                        text = text.split('[/INST]')[-1].strip()
                    return text[:2000]  # Limitar para Telegram
                elif api_type == "code":
                    return f"```python\n{result[0].get('generated_text', str(result[0]))}\n```"
            
            return str(result)
            
        except Exception as e:
            logger.error(f"Error en {api_type}: {e}")
            return f"❌ Error: {str(e)}"

# Inicializar asistente
assistant = MultiAIAssistant()

# ========== HANDLERS DE TELEGRAM ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    welcome = """
🤖 *ASISTENTE PERSONAL MULTI-IA*

*Comandos disponibles:*
/chat [mensaje] - Conversación con IA
/code [descripción] - Generar código Python
/image [descripción] - Generar imagen
/help - Ver esta ayuda

*Ejemplos:*
/chat ¿Cómo aprender Python?
/code función para ordenar lista
/image paisaje montañoso al atardecer

*Privacidad:* Solo tú puedes usar este bot.
"""
    await update.message.reply_text(welcome, parse_mode='Markdown')

async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /chat"""
    # Verificar que eres tú
    if update.effective_user.id != YOUR_TELEGRAM_ID:
        await update.message.reply_text("⛔ Acceso restringido")
        return
    
    if not context.args:
        await update.message.reply_text("📝 Escribe: /chat [tu mensaje]")
        return
    
    prompt = " ".join(context.args)
    msg = await update.message.reply_text("💭 Pensando...")
    
    response = await assistant.ask_huggingface("chat", prompt)
    await msg.edit_text(response)

async def code_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /code"""
    if update.effective_user.id != YOUR_TELEGRAM_ID:
        await update.message.reply_text("⛔ Acceso restringido")
        return
    
    if not context.args:
        await update.message.reply_text("💻 Escribe: /code [descripción del código]")
        return
    
    prompt = " ".join(context.args)
    msg = await update.message.reply_text("🖥️ Generando código...")
    
    response = await assistant.ask_huggingface("code", prompt)
    await msg.edit_text(response)

async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /image"""
    if update.effective_user.id != YOUR_TELEGRAM_ID:
        await update.message.reply_text("⛔ Acceso restringido")
        return
    
    if not context.args:
        await update.message.reply_text("🎨 Escribe: /image [descripción de la imagen]")
        return
    
    prompt = " ".join(context.args)
    msg = await update.message.reply_text("🎨 Creando imagen...")
    
    image_path = await assistant.ask_huggingface("image", prompt)
    
    if image_path and os.path.exists(image_path):
        with open(image_path, 'rb') as photo:
            await update.message.reply_photo(photo, caption=f"🖼️ {prompt}")
        os.remove(image_path)  # Limpiar
        await msg.delete()
    else:
        await msg.edit_text("❌ No pude generar la imagen")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help"""
    await start(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mensajes normales - solo responder si mencionan al bot"""
    if update.effective_user.id != YOUR_TELEGRAM_ID:
        return
    
    text = update.message.text.lower()
    
    # Solo responder si mencionan al bot
    if any(word in text for word in ["samanta", "sam", "bot", "asistente"]):
        prompt = update.message.text
        msg = await update.message.reply_text("💭 Pensando...")
        response = await assistant.ask_huggingface("chat", prompt)
        await msg.edit_text(response)

def main():
    """Función principal"""
    print("🚀 Iniciando Asistente Personal...")
    
    if not BOT_TOKEN:
        print("❌ ERROR: No hay BOT_TOKEN")
        print("💡 Solución: Crea archivo .env con TELEGRAM_BOT_TOKEN=tu_token")
        return
    
    # Crear aplicación de Telegram
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Registrar comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("chat", chat_command))
    app.add_handler(CommandHandler("code", code_command))
    app.add_handler(CommandHandler("image", image_command))
    app.add_handler(CommandHandler("help", help_command))
    
    # Mensajes normales
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot configurado correctamente")
    print("📱 Envíale /start a tu bot en Telegram")
    print("🔒 Solo responderá a tu ID:", YOUR_TELEGRAM_ID)
    
    # Iniciar bot
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
