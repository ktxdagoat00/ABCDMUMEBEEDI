import os
import sys
import time
import glob
import asyncio
import logging
import importlib
from aiohttp import web
from telethon import TelegramClient, events
from telethon.sessions import StringSession

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
STRING_SESSION = os.environ.get("STRING_SESSION", "").strip()

if not STRING_SESSION or not API_ID:
    print("FATAL: STRING_SESSION ya API_ID missing hai!", flush=True)
    sys.exit(1)

# Force IPv4 to prevent cloud socket freeze
client = TelegramClient(
    StringSession(STRING_SESSION),
    API_ID,
    API_HASH,
    use_ipv6=False,
    connection_retries=5,
    timeout=15
)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.ping$'))
async def ping(event):
    start = time.time()
    msg = await event.edit("🏓 **Pinging...**")
    end = time.time()
    ms = round((end - start) * 1000, 2)
    await msg.edit(f"🔥 **Pong!**\n⚡ Latency: `{ms} ms`")

plugin_files = glob.glob("plugins/*.py")
for file in plugin_files:
    mod_name = file.replace("/", ".").replace(".py", "")
    try:
        mod = importlib.import_module(mod_name)
        if hasattr(mod, "setup"):
            mod.setup(client)
            print(f"Loaded plugin: {mod_name}", flush=True)
    except Exception as e:
        print(f"Plugin load error in {mod_name}: {e}", flush=True)

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
    print(f"==> Web server listening on port {port}", flush=True)

async def main():
    await start_web_server()
    print(">>> Initializing Telegram Client Handshake...", flush=True)
    try:
        await asyncio.wait_for(client.connect(), timeout=25.0)
    except asyncio.TimeoutError:
        print("ERROR: Connection to Telegram timed out!", flush=True)
        return
    except Exception as err:
        print(f"ERROR while connecting: {err}", flush=True)
        return

    if not await client.is_user_authorized():
        print("❌ CRITICAL: String session is not authorized or expired!", flush=True)
        return

    me = await client.get_me()
    print(f"✅ SUCCESS: Connected as {me.first_name} (@{me.username or 'NoUsername'})", flush=True)
    print(">>> 🚀 USERBOT IS LIVE AND LISTENING! <<<", flush=True)
    await client.run_until_disconnected()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
