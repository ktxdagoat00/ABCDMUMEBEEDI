import os
import asyncio
from aiohttp import web
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")

if not API_ID or not API_HASH or not STRING_SESSION:
    print("[FATAL] Environment variables missing!")
    exit(1)

try:
    API_ID = int(API_ID)
except ValueError:
    pass

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

# Simple web server to satisfy Render port detection
async def handle_ping(request):
    return web.Response(text="Bot is active and running 24/7!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"[✓] Web server bound on port {port}")

async def main():
    # Start the web server first so Render detects the open port immediately
    await start_web_server()

    # Load plugins if any
    import glob
    import importlib
    from pathlib import Path
    
    files = glob.glob("plugins/*.py")
    for name in files:
        with open(name, "r") as f:
            code = f.read()
        if "def setup(client):" in code:
            mod_name = Path(name).stem
            try:
                module = importlib.import_module(f"plugins.{mod_name}")
                if hasattr(module, "setup"):
                    module.setup(client)
            except Exception as e:
                print(f"[!] Plugin error in {mod_name}: {e}")

    print("[~] Connecting to Telegram...")
    await client.start()
    me = await client.get_me()
    print(f"[✓] Logged in as @{me.username or me.first_name}!")

    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
