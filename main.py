import os
import time
import glob
import importlib
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

print(">>> Userbot LIVE!")
client.start()
client.run_until_disconnected()
