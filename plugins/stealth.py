import asyncio
from telethon import events
from telethon.tl.types import MessageEntityMention, MessageEntityMentionName

# Target user IDs jinka mention/reply delete karna hai
# Format: set of user_ids
antitag_users = set()

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

        # Agar delay diya hai aur text bacha hai
        msg_text = text_arg if text_arg else (reply.raw_text if reply else "")

        if not msg_text and not (reply and reply.media):
            await event.edit("```text\n[!] Usage: .ghost <seconds> <text>\n```")
            return

        chat = await event.get_input_chat()
        await event.delete()

        # Target message bhejo
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
            "├─ ⚡ 𝗔𝗖𝗧𝗜𝗢𝗡 :: Auto-purge on mention/reply\n"
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

    # --- LISTENER: Auto-delete target's reply or mention ---
    @client.on(events.NewMessage(incoming=True))
    async def antitag_listener(event):
        if not antitag_users:
            return

        sender_id = event.sender_id
        if sender_id not in antitag_users:
            return

        me = await client.get_me()
        should_delete = False

        # Check 1: Reply to me?
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            if reply_msg and reply_msg.sender_id == me.id:
                should_delete = True

        # Check 2: Mention me?
        if not should_delete and event.entities:
            text = event.raw_text or ""
            my_username = me.username.lower() if me.username else None

            for entity in event.entities:
                # Text mention with user ID
                if isinstance(entity, MessageEntityMentionName) and entity.user_id == me.id:
                    should_delete = True
                    break
                # @username mention
                elif isinstance(entity, MessageEntityMention) and my_username:
                    mention_text = text[entity.offset:entity.offset + entity.length].lower()
                    if mention_text == f"@{my_username}":
                        should_delete = True
                        break

        if should_delete:
            try:
                await event.delete()
            except Exception:
                pass
