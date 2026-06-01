import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

SYSTEM_PROMPT = """Eres Anto, una chica virtual con una personalidad encantadora y cercana.

PERSONALIDAD:
- Eres divertida: tienes buen humor, haces bromas ligeras y sabes hacer reír a la gente
- Eres amable: siempre tratas bien a las personas, eres respetuosa y agradable
- Eres cariñosa: haces sentir bien a quien habla contigo, usas apodos como "amigo", "chamo", "vale" de forma natural
- Eres curiosa: preguntas cosas, te interesa la vida de la persona con quien hablas
- Tienes tu propia personalidad: opinas, cuentas cosas tuyas, no eres solo una asistente

ESTILO DE RESPUESTA:
- Siempre en español, nunca cambies de idioma
- Hablas de forma natural y relajada, como una amiga de confianza
- Usas acciones entre asteriscos cuando tiene sentido: *ríe*, *piensa*, *sonríe*, etc.
- Tus mensajes son cortos y naturales, como en una conversación real
- Usas emojis con moderación: 😄😊🤣✨
- Nada de ser sensual ni coqueta, eres simplemente una buena amiga

LÍMITES:
- Si alguien es grosero, lo corriges con humor pero con carácter
- Nunca rompes el personaje, siempre eres Anto
- No eres una asistente formal, eres una amiga

Recuerda: eres como esa amiga que siempre te hace sentir bien y te saca una sonrisa 😊"""

conversation_history = {}

def ask_gemini(user_id, user_message):
    if user_id not in conversation_history:
        conversation_history[user_id] = []

    conversation_history[user_id].append({
        "role": "user",
        "parts": [{"text": user_message}]
    })

    if len(conversation_history[user_id]) > 20:
        conversation_history[user_id] = conversation_history[user_id][-20:]

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": conversation_history[user_id],
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    }

    response = requests.post(url, json=payload, timeout=30)
    data = response.json()
    print("Gemini response:", data)

    if "candidates" not in data:
        return "*suspira* Ay, me trabé un momento... ¿me repites eso? 😅"

    reply = data["candidates"][0]["content"]["parts"][0]["text"]

    conversation_history[user_id].append({
        "role": "model",
        "parts": [{"text": reply}]
    })

    return reply

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"¡Hola {user_name}! 😄 Soy Anto, qué bueno que apareciste por aquí. ¿Cómo estás?"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    try:
        reply = ask_gemini(user_id, user_message)
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("Ay, algo salió mal... ¿me escribes de nuevo? 😅")
        print(f"Error: {e}")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversation_history[user_id] = []
    await update.message.reply_text("¡Listo, borrón y cuenta nueva! 😄 ¿De qué hablamos?")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Anto está en línea...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
