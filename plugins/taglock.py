import re
import asyncio
from telethon import events
from telethon.tl.types import PeerChannel, PeerChat, PeerUser

# target_chat_id: target_message_id
taglock_chats = {}

async def parse_telegram_link(client, link: str):
    link = link.strip()
    
    # Private/Supergroup link: https://t.me/c/1234567890/456
    c_match = re.search(r't\.me/c/(\d+)/(\d+)', link)
    if c_match:
        chat_id = int("-100" + c_match.group(1))
        msg_id = int(c_match.group(2))
        return chat_id, msg_id

    # Public group/channel link: https://t.me/username/456
    pub_match = re.search(r't\.me/([a-zA-Z0-9_]+)/(\d+)', link)
    if pub_match:
        username = pub_match.group(1)
        msg_id = int(pub_match.group(2))
        try:
            entity = await client.get_entity(username)
            return entity.id, msg_id
        except Exception:
            return None, None

    return None, None

def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.taglock(?:\s+(.*))?'))
    async def enable_taglock(event):
        arg = event.pattern_match.group(1)
        reply = await event.get_reply_message()
        target_chat_id = None
        target_msg_id = None

        if reply:
            target_chat_id = event.chat_id
            target_msg_id = reply.id
        elif arg:
            target_chat_id, target_msg_id = await parse_telegram_link(client, arg)

        # Trigger command delete
        await event.delete()

        if target_chat_id and target_msg_id:
            taglock_chats[target_chat_id] = target_msg_id
            alert = await event.respond(
                "```text\n"
                "┌───「 🔒 𝗧𝗔𝗚𝗟𝗢𝗖𝗞 𝗔𝗖𝗧𝗜𝗩𝗔𝗧𝗘𝗗 」\n"
                f"├─ 🎯 𝗖𝗛𝗔𝗧_𝗜𝗗 :: {target_chat_id}\n"
                f"└─ 📌 𝗠𝗦𝗚_𝗜𝗗  :: {target_msg_id}\n"
                "```"
            )
            await asyncio.sleep(0.5)
            await alert.delete()

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.untaglock(?:\s+(.*))?'))
    async def disable_taglock(event):
        arg = event.pattern_match.group(1)
        target_chat_id = event.chat_id

        if arg:
            parsed_chat, _ = await parse_telegram_link(client, arg)
            if parsed_chat:
                target_chat_id = parsed_chat

        await event.delete()

        if target_chat_id in taglock_chats:
            del taglock_chats[target_chat_id]
            alert = await event.respond(
                "```text\n"
                "┌───「 🔓 𝗧𝗔𝗚𝗟𝗢𝗖𝗞 𝗥𝗘𝗟𝗘𝗔𝗦𝗘𝗗 」\n"
                f"└─ ⚡ Chat {target_chat_id} unlocked.\n"
                "```"
            )
            await asyncio.sleep(0.5)
            await alert.delete()

    @client.on(events.NewMessage(outgoing=True))
    async def auto_reply_handler(event):
        text = event.raw_text or ""
        if text.startswith((".", "/", "!")):
            return

        target_id = taglock_chats.get(event.chat_id)
        if not target_id:
            return

        if event.reply_to_msg_id != target_id:
            chat = await event.get_input_chat()
            msg_text = event.text

            await event.delete()
            await client.send_message(chat, msg_text, reply_to=target_id)
