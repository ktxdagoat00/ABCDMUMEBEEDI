import asyncio
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import config

with TelegramClient(StringSession(), config.API_ID, config.API_HASH) as client:
    session_str = client.session.save()
    client.send_message("me", f"🔐 **YOUR STRING SESSION (DO NOT SHARE):**\n\n`{session_str}`")
    print("\n✅ Session successfully aapke Telegram Saved Messages me bhej diya gaya hai!")
