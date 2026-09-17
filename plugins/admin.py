import asyncio
from telethon import events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

locked_users = {}
locked_chats = set()

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True
)

UNBANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=False,
    send_messages=False,
    send_media=False,
    send_stickers=False,
    send_gifs=False,
    send_games=False,
    send_inline=False,
    embed_links=False
)

async def extract_target_user(event, client):
    reply = await event.get_reply_message()
    if reply:
        parts = event.raw_text.split(maxsplit=1)
        reason = parts[1] if len(parts) > 1 else ""
        return reply.sender_id, reason
    
    parts = event.raw_text.split(maxsplit=2)
    if len(parts) > 1:
        target = parts[1]
        reason = parts[2] if len(parts) > 2 else ""
        if target.isdigit() or (target.startswith("-") and target[1:].isdigit()):
            return int(target), reason
        try:
            entity = await client.get_entity(target)
            return entity.id, reason
        except Exception:
            return None, ""
    return None, ""

def setup(client):

    # --- BAN COMMAND ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ban(?:\s+(.*))?'))
    async def ban_user(event):
        chat = await event.get_input_chat()
        target_id, reason = await extract_target_user(event, client)
        
        if not target_id:
            await event.edit("```text\n[!] Reply to user or provide ID/Username\n```")
            return

        reason_text = reason if reason else "No reason specified"
        
        try:
            target_entity = await client.get_input_entity(target_id)
            await client(EditBannedRequest(chat, target_entity, BANNED_RIGHTS))
            
            card = (
                "```text\n"
                "┌───「 🚫 𝗨𝗦𝗘𝗥 𝗘𝗫𝗘𝗖𝗨𝗧𝗜𝗢𝗡 ⚡ 」\n"
                "│\n"
                f"├─ 👤 𝗧𝗔𝗥𝗚𝗘𝗧 :: {target_id}\n"
                f"├─ 📝 𝗥𝗘𝗔𝗦𝗢𝗡 :: {reason_text}\n"
                "├─ 🛡️ 𝗔𝗖𝗧𝗜𝗢𝗡 :: Banned from Network\n"
                "│\n"
                "└───「 💀 𝗣𝗨𝗥𝗚𝗘𝗗 𝗕𝗬 𝗞𝗘𝗦𝗛𝗔𝗩 」\n"
                "```"
            )
            await event.edit(card)
        except Exception as e:
            await event.edit(f"```text\n[!] Ban Failed: {e}\n```")

    # --- UNBAN COMMAND ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.unban(?:\s+(.*))?'))
    async def unban_user(event):
        chat = await event.get_input_chat()
        target_id, _ = await extract_target_user(event, client)

        if not target_id:
            await event.edit("```text\n[!] Reply to user or provide ID/Username\n```")
            return

        try:
            target_entity = await client.get_input_entity(target_id)
            await client(EditBannedRequest(chat, target_entity, UNBANNED_RIGHTS))

            card = (
                "```text\n"
                "┌───「 🔓 𝗨𝗦𝗘𝗥 𝗣𝗔𝗥𝗗𝗢𝗡𝗘𝗗 ⚡ 」\n"
                "│\n"
                f"├─ 👤 𝗧𝗔𝗥𝗚𝗘𝗧 :: {target_id}\n"
                "├─ 🛡️ 𝗔𝗖𝗧𝗜𝗢𝗡 :: Unbanned / Restrictions Lifted\n"
                "│\n"
                "└───「 🕊️ 𝗞𝗘𝗦𝗛𝗔𝗩-𝗦𝗘𝗖𝗨𝗥𝗜𝗧𝗬 」\n"
                "```"
            )
            await event.edit(card)
        except Exception as e:
            await event.edit(f"```text\n[!] Unban Failed: {e}\n```")

    # --- USER LOCK / UNLOCK ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.lock(?:\s+(.*))?'))
    async def lock_user(event):
        target_id, _ = await extract_target_user(event, client)
        if not target_id:
            await event.edit("```text\n[!] Reply to user or provide username/ID\n```")
            return

        chat_id = event.chat_id
        if chat_id not in locked_users:
            locked_users[chat_id] = set()
        
        locked_users[chat_id].add(target_id)
        card = (
            "```text\n"
            "┌───「 🔒 𝗨𝗦𝗘𝗥 𝗟𝗢𝗖𝗞𝗘𝗗 ⚡ 」\n"
            "│\n"
            f"├─ 👤 𝗧𝗔𝗥𝗚𝗘𝗧 :: {target_id}\n"
            "├─ 🛡️ 𝗦𝗧𝗔𝗧𝗨𝗦 :: Auto-Delete Trigger Active\n"
            "│\n"
            "└───「 ⚡ 𝗦𝗜𝗟𝗘𝗡𝗖𝗘 𝗖𝗢𝗥𝗘 」\n"
            "```"
        )
        await event.edit(card)

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.unlock(?:\s+(.*))?'))
    async def unlock_user(event):
        target_id, _ = await extract_target_user(event, client)
        chat_id = event.chat_id

        if not target_id:
            await event.edit("```text\n[!] Reply to user or provide username/ID\n```")
            return

        if chat_id in locked_users and target_id in locked_users[chat_id]:
            locked_users[chat_id].remove(target_id)
            card = (
                "```text\n"
                "┌───「 🔓 𝗨𝗦𝗘𝗥 𝗨𝗡𝗟𝗢𝗖𝗞𝗘𝗗 ⚡ 」\n"
                "│\n"
                f"├─ 👤 𝗧𝗔𝗥𝗚𝗘𝗧 :: {target_id}\n"
                "├─ ⚡ 𝗦𝗧𝗔𝗧𝗨𝗦 :: Restriction Lifted\n"
                "│\n"
                "└───「 🕊️ 𝗙𝗥𝗘𝗘𝗗 」\n"
                "```"
            )
            await event.edit(card)
        else:
            await event.edit("```text\n[!] User not in lock list.\n```")

    # --- GC LOCK / GC UNLOCK ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.gclock$'))
    async def lock_entire_chat(event):
        locked_chats.add(event.chat_id)
        await event.delete()
        notice = await event.respond(
            "```text\n"
            "┌───「 🛑 𝗚𝗖 𝗟𝗢𝗖𝗞 𝗔𝗖𝗧𝗜𝗩𝗔𝗧𝗘𝗗 ⚡ 」\n"
            "│\n"
            "├─ 🚨 𝗦𝗧𝗔𝗧𝗨𝗦 :: Total Lockdown Engaged\n"
            "├─ 🛡️ 𝗔𝗖𝗧𝗜𝗢𝗡 :: Incoming msgs will be purged\n"
            "│\n"
            "└───「 🔒 𝗞𝗘𝗦𝗛𝗔𝗩 𝗦𝗘𝗖𝗨𝗥𝗜𝗧𝗬 」\n"
            "```"
        )
        await asyncio.sleep(2)
        await notice.delete()

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.gcunlock$'))
    async def unlock_entire_chat(event):
        if event.chat_id in locked_chats:
            locked_chats.remove(event.chat_id)
        await event.delete()
        notice = await event.respond(
            "```text\n"
            "┌───「 🟢 𝗚𝗖 𝗨𝗡𝗟𝗢𝗖𝗞 𝗔𝗖𝗧𝗜𝗩𝗔𝗧𝗘𝗗 ⚡ 」\n"
            "│\n"
            "├─ ⚡ 𝗦𝗧𝗔𝗧𝗨𝗦 :: Lockdown Deactivated\n"
            "│\n"
            "└───「 🔓 𝗦𝗬𝗦𝗧𝗘𝗠 𝗡𝗢𝗥𝗠𝗔𝗟 」\n"
            "```"
        )
        await asyncio.sleep(2)
        await notice.delete()

    # --- BACKGROUND DELETER LISTENER ---
    @client.on(events.NewMessage(incoming=True))
    async def auto_delete_listener(event):
        chat_id = event.chat_id
        sender_id = event.sender_id

        if chat_id in locked_chats:
            try:
                await event.delete()
                return
            except Exception:
                pass

        if chat_id in locked_users and sender_id in locked_users[chat_id]:
            try:
                await event.delete()
            except Exception:
                pass
