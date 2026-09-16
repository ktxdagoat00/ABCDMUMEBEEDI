import re
import asyncio
from telethon import events
from telethon.utils import get_peer_id

taglock_chats = {}
is_redirecting = set()

def normalize_id(chat_id):
    s = str(chat_id)
    if s.startswith("-100"):
        return int(s[4:])
    elif s.startswith("-"):
        return int(s[1:])
    return int(s)

async def parse_telegram_link(client, link: str):
    link = link.strip()
    
    # Private / Supergroup: https://t.me/c/1234567890/456
    c_match = re.search(r't\.me/c/(\d+)/(\d+)', link)
    if c_match:
        return normalize_id(c_match.group(1)), int(c_match.group(2))

    # Public: https://t.me/username/456
    pub_match = re.search(r't\.me/([a-zA-Z0-9_]+)/(\d+)', link)
    if pub_match:
        try:
            entity = await client.get_entity(pub_match.group(1))
            return normalize_id(entity.id), int(pub_match.group(2))
        except Exception:
            return None, None

    return None, None

def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.taglock(?:\s+(.*))?'))
    async def enable_taglock(event):
        arg = event.pattern_match.group(1)
        reply = await event.get_reply_message()
        target_chat_raw = None
        target_msg_id = None

        if reply:
            target_chat_raw = normalize_id(event.chat_id)
            target_msg_id = reply.id
        elif arg:
            target_chat_raw, target_msg_id = await parse_telegram_link(client, arg)

        await event.delete()

        if target_chat_raw and target_msg_id:
            taglock_chats[target_chat_raw] = target_msg_id
            alert = await event.respond(
                "```text\n"
                "┌───「 🔒 𝗧𝗔𝗚𝗟𝗢𝗖𝗞 𝗔𝗖𝗧𝗜𝗩𝗔𝗧𝗘𝗗 」\n"
                f"├─ 🎯 𝗖𝗛𝗔𝗧 :: {target_chat_raw}\n"
                f"└─ 📌 𝗠𝗦𝗚  :: {target_msg_id}\n"
                "```"
            )
            await asyncio.sleep(0.5)
            await alert.delete()

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.untaglock(?:\s+(.*))?'))
    async def disable_taglock(event):
        arg = event.pattern_match.group(1)
        target_chat_raw = normalize_id(event.chat_id)

        if arg:
            parsed_chat, _ = await parse_telegram_link(client, arg)
            if parsed_chat:
                target_chat_raw = parsed_chat

        await event.delete()

        if target_chat_raw in taglock_chats:
            del taglock_chats[target_chat_raw]
            alert = await event.respond(
                "```text\n"
                "┌───「 🔓 𝗧𝗔𝗚𝗟𝗢𝗖𝗞 𝗥𝗘𝗟𝗘𝗔𝗦𝗘𝗗 」\n"
                f"└─ ⚡ Chat unlocked.\n"
                "```"
            )
            await asyncio.sleep(0.5)
            await alert.delete()

    @client.on(events.NewMessage(outgoing=True))
    async def auto_reply_handler(event):
        msg_text = event.raw_text or ""
        if msg_text.startswith((".", "/", "!")):
            return

        chat_normalized = normalize_id(event.chat_id)
        target_id = taglock_chats.get(chat_normalized)

        if not target_id:
            return

        # Self-loop protection: bot ke apne redirect kiye hue message ko dobara pakadne se rokna
        if event.id in is_redirecting:
            is_redirecting.remove(event.id)
            return

        # Agar message pehle se hi lock msg pe reply nahi hai
        if event.reply_to_msg_id != target_id:
            chat = await event.get_input_chat()
            content = event.message

            # Delete original message
            await event.delete()

            # Target msg par as a reply bhej do
            sent = await client.send_message(
                chat,
                content.text or "",
                file=content.media,
                reply_to=target_id
            )
            is_redirecting.add(sent.id)
