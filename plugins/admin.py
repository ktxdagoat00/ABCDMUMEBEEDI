import asyncio
from telethon import events
from telethon.tl.functions.channels import EditBannedRequest, EditAdminRequest
from telethon.tl.types import ChatBannedRights, ChatAdminRights

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

# --- Group-safe Admin Rights Tiers ---
# Tier 1: Ghost admin (no practical rights, only badge)
ADMIN_TIER_1 = ChatAdminRights(
    change_info=False,
    delete_messages=False,
    ban_users=False,
    invite_users=False,
    pin_messages=False,
    add_admins=False,
    anonymous=False,
    manage_call=False,
    other=True
)

# Tier 2: Standard admin (moderate privileges, no add admin, no anon)
ADMIN_TIER_2 = ChatAdminRights(
    change_info=True,
    delete_messages=True,
    ban_users=True,
    invite_users=True,
    pin_messages=True,
    add_admins=False,
    anonymous=False,
    manage_call=True,
    other=True
)

# Tier 3: Super admin (full rights except anonymous)
ADMIN_TIER_3 = ChatAdminRights(
    change_info=True,
    delete_messages=True,
    ban_users=True,
    invite_users=True,
    pin_messages=True,
    add_admins=True,
    anonymous=False,
    manage_call=True,
    other=True
)

# Demote rights: completely stripped
DEMOTE_RIGHTS = ChatAdminRights(
    change_info=False,
    delete_messages=False,
    ban_users=False,
    invite_users=False,
    pin_messages=False,
    add_admins=False,
    anonymous=False,
    manage_call=False,
    other=False
)

async def resolve_entity(client, chat, target):
    try:
        return await client.get_input_entity(target)
    except Exception:
        pass

    if isinstance(target, int) or (isinstance(target, str) and (target.isdigit() or target.startswith("-"))):
        uid = int(target)
        try:
            async for member in client.iter_participants(chat):
                if member.id == uid:
                    return await client.get_input_entity(member)
        except Exception:
            pass

    try:
        async for member in client.iter_participants(chat, search=str(target)):
            if str(member.id) == str(target) or member.username == str(target).replace("@", ""):
                return await client.get_input_entity(member)
    except Exception:
        pass

    return None

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
        return target, reason
    return None, ""

