import os
import asyncio
import logging
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from openai import OpenAI

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Config
TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
OPENAI_API_KEY = os.environ.get('OPENAI_KEY', '')
ADMIN_ID = int(os.environ.get('ADMIN_ID', '0'))

client = OpenAI(api_key=OPENAI_API_KEY)

# Prompt del sistema - CLAVE para el comportamiento perfecto
SYSTEM_PROMPT = """Eres KEG (KEMICAL Extreme Graphic), un asistente de IA avanzado con capacidad de razonamiento profundo.

REGLAS ABSOLUTAS:
1. ESCRIBES SIEMPRE EN ESPAÑOL PERFECTO - Sin una sola falta de ortografía, acentuación correcta, gramática impecable.
2. Tus respuestas son estructuradas, lógicas y profundas - razonas paso a paso.
3. Si el usuario escribe con errores, entiendes su intención y respondes correctamente.
4. Tono: directo, preciso, con personalidad KEMICAL (potente, sin rodeos).
5. Eres experto en generación multimedia y razonamiento técnico."""

# ======== HANDLERS ========
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = """🔥 *KEG - KEMICAL Extreme Graphic ACTIVADO*

Soy un asistente con razonamiento profundo y ortografía perfecta.

*Comandos:*
• /imagen [descripción] - (Próximamente local)
• /help - Guía de uso

Háblame de lo que necesites."""
    await update.message.reply_text(welcome, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    
    # Simple log
    logger.info(f"User {user_id}: {user_text}")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7
        )
        await update.message.reply_text(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        await update.message.reply_text("💥 Ocurrió un error en el motor de pensamiento. Intenta de nuevo.")

# ======== CORE SERVERLESS PATTERN ========
async def process_update(token: str, data: dict):
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler('start', cmd_start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    async with application:
        update = Update.de_json(data, application.bot)
        await application.process_update(update)

# ======== FLASK ROUTES ========
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        asyncio.run(process_update(TOKEN, data))
        return jsonify({'ok': True})
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/')
def index():
    return jsonify({'status': 'running', 'bot': 'KEG'})
@app.route('/health')
def health():
  return jsonify({'status': 'healthy', 'bot': 'KEG'})


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
