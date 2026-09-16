import os
import sys
import time
import glob
import asyncio
import importlib
from aiohttp import web
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
STRING_SESSION = os.environ.get("STRING_SESSION", "").strip()

if not API_ID or not API_HASH:
    try:
        import config
        API_ID = config.API_ID
        API_HASH = config.API_HASH
    except Exception:
        print("FATAL: API_ID / API_HASH missing!", flush=True)
        sys.exit(1)

if STRING_SESSION:
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
else:
    client = TelegramClient('userbot_session', API_ID, API_HASH)

for file in glob.glob("plugins/*.py"):
    mod_name = file.replace("/", ".").replace(".py", "")
    try:
        mod = importlib.import_module(mod_name)
        if hasattr(mod, "setup"):
            mod.setup(client)
            print(f"[PLUGIN] Loaded: {mod_name}", flush=True)
    except Exception as e:
        print(f"[PLUGIN ERROR] {mod_name}: {e}", flush=True)

async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def start_web():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"[WEB] Port {port} active", flush=True)

async def start_telegram():
    print("[TG] Connecting client...", flush=True)
    await client.start()
    me = await client.get_me()
    print(f"✅ [SUCCESS] Logged in as: {me.first_name} (@{me.username or 'NoUsername'})", flush=True)
    print(">>> 🚀 BOT IS RUNNING! <<<", flush=True)

async def main():
    await start_web()
    await start_telegram()
    await client.run_until_disconnected()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        pass
