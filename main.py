import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://keg-kemical-bot.vercel.app/webhook")

app = Flask(__name__)

_ptb = None

def get_ptb():
    global _ptb
    if _ptb is None:
        _ptb = Application.builder().token(BOT_TOKEN).build()
        _ptb.add_handler(CommandHandler("start", start))
        _ptb.add_handler(CommandHandler("alerta", alerta_command))
        _ptb.add_handler(CallbackQueryHandler(button_handler))
        _ptb.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    return _ptb

# -- TEXTS --

WELCOME = (
    "\U0001f5a4 *KEMICAL ADDICTION* \U0001f5a4\n"
    "_Tu universo de moda urbana, streetwear y cultura_\n\n"
    "Bienvenid@ a la experiencia mas raw y autentica del underground fashion.\n\n"
    "Elige una opcion:"
)

CATALOGO = (
    "\U0001f6cd *CATALOGO KEMICAL*\n\n"
    "\U0001f525 *Streetwear* - Tees, hoodies, cargos y mas piezas con actitud.\n\n"
    "\U0001f451 *Accesorios* - Gorras, bags, cadenas, cinturones statement.\n\n"
    "\U0001f45f *Footwear* - Colabs exclusivos y drops limitados.\n\n"
    "\U0001f4e6 *Drops Especiales* - Ediciones limitadas solo para la comunidad.\n\n"
    "Visita: https://kemicaladdiction.com"
)

DROPS = (
    "\u26a1 *PROXIMOS DROPS*\n\n"
    "\U0001f4cc *KEMICAL x UNDERGROUND* - Pronto\n"
    "Una coleccion nacida en las calles, para los que viven el juego.\n\n"
    "\U0001f4cc *DARK SEASON VOL.2* - En camino\n"
    "Paleta oscura, cortes oversize, energia pura.\n\n"
    "\U0001f514 Activa alertas: /alerta"
)

COMUNIDAD = (
    "\U0001f30d *LA COMUNIDAD KEMICAL*\n\n"
    "Somos mas que una marca. Somos un movimiento.\n\n"
    "\U0001f4f1 Instagram: @kemicaladdiction\n"
    "\U0001f3b5 TikTok: @kemicaladdiction\n"
    "\U0001f4e2 Canal: t.me/kemicaladdictionoficial\n\n"
    "Comparte tu look con *#KEMICAL* y aparezcas en nuestro feed.\n"
    "La calle es la pasarela."
)

COLABS = (
    "\U0001f91d *COLABORACIONES*\n\n"
    "\U0001f3a8 Para artistas y creadores:\n"
    "Tu vision + la estetica Kemical = algo unico.\n\n"
    "\U0001f4f8 Para influencers y content creators:\n"
    "Programa de embajadores activo.\n\n"
    "\U0001f4e7 collabs@kemicaladdiction.com"
)

CONTACTO = (
    "\U0001f4ac *CONTACTO DIRECTO*\n\n"
    "\u2753 Preguntas sobre pedidos, tallas o envios:\n"
    "Escribe aqui y te respondemos.\n\n"
    "\U0001f4e7 info@kemicaladdiction.com\n"
    "\U0001f4f1 IG: @kemicaladdiction\n\n"
    "Horario: Lun-Vie 10am-7pm (AST)"
)

ALERTA = (
    "\U0001f514 *ALERTAS DE DROPS ACTIVADAS*\n\n"
    "Ahora eres parte del inner circle Kemical.\n"
    "Seras el primero en saber cuando caigan nuevas piezas.\n\n"
    "\U0001f5a4 #KEMICAL"
)

# -- KEYBOARDS --

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("\U0001f6cd Catalogo", callback_data="catalogo"),
         InlineKeyboardButton("\u26a1 Drops", callback_data="drops")],
        [InlineKeyboardButton("\U0001f30d Comunidad", callback_data="comunidad"),
         InlineKeyboardButton("\U0001f91d Colaboraciones", callback_data="colabs")],
        [InlineKeyboardButton("\U0001f4ac Contacto", callback_data="contacto"),
         InlineKeyboardButton("\U0001f514 Alertas", callback_data="alerta")],
    ])

def back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("\u2190 Menu Principal", callback_data="menu")]
    ])

# -- HANDLERS --

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        WELCOME, parse_mode="Markdown", reply_markup=main_keyboard()
    )

async def alerta_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        ALERTA, parse_mode="Markdown", reply_markup=back_keyboard()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    texts = {
        "menu": WELCOME,
        "catalogo": CATALOGO,
        "drops": DROPS,
        "comunidad": COMUNIDAD,
        "colabs": COLABS,
        "contacto": CONTACTO,
        "alerta": ALERTA,
    }
    keyboard = main_keyboard() if data == "menu" else back_keyboard()
    await query.edit_message_text(
        text=texts.get(data, WELCOME), parse_mode="Markdown", reply_markup=keyboard
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.lower()
    if any(w in msg for w in ["hola", "hello", "hi", "hey", "buenas"]):
        await update.message.reply_text(
            "\U0001f5a4 Que hay! Bienvenid@ a Kemical Addiction.\nUsa el menu:",
            reply_markup=main_keyboard()
        )
    elif any(w in msg for w in ["precio", "costo", "cuanto", "price"]):
        await update.message.reply_text(
            "\U0001f4b0 Los precios varian segun la pieza y el drop.\nRevisa el catalogo:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("\U0001f6cd Ver Catalogo", callback_data="catalogo")
            ]])
        )
    elif any(w in msg for w in ["envio", "shipping", "enviar", "deliver"]):
        await update.message.reply_text(
            "\U0001f69a *ENVIOS*\n\n"
            "\U0001f1f5\U0001f1f7 Puerto Rico: 2-3 dias\n"
            "\U0001f1fa\U0001f1f8 EEUU: 4-7 dias\n"
            "\U0001f310 Internacional: Consultar\n\n"
            "info@kemicaladdiction.com",
            parse_mode="Markdown",
            reply_markup=back_keyboard()
        )
    else:
        await update.message.reply_text(
            "\U0001f5a4 Gracias por escribir. Explora el menu:",
            reply_markup=main_keyboard()
        )

# -- FLASK ROUTES --

@app.route("/", methods=["GET"])
def index():
    return "\U0001f5a4 Kemical Addiction Bot LIVE", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    ptb = get_ptb()
    data = request.get_json(force=True)
    update = Update.de_json(data, ptb.bot)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(ptb.process_update(update))
    loop.close()
    return "ok", 200

@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    ptb = get_ptb()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(ptb.bot.set_webhook(url=WEBHOOK_URL))
    loop.close()
    return f"Webhook set to {WEBHOOK_URL}", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))