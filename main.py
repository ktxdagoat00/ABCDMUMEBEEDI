import os
import sys
import time
import glob
import asyncio
import importlib
from aiohttp import web
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Flush print immediately
def log(text):
    print(text, flush=True)

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
STRING_SESSION = os.environ.get("STRING_SESSION", "").strip()

log(f"--- BOT INITIALIZING ---")
log(f"API_ID: {'PRESENT' if API_ID else 'EMPTY'}")
log(f"API_HASH: {'PRESENT' if API_HASH else 'EMPTY'}")
log(f"STRING_SESSION: {'PRESENT' if STRING_SESSION else 'EMPTY'}")

if not STRING_SESSION:
    log("FATAL: STRING_SESSION is missing from Environment Variables!")
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
            log(f"Plugin loaded: {mod_name}")
    except Exception as e:
        log(f"Failed to load {mod_name}: {e}")

async def handle_ping(request):
    return web.Response(text="Userbot is running!")

async def start_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    log(f"Web server bound on port {port}")

async def start_bot():
    log("Starting Telethon Client connection...")
    await client.start()
    me = await client.get_me()
    log(f"SUCCESS: Logged in as {me.first_name} (ID: {me.id})")
    log(">>> USERBOT IS NOW FULLY LIVE & READY FOR COMMANDS! <<<")
    await client.run_until_disconnected()

async def main():
    await start_server()
    await start_bot()

if __name__ == "__main__":
    asyncio.run(main())
