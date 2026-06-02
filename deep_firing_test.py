import asyncio
import aiohttp
import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ========== CONFIG ==========
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8800743229:AAFYR1yzQ2lMpjvxDmDFqvMnbQDuqpFUvVA")
COOKIE_DIR = "saved_cookies"
os.makedirs(COOKIE_DIR, exist_ok=True)

# In-memory storage for one-time IDs
pending_ids = []

# ========== COOKIE HELPERS ==========
def save_cookie(nickname: str, data):
    """data can be a dict (parsed JSON) or a raw string."""
    filepath = os.path.join(COOKIE_DIR, f"{nickname}.json")
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def load_cookie(nickname: str):
    filepath = os.path.join(COOKIE_DIR, f"{nickname}.json")
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r") as f:
        return json.load(f)

def list_cookies():
    files = [f[:-5] for f in os.listdir(COOKIE_DIR) if f.endswith(".json")]
    return files

def cookie_to_header(cookie_data):
    """Convert saved cookie data to a Cookie header string."""
    if isinstance(cookie_data, dict):
        # Assume it's a list of cookies like [{"name": "...", "value": "..."}]
        if isinstance(cookie_data, list) and all("name" in c and "value" in c for c in cookie_data):
            return "; ".join(f"{c['name']}={c['value']}" for c in cookie_data)
        # Or a simple dict {name: value}
        return "; ".join(f"{k}={v}" for k, v in cookie_data.items())
    else:
        # Raw cookie string
        return str(cookie_data)

# ========== API REQUEST ==========
BASE_URL = "https://www.indiageniuschallenge.com/api"

async def fire_anon_id(session, anon_id, cookie_header):
    """Send one link request for a single anon ID."""
    url = f"{BASE_URL}/attempt/linkAnon"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.indiageniuschallenge.com/quiz",
        "Cookie": cookie_header,
    }
    # The API expects the anon ID as a query param? From earlier code it was in cookie.
    # But the working version used: GET /attempt/linkAnon with cookie anon_attempt_id=<id>
    # Actually the original code sent a GET with anon_attempt_id in the cookie.
    # We'll replicate that: put anon_id into the Cookie header as well.
    # However, the endpoint might also accept ?anonId=... 
    # Let's use the method from the original bot: set cookie "anon_attempt_id" to the ID.
    # But we already have a cookie from the user. We need to add/override that cookie.
    # Simpler: send the request with the user's cookie AND add the anon_attempt_id cookie.
    # We'll construct a combined cookie string.
    combined_cookie = f"{cookie_header}; anon_attempt_id={anon_id}"
    headers["Cookie"] = combined_cookie

    try:
        async with session.get(url, headers=headers) as resp:
            text = await resp.text()
            return {"id": anon_id, "status": resp.status, "response": text[:200]}
    except Exception as e:
        return {"id": anon_id, "status": "error", "response": str(e)}

async def fire_all_ids(anon_ids, cookie_header):
    """Fire all IDs concurrently without any delay."""
    async with aiohttp.ClientSession() as session:
        tasks = [fire_anon_id(session, aid, cookie_header) for aid in anon_ids]
        results = await asyncio.gather(*tasks)
    return results

# ========== TELEGRAM HANDLERS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎯 *India Genius Challenge Link Bot*\n\n"
        "• `/savecookie <nick>` – save cookie (send text or .json file)\n"
        "• `/listcookies` – show saved nicknames\n"
        "• `/setids <id1> <id2> …` – store anon IDs (one‑time)\n"
        "• `/play <nick>` – fire all stored IDs against that cookie\n"
        "• `/test <id1> <id2> …` – test fire with dummy cookie\n\n"
        "_All requests are sent truly simultaneously._",
        parse_mode="Markdown"
    )

async def savecookie_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/savecookie <nickname>` then send the cookie content.")
        return
    nickname = context.args[0]
    context.user_data["awaiting_cookie"] = nickname
    await update.message.reply_text(f"Send the cookie for `{nickname}` as text or upload a `.json` file.", parse_mode="Markdown")

async def handle_cookie_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nickname = context.user_data.pop("awaiting_cookie", None)
    if not nickname:
        return
    # Check if it's a document (JSON file)
    if update.message.document and update.message.document.file_name.endswith(".json"):
        file = await update.message.document.get_file()
        data = await file.download_as_bytearray()
        try:
            cookie_data = json.loads(data.decode())
            save_cookie(nickname, cookie_data)
            await update.message.reply_text(f"✅ Cookie saved as `{nickname}` (JSON file).", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ Invalid JSON: {e}")
    else:
        # Treat as raw cookie string
        cookie_text = update.message.text
        if not cookie_text:
            await update.message.reply_text("Please send a non‑empty cookie string.")
            return
        save_cookie(nickname, cookie_text)
        await update.message.reply_text(f"✅ Cookie saved as `{nickname}` (text).", parse_mode="Markdown")

async def listcookies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cookies = list_cookies()
    if not cookies:
        await update.message.reply_text("No saved cookies.")
    else:
        await update.message.reply_text("Saved cookies:\n" + "\n".join(f"• `{c}`" for c in cookies), parse_mode="Markdown")

async def setids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_ids
    if not context.args:
        await update.message.reply_text("Usage: `/setids <anon_id1> <anon_id2> …`", parse_mode="Markdown")
        return
    pending_ids = context.args
    await update.message.reply_text(f"✅ Stored {len(pending_ids)} ID(s) for next `/play`.", parse_mode="Markdown")

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_ids
    if not pending_ids:
        await update.message.reply_text("No IDs stored. Use `/setids` first.")
        return
    if not context.args:
        await update.message.reply_text("Usage: `/play <nickname>`", parse_mode="Markdown")
        return
    nickname = context.args[0]
    cookie_data = load_cookie(nickname)
    if not cookie_data:
        await update.message.reply_text(f"❌ Cookie `{nickname}` not found.", parse_mode="Markdown")
        return

    cookie_header = cookie_to_header(cookie_data)
    msg = await update.message.reply_text(f"🚀 Firing {len(pending_ids)} ID(s) against `{nickname}`...", parse_mode="Markdown")

    results = await fire_all_ids(pending_ids, cookie_header)

    # Build result text
    lines = [f"*Results for {nickname}*:"]
    for r in results:
        status_icon = "✅" if r["status"] == 200 else "❌"
        lines.append(f"{status_icon} `{r['id']}` → HTTP {r['status']}")
    lines.append("\n_IDs cleared after this command._")
    await msg.edit_text("\n".join(lines), parse_mode="Markdown")

    # Clear the stored IDs after play
    pending_ids = []

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/test <anon_id1> <anon_id2> …`", parse_mode="Markdown")
        return
    test_ids = context.args
    # Use a dummy cookie (or no real cookie)
    dummy_cookie = "test=1"
    await update.message.reply_text(f"🔍 Testing {len(test_ids)} ID(s) with dummy cookie...", parse_mode="Markdown")
    results = await fire_all_ids(test_ids, dummy_cookie)
    lines = ["*Test results (dummy cookie)*:"]
    for r in results:
        status_icon = "✅" if r["status"] == 200 else "❌"
        lines.append(f"{status_icon} `{r['id']}` → HTTP {r['status']}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

# ========== MAIN ==========
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("savecookie", savecookie_cmd))
    app.add_handler(CommandHandler("listcookies", listcookies))
    app.add_handler(CommandHandler("setids", setids))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("test", test))
    app.add_handler(MessageHandler(filters.TEXT | filters.Document.ALL, handle_cookie_message))

    print("Bot started. Polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
