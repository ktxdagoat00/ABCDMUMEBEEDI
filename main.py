import os
import sys
import glob
import asyncio
import logging
import importlib.util
from telethon import TelegramClient
from telethon.sessions import StringSession
from aiohttp import web

# Performance logging
logging.basicConfig(level=logging.WARNING)

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")

if not API_ID or not API_HASH or not SESSION_STRING:
    print("[FATAL] Environment variables missing!")
    sys.exit(1)

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

def load_plugins():
    plugin_files = glob.glob("plugins/*.py")
    for file_path in plugin_files:
        name = os.path.splitext(os.path.basename(file_path))[0]
        if name.startswith("__"):
            continue
        try:
            spec = importlib.util.spec_from_file_location(f"plugins.{name}", file_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "setup"):
                mod.setup(client)
            print(f"[+] Loaded plugin: {name}")
        except Exception as e:
            print(f"[-] Error loading plugin {name}: {e}")

async def health_check(request):
    return web.Response(text="Bot Engine Running 24/7 at Peak Speed!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"[+] Web engine bound to port {port}")

async def main():
    await client.start()
    load_plugins()
    await start_web_server()
    print("[+] Master Userbot Online & Multitasking Active!")
    
    # Auto-Reconnection & Crash Guard Watchdog
    while True:
        try:
            if not client.is_connected():
                print("[!] Reconnecting client...")
                await client.connect()
            await asyncio.sleep(15)
        except Exception as e:
            print(f"[Watchdog Error] {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
