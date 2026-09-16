import re
import asyncio
from telethon import events

# chat_id: target_message_id
taglock_chats = {}

def extract_msg_id_from_link(link: str):
    # Telegram links: https://t.me/c/1234567890/456 or https://t.me/username/456
    match = re.search(r'/(\d+)$', link.strip())
    if match:
        return int(match.group(1))
    return None

def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.taglock(?:\s+(.*))?'))
    async def enable_taglock(event):
        arg = event.pattern_match.group(1)
        reply = await event.get_reply_message()
        target_msg_id = None

        if reply:
            target_msg_id = reply.id
        elif arg:
            target_msg_id = extract_msg_id_from_link(arg)

        # Command trigger turant delete karo taaki kisi ko pata na chale
        await event.delete()

        if target_msg_id:
            taglock_chats[event.chat_id] = target_msg_id
            alert = await event.respond(
                "```text\n"
                "┌───「 🔒 𝗧𝗔𝗚𝗟𝗢𝗖𝗞 𝗔𝗖𝗧𝗜𝗩𝗔𝗧𝗘𝗗 」\n"
                f"└─ 🎯 𝗧𝗔𝗥𝗚𝗘𝗧 :: {target_msg_id}\n"
                "```"
            )
            await asyncio.sleep(0.5)
            await alert.delete()

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.untaglock$'))
    async def disable_taglock(event):
        await event.delete()
        if event.chat_id in taglock_chats:
            del taglock_chats[event.chat_id]
            alert = await event.respond(
                "```text\n"
                "┌───「 🔓 𝗧𝗔𝗚𝗟𝗢𝗖𝗞 𝗥𝗘𝗟𝗘𝗔𝗦𝗘𝗗 」\n"
                "└─ ⚡ Auto-reply disabled.\n"
                "```"
            )
            await asyncio.sleep(0.5)
            await alert.delete()

    @client.on(events.NewMessage(outgoing=True))
    async def auto_reply_handler(event):
        # Ignore commands
        text = event.raw_text or ""
        if text.startswith((".", "/", "!")):
            return

        target_id = taglock_chats.get(event.chat_id)
        if not target_id:
            return

        # Agar message pehle se hi target message par replied nahi hai
        if event.reply_to_msg_id != target_id:
            chat = await event.get_input_chat()
            msg_text = event.text

            # Purana plain msg delete karke target par as a reply bhej do
            await event.delete()
            await client.send_message(chat, msg_text, reply_to=target_id)