def setup(client):

    # --- BAN COMMAND ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ban(?:\s+(.*))?'))
    async def ban_user(event):
        chat = await event.get_input_chat()
        target_raw, reason = await extract_target_user(event, client)
        
        if not target_raw:
            await event.edit("```text\n[!] Reply to user or provide ID/Username\n```")
            return

        reason_text = reason if reason else "No reason specified"
        
        try:
            target_entity = await resolve_entity(client, chat, target_raw)
            if not target_entity:
                await event.edit("```text\n[!] User not found in this group/cache!\n```")
                return

            await client(EditBannedRequest(chat, target_entity, BANNED_RIGHTS))
            
            card = (
                "```text\n"
                "┌───「 🚫 𝗨𝗦𝗘𝗥 𝗘𝗫𝗘𝗖𝗨𝗧𝗜𝗢𝗡 ⚡ 」\n"
                "│\n"
                f"├─ 👤 𝗧𝗔𝗥𝗚𝗘𝗧 :: {target_raw}\n"
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
        target_raw, _ = await extract_target_user(event, client)

        if not target_raw:
            await event.edit("```text\n[!] Reply to user or provide ID/Username\n```")
            return

        try:
            target_entity = await resolve_entity(client, chat, target_raw)
            if not target_entity:
                await event.edit("```text\n[!] User entity not resolved!\n```")
                return

            await client(EditBannedRequest(chat, target_entity, UNBANNED_RIGHTS))

            card = (
                "```text\n"
                "┌───「 🔓 𝗨𝗦𝗘𝗥 𝗣𝗔𝗥𝗗𝗢𝗡𝗘𝗗 ⚡ 」\n"
                "│\n"
                f"├─ 👤 𝗧𝗔𝗥𝗚𝗘𝗧 :: {target_raw}\n"
                "├─ 🛡️ 𝗔𝗖𝗧𝗜𝗢𝗡 :: Unbanned / Restrictions Lifted\n"
                "│\n"
                "└───「 🕊️ 𝗞𝗘𝗦𝗛𝗔𝗩-𝗦𝗘𝗖𝗨𝗥𝗜𝗧𝗬 」\n"
                "```"
            )
            await event.edit(card)
        except Exception as e:
            await event.edit(f"```text\n[!] Unban Failed: {e}\n```")

    # --- PROMOTE COMMANDS (1, 2, 3) ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.promote(?:\s+(.*))?'))
    async def promote_handler(event):
        chat = await event.get_input_chat()
        args = (event.pattern_match.group(1) or "").strip().split()
        reply = await event.get_reply_message()

        tier = "2"
        target_raw = None

        if reply:
            target_raw = reply.sender_id
            if len(args) >= 1 and args[0] in ["1", "2", "3"]:
                tier = args[0]
        else:
            if len(args) >= 2 and args[0] in ["1", "2", "3"]:
                tier = args[0]
                target_raw = args[1]
            elif len(args) >= 1:
                target_raw = args[0]

        if not target_raw:
            await event.edit(
                "```text\n"
                "┌───「 ⚠️ 𝗣𝗥𝗢𝗠𝗢𝗧𝗘 𝗨𝗦𝗔𝗚𝗘 」\n"
                "├─ .promote 1 <user/reply> :: Zero Rights\n"
                "├─ .promote 2 <user/reply> :: Standard (No Add Admin/Anon)\n"
                "└─ .promote 3 <user/reply> :: Full Rights (No Anon)\n"
                "```"
            )
            return

        if str(target_raw).isdigit() or (str(target_raw).startswith("-") and str(target_raw)[1:].isdigit()):
            target_raw = int(target_raw)

        rights_map = {
            "1": (ADMIN_TIER_1, "Tier 1 [Zero Rights / Badge]"),
            "2": (ADMIN_TIER_2, "Tier 2 [Standard Admin]"),
            "3": (ADMIN_TIER_3, "Tier 3 [Super Admin]")
        }
        chosen_rights, tier_name = rights_map.get(tier, (ADMIN_TIER_2, "Tier 2 [Standard Admin]"))

        try:
            target_entity = await resolve_entity(client, chat, target_raw)
            if not target_entity:
                await event.edit("```text\n[!] User entity not found!\n```")
                return

            await client(EditAdminRequest(
                channel=chat,
                user_id=target_entity,
                admin_rights=chosen_rights,
                rank="Admin"
            ))

            card = (
                "```text\n"
                "┌───「 ⚡ 𝗔𝗗𝗠𝗜𝗡 𝗣𝗥𝗢𝗠𝗢𝗧𝗜𝗢𝗡 ⚡ 」\n"
                "│\n"
                f"├─ 👤 𝗧𝗔𝗥𝗚𝗘𝗧 :: {target_raw}\n"
                f"├─ 🎖️ 𝗟𝗘𝗩𝗘𝗟  :: {tier_name}\n"
                "├─ 🛡️ 𝗦𝗧𝗔𝗧𝗨𝗦 :: Privileges Granted\n"
                "│\n"
                "└───「 👑 𝗞𝗘𝗦𝗛𝗔𝗩-𝗦𝗬𝗦𝗧𝗘𝗠 」\n"
                "```"
            )
            await event.edit(card)
        except Exception as e:
            await event.edit(f"```text\n[!] Promote Failed: {e}\n```")

    # --- DEMOTE COMMAND ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.demote(?:\s+(.*))?'))
    async def demote_handler(event):
        chat = await event.get_input_chat()
        target_raw, _ = await extract_target_user(event, client)

        if not target_raw:
            await event.edit("```text\n[!] Reply to user or provide username/ID\n```")
            return

        try:
            target_entity = await resolve_entity(client, chat, target_raw)
            if not target_entity:
                await event.edit("```text\n[!] User entity not found!\n```")
                return

            await client(EditAdminRequest(
                channel=chat,
                user_id=target_entity,
                admin_rights=DEMOTE_RIGHTS,
                rank=""
            ))

            card = (
                "```text\n"
                "┌───「 🔻 𝗔𝗗𝗠𝗜𝗡 𝗗𝗘𝗠𝗢𝗧𝗜𝗢𝗡 ⚡ 」\n"
                "│\n"
                f"├─ 👤 𝗧𝗔𝗥𝗚𝗘𝗧 :: {target_raw}\n"
                "├─ 🛡️ 𝗦𝗧𝗔𝗧𝗨𝗦 :: All Admin Rights Stripped\n"
                "│\n"
                "└───「 📉 𝗞𝗘𝗦𝗛𝗔𝗩-𝗦𝗬𝗦𝗧𝗘𝗠 」\n"
                "```"
            )
            await event.edit(card)
        except Exception as e:
            await event.edit(f"```text\n[!] Demote Failed: {e}\n```")

    # --- USER LOCK / UNLOCK ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.lock(?:\s+(.*))?'))
    async def lock_user(event):
        target_raw, _ = await extract_target_user(event, client)
        if not target_raw:
            await event.edit("```text\n[!] Reply to user or provide username/ID\n```")
            return

        target_id = target_raw
        if isinstance(target_raw, str) and not target_raw.isdigit():
            try:
                entity = await client.get_entity(target_raw)
                target_id = entity.id
            except Exception:
                pass

        chat_id = event.chat_id
        if chat_id not in locked_users:
            locked_users[chat_id] = set()
        
        locked_users[chat_id].add(target_id)
        card = (
            "```text\n"
            "┌───「 🔒 𝗨𝗦𝗘𝗥 𝗟𝗢𝗖𝗞𝗘𝗗 ⚡ 」\n"
            "│\n"
            f"├─ 👤 𝗧𝗔𝗥𝗚𝗘𝗧 :: {target_raw}\n"
            "├─ 🛡️ 𝗦𝗧𝗔𝗧𝗨𝗦 :: Auto-Delete Trigger Active\n"
            "│\n"
            "└───「 ⚡ 𝗦𝗜𝗟𝗘𝗡𝗖𝗘 𝗖𝗢𝗥𝗘 」\n"
            "```"
        )
        await event.edit(card)

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.unlock(?:\s+(.*))?'))
    async def unlock_user(event):
        target_raw, _ = await extract_target_user(event, client)
        chat_id = event.chat_id

        if not target_raw:
            await event.edit("```text\n[!] Reply to user or provide username/ID\n```")
            return

        target_id = target_raw
        if isinstance(target_raw, str) and not target_raw.isdigit():
            try:
                entity = await client.get_entity(target_raw)
                target_id = entity.id
            except Exception:
                pass

        if chat_id in locked_users and target_id in locked_users[chat_id]:
            locked_users[chat_id].remove(target_id)
            card = (
                "```text\n"
                "┌───「 🔓 𝗨𝗦𝗘𝗥 𝗨𝗡𝗟𝗢𝗖𝗞𝗘𝗗 ⚡ 」\n"
                "│\n"
                f"├─ 👤 𝗧𝗔𝗥𝗚𝗘𝗧 :: {target_raw}\n"
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
