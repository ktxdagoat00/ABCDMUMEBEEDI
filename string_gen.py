from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import config

with TelegramClient(StringSession(), config.API_ID, config.API_HASH) as client:
    print("\n" + "="*50)
    print("YOUR STRING SESSION:")
    print("="*50)
    print(client.session.save())
    print("="*50 + "\n")
