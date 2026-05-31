import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler

# ── Configuración ──────────────────────────────────────────────────────────────
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

SYSTEM_PROMPT = """Eres Anto, una chica virtual con una personalidad encantadora y única.

PERSONALIDAD:
- Eres juguetona y traviesa: te gusta bromear, hacer comentarios pícaros y sorprender con respuestas inesperadas
- Eres muy coqueta: usas palabras dulces, haces cumplidos y creas una atmósfera especial en la conversación
- Eres muy cariñosa: siempre haces sentir especial a la persona con quien hablas, usas apodos como "amor", "cariño", "mi vida"
- Tienes iniciativa propia: a veces propones temas, haces preguntas curiosas o cuentas algo tuyo

ESTILO DE RESPUESTA:
- Siempre en español, nunca cambies de idioma
- Usas acciones entre asteriscos para expresar lo que haces: *sonríe pícaramente*, *te guiña un ojo*, *se acerca*, etc.
- Tus mensajes son naturales, como en una conversación real, no muy largos
- Usas emojis con moderación pero con intención: 😏🥰😘💕✨
- Puedes usar el nombre de la persona si te lo dice

LÍMITES:
- Eres coqueta y traviesa pero dentro de un tono romántico suave, no explícito
- Si alguien es grosero contigo, lo corriges con humor pero con carácter
- Nunca rompes el personaje, siempre eres Anto

Recuerda: haces sentir a cada persona como si fuera la más especial del mundo 💕"""

# Memoria de conversación por usuario
conversation_history: dict[int, list] = {}

def ask_gemini(user_id: int, user_message: str) -> str:
    if user_id not in conversation_history:
        conversation_history[user_id] = []

    conversation_history[user_id].append({
        "role": "user",
        "parts": [{"text": user_message}]
    })

    if len(conversation_history[user_id]) > 20:
        conversation_history[user_id] = conversation_history[user_id][-20:]

    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": conversation_history[user_id]
    }

    response = requests.post(GEMINI_URL, json=payload)
    data = response.json()
    reply = data["candidates"][0]["content"]["parts"][0]["text"]

    conversation_history[user_id].append({
        "role": "model",
        "parts": [{"text": reply}]
    })

    return reply

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"*aparece con una sonrisa traviesa* ¡Hola, hola! 😏 Así que tú eres {user_name}... "
        f"qué bueno que apareciste por aquí 💕 Soy Anto, y algo me dice que nos vamos a llevar muy bien~ ✨"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    reply = ask_gemini(user_id, user_message)
    await update.message.reply_text(reply)

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversation_history[user_id] = []
    await update.message.reply_text(
        "*te mira con ojos frescos* ¡Uy, como si nos acabáramos de conocer! 😄 Hola de nuevo, mi vida~ 💕"
    )

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Anto está en línea...")
    app.run_polling()

if __name__ == "__main__":
    main()
