import os
import time
import glob
import asyncio
import importlib
from aiohttp import web
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
STRING_SESSION = os.environ.get("STRING_SESSION", "")

if not API_ID:
    import config
    API_ID = config.API_ID
    API_HASH = config.API_HASH
    client = TelegramClient('userbot_session', API_ID, API_HASH)
else:
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

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
    mod = importlib.import_module(mod_name)
    if hasattr(mod, "setup"):
        mod.setup(client)

# Web health check server for Render free tier
async def handle_ping(request):
    return web.Response(text="Userbot is running!")

async def start_web():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await client.start()
    await start_web()
    print(">>> Userbot 24/7 LIVE on Free Web Service!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
