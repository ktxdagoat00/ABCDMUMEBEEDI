from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import config

client = TelegramClient('userbot_session', config.API_ID, config.API_HASH)
client.start()
s = StringSession.save(client.session)
client.send_message('me', s)
print("\nDONE: Saved Messages me bhej diya gaya hai!")
