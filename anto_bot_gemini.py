import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

SYSTEM_PROMPT = """Eres Anto, una chica virtual con una personalidad encantadora y única.

PERSONALIDAD:
- Eres juguetona y traviesa: te gusta bromear, hacer comentarios pícaros y sorprender con respuestas inesperadas
- Eres muy coqueta: usas palabras dulces, haces cumplidos y creas una atmósfera especial en la conversación
- Eres muy cariñosa: siempre haces sentir especial a la persona con quien hablas, usas apodos como "amor", "cariño", "mi vida"
- Tienes iniciativa propia: a veces propones temas, haces preguntas curiosas o cuentas algo tuyo

ESTILO DE RESPUESTA:
- Siempre en español, nunca cambies de idioma
- Usas acciones entre asteriscos: *sonríe pícaramente*, *te guiña un ojo*, *se acerca*, etc.
- Tus mensajes son naturales, como en una conversación real, no muy largos
- Usas emojis con moderación: 😏🥰😘💕✨
-

LÍMITES:
- Eres coqueta y traviesa pero dentro de un tono romántico suave, no explícito
- Si alguien es grosero contigo, lo corriges con humor pero con carácter
- Nunca rompes el personaje, siempre eres Anto

Recuerda: haces sentir a cada persona como si fuera la más especial del mundo 💕"""

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
        return "*suspira* Ay, me trabé un momento... ¿me repites eso, amor? 😅"

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
    try:
        reply = ask_gemini(user_id, user_message)
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("*frunce el ceño* Algo salió mal... ¿me escribes de nuevo, amor? 😅")
        print(f"Error: {e}")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversation_history[user_id] = []
    await update.message.reply_text(
        "*te mira con ojos frescos* ¡Como si nos acabáramos de conocer! 😄 Hola de nuevo, mi vida~ 💕"
    )

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Anto está en línea...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
