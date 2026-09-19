import re
import asyncio
from telethon import events
from telethon.tl.types import MessageEntityMention, MessageEntityMentionName

# Set of user IDs to watch
antitag_users = set()

# Aapke account ke exact identifiers
MY_USERNAMES = ["k3xhv"]
MY_ID = None

async def get_my_id(client):
    global MY_ID
    if MY_ID is None:
        me = await client.get_me()
        MY_ID = me.id
    return MY_ID

async def resolve_target(client, event):
    reply = await event.get_reply_message()
    if reply:
        return reply.sender_id
    
    parts = event.raw_text.split(maxsplit=1)
    if len(parts) > 1:
        target = parts[1].strip()
        if target.isdigit() or (target.startswith("-") and target[1:].isdigit()):
            return int(target)
        try:
            entity = await client.get_entity(target)
            return entity.id
        except Exception:
            return None
    return None

def setup(client):

    # --- .ghost <seconds> <text> ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ghost(?:\s+(\d+))?(?:\s+([\s\S]+))?'))
    async def ghost_message(event):
        sec_arg = event.pattern_match.group(1)
        text_arg = event.pattern_match.group(2)
        reply = await event.get_reply_message()

        try:
            delay = int(sec_arg) if sec_arg else 5
        except ValueError:
            delay = 5

        msg_text = text_arg if text_arg else (reply.raw_text if reply else "")

        if not msg_text and not (reply and reply.media):
            await event.edit("```text\n[!] Usage: .ghost <seconds> <text>\n```")
            return

        chat = await event.get_input_chat()
        await event.delete()

        if reply and not text_arg:
            sent_msg = await client.send_message(chat, reply)
        else:
            sent_msg = await client.send_message(chat, msg_text)

        await asyncio.sleep(delay)
        try:
            await sent_msg.delete()
        except Exception:
            pass

    # --- .antitag <user/reply> ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.antitag(?:\s+(.*))?'))
    async def enable_antitag(event):
        await get_my_id(client)
        target_id = await resolve_target(client, event)
        await event.delete()

        if not target_id:
            alert = await event.respond("```text\n[!] Provide user ID/username or reply to a message.\n```")
            await asyncio.sleep(2)
            await alert.delete()
            return

        antitag_users.add(target_id)
        notice = await event.respond(
            "```text\n"
            "┌───「 🛡️ 𝗔𝗡𝗧𝗜-𝗧𝗔𝗚 𝗘𝗡𝗚𝗔𝗚𝗘𝗗 」\n"
            f"├─ 👤 𝗧𝗔𝗥𝗚𝗘𝗧 :: {target_id}\n"
            "├─ ⚡ 𝗔𝗖𝗧𝗜𝗢𝗡 :: Purge on mention & reply\n"
            "└───「 🔒 𝗞𝗘𝗦𝗛𝗔𝗩-𝗦𝗧𝗘𝗔𝗟𝗧𝗛 」\n"
            "```"
        )
        await asyncio.sleep(2)
        await notice.delete()

    # --- .unantitag <user/reply> ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.unantitag(?:\s+(.*))?'))
    async def disable_antitag(event):
        target_id = await resolve_target(client, event)
        await event.delete()

        if not target_id:
            alert = await event.respond("```text\n[!] Provide user ID/username or reply to a message.\n```")
            await asyncio.sleep(2)
            await alert.delete()
            return

        if target_id in antitag_users:
            antitag_users.remove(target_id)
            notice = await event.respond(
                "```text\n"
                "┌───「 🔓 𝗔𝗡𝗧𝗜-𝗧𝗔𝗚 𝗥𝗘𝗟𝗘𝗔𝗦𝗘𝗗 」\n"
                f"├─ 👤 𝗧𝗔𝗥𝗚𝗘𝗧 :: {target_id}\n"
                "└───「 🕊️ 𝗥𝗘𝗦𝗧𝗥𝗜𝗖𝗧𝗜𝗢𝗡 𝗟𝗜𝗙𝗧𝗘𝗗 」\n"
                "```"
            )
            await asyncio.sleep(2)
            await notice.delete()
        else:
            alert = await event.respond("```text\n[!] User not in Anti-Tag list.\n```")
            await asyncio.sleep(2)
            await alert.delete()

    # --- 100% RELIABLE SCANNER (outgoing=False) ---
    @client.on(events.NewMessage(outgoing=False))
    async def antitag_listener(event):
        if not antitag_users:
            return

        # Check sender ID
        sender_id = event.sender_id
        if not sender_id or sender_id not in antitag_users:
            return

        my_id = await get_my_id(client)
        should_delete = False

        # Raw message text lowercased
        text = (event.raw_text or "").lower()

        # 1. Direct Regex check for @k3xhv (Word boundary check)
        for u in MY_USERNAMES:
            if f"@{u}" in text:
                should_delete = True
                break

        # 2. Telegram entities scan (agar @ mention ya text mention format ho)
        if not should_delete and event.entities:
            for ent in event.entities:
                if isinstance(ent, MessageEntityMentionName) and ent.user_id == my_id:
                    should_delete = True
                    break
                elif isinstance(ent, MessageEntityMention):
                    extracted = text[ent.offset:ent.offset + ent.length].lstrip("@")
                    if extracted in MY_USERNAMES:
                        should_delete = True
                        break

        # 3. Reply check
        if not should_delete and event.is_reply:
            try:
                reply_msg = await event.get_reply_message()
                if reply_msg and reply_msg.sender_id == my_id:
                    should_delete = True
            except Exception:
                pass

        # Execution
        if should_delete:
            try:
                await event.delete()
            except Exception:
                pass
