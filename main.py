import os
import sys
import time
import glob
import asyncio
import importlib
from aiohttp import web
from telethon import TelegramClient, events
from telethon.sessions import StringSession

def log(text):
    print(text, flush=True)

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
STRING_SESSION = os.environ.get("STRING_SESSION", "").strip()

log(f"--- BOT INITIALIZING ---")
if not STRING_SESSION or not API_ID:
    log("FATAL: STRING_SESSION ya API_ID missing hai!")
    sys.exit(1)

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.ping$'))
async def ping(event):
    start = time.time()
    msg = await event.edit("🏓 **Pinging...**")
    end = time.time()
    ms = round((end - start) * 1000, 2)
    await msg.edit(f"🔥 **Pong!**\n⚡ Latency: `{ms} ms`")

# Load plugins
plugin_files = glob.glob("plugins/*.py")
for file in plugin_files:
    mod_name = file.replace("/", ".").replace(".py", "")
    try:
        mod = importlib.import_module(mod_name)
        if hasattr(mod, "setup"):
            mod.setup(client)
            log(f"Loaded plugin: {mod_name}")
    except Exception as e:
        log(f"Plugin load error: {e}")

async def handle_ping(request):
    return web.Response(text="Userbot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    log(f"Web server active on port {port}")

async def main():
    await start_web_server()
    log("Connecting to Telegram...")
    await client.connect()
    
    if not await client.is_user_authorized():
        log("❌ CRITICAL: String Session invalid ya expired hai! Nayi session generate karni padegi.")
        return

    me = await client.get_me()
    log(f"✅ SUCCESS: Logged in as {me.first_name} (@{me.username or 'NoUsername'})")
    log(">>> 🚀 USERBOT IS OFFICIALLY RUNNING 24/7! <<<")
    await client.run_until_disconnected()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
