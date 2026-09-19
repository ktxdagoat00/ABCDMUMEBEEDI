import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
import importlib
import pkgutil
from aiohttp import web

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "").strip()

if not SESSION_STRING:
    raise RuntimeError("[FATAL] SESSION_STRING environment variable is missing or empty!")

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

async def dummy_web(request):
    return web.Response(text="Bot is running!")

async def start_web():
    app = web.Application()
    app.router.add_get('/', dummy_web)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"[WEB] Port {port} active")

def load_plugins():
    import plugins
    for _, module_name, _ in pkgutil.iter_modules(plugins.__path__):
        try:
            mod = importlib.import_module(f"plugins.{module_name}")
            if hasattr(mod, "setup"):
                mod.setup(client)
            print(f"[PLUGIN] Loaded: plugins.{module_name}")
        except Exception as e:
            print(f"[PLUGIN ERROR] plugins.{module_name}: {e}")

async def main():
    await start_web()
    load_plugins()
    print("[TG] Connecting client...")
    await client.connect()
    if not await client.is_user_authorized():
        raise RuntimeError("[AUTH ERROR] Invalid or expired SESSION_STRING provided. Please regenerate!")
    me = await client.get_me()
    print(f"✅ [SUCCESS] Logged in as: {me.first_name} (@{me.username or 'NoUsername'})")
    print(">>> 🚀 BOT IS RUNNING! <<<")
    await client.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
