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

if not API_ID or not STRING_SESSION:
    print("FATAL: API_ID or STRING_SESSION is missing!", flush=True)
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
    print(f"[WEB] Bound to port {port}", flush=True)

async def start_telegram():
    print("[TG] Connecting client...", flush=True)
    await client.connect()
    authorized = await client.is_user_authorized()
    if not authorized:
        print("❌ [TG ERROR] Session string invalid ya expire ho chuki hai!", flush=True)
        return
    me = await client.get_me()
    print(f"✅ [TG SUCCESS] Logged in as: {me.first_name} (@{me.username})", flush=True)
    print(">>> BOT READY HAI: Telegram me .ping bhejo! <<<", flush=True)

async def main():
    await start_web()
    asyncio.create_task(start_telegram())
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        pass
