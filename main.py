import os
import asyncio
from aiohttp import web
from telethon import TelegramClient
from telethon.sessions import StringSession

# Load environment credentials
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")

if not API_ID or not API_HASH:
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("API_ID="):
                    API_ID = line.split("=", 1)[1].strip("'\" \n")
                elif line.startswith("API_HASH="):
                    API_HASH = line.split("=", 1)[1].strip("'\" \n")

if API_ID:
    API_ID = int(API_ID)

# Collect all available string sessions from environment (.env or Render env vars)
sessions = []
# Session 1
s1 = os.environ.get("STRING_SESSION") or os.environ.get("SESSION_1")
if s1: sessions.append(s1)

# Session 2
s2 = os.environ.get("STRING_SESSION_2") or os.environ.get("SESSION_2")
if s2: sessions.append(s2)

# Session 3
s3 = os.environ.get("STRING_SESSION_3") or os.environ.get("SESSION_3")
if s3: sessions.append(s3)

print(f"[✓] Loaded {len(sessions)} active Telegram session(s).")

clients = []
if s1: clients.append(TelegramClient(StringSession(s1), API_ID, API_HASH))
if s2: clients.append(TelegramClient(StringSession(s2), API_ID, API_HASH))
if s3: clients.append(TelegramClient(StringSession(s3), API_ID, API_HASH))

# Load plugins dynamically for all active clients
import glob
import importlib
from pathlib import Path

def load_plugins_for_client(client):
    path = "plugins/*.py"
    files = glob.glob(path)
    for name in files:
        with open(name, "r") as f:
            code = f.read()
        # Avoid syntax errors or empty plugins
        if "def setup(client):" in code:
            mod_name = Path(name).stem
            try:
                module = importlib.import_module(f"plugins.{mod_name}")
                if hasattr(module, "setup"):
                    module.setup(client)
            except Exception as e:
                print(f"[!] Error loading plugin {mod_name}: {e}")

# Simple web server to satisfy Render port binding requirement
async def handle_ping(request):
    return web.Response(text="Bot running at high speed 24/7!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"[✓] Web server bound successfully on port {port}")

async def main():
    if not clients:
        print("[!] Error: No sessions found! Please set STRING_SESSION in environment or .env")
        return

    # Start all clients and load plugins
    for client in clients:
        load_plugins_for_client(client)
        await client.start()
        print(f"[✓] Client connected successfully!")

    # Start background keep-alive web server
    await start_web_server()

    # Run all clients concurrently until disconnected
    await asyncio.gather(*(client.run_until_disconnected() for client in clients))

if __name__ == "__main__":
    asyncio.run(main())
