import asyncio
from telethon import events
from telethon.tl.types import ChatBannedRights
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.functions.messages import UpdatePinnedMessageRequest

def setup(client):

    # --- .gban <user/reply> ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.gban(?:\s+(.+))?'))
    async def global_ban(event):
        reply = await event.get_reply_message()
        user_arg = event.pattern_match.group(1)
        target = None

        if reply:
            target = await reply.get_sender()
        elif user_arg:
            try:
                target = await client.get_entity(int(user_arg) if user_arg.isdigit() else user_arg)
            except Exception as e:
                await event.edit(f"```text\n[!] User not found: {e}\n```")
                return
        else:
            await event.edit("```text\n[!] Usage: .gban <user/reply>\n```")
            return

        status = await event.edit(f"```text\n┌───「 🚨 𝗚𝗟𝗢𝗕𝗔𝗟 𝗕𝗔𝗡 𝗜𝗡𝗜𝗧𝗜𝗔𝗧𝗘𝗗 」\n└─ 🎯 Target: {target.id}\n```")
        banned_count = 0
        failed_count = 0

        ban_rights = ChatBannedRights(until_date=None, view_messages=True, send_messages=True)

        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                try:
                    await client(EditBannedRequest(dialog.id, target.id, ban_rights))
                    banned_count += 1
                    await asyncio.sleep(0.1)
                except Exception:
                    failed_count += 1

        result = (
            "```text\n"
            "╔════「 ⚡ 𝗚𝗟𝗢𝗕𝗔𝗟 𝗕𝗔𝗡 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗 」════╗\n"
            f"╠─ 👤 𝗧𝗔𝗥𝗚𝗘𝗧 :: {getattr(target, 'first_name', 'User')} ({target.id})\n"
            f"╠─ 🔨 𝗕𝗔𝗡𝗡𝗘𝗗 :: {banned_count} chats\n"
            f"╠─ 🛡️ 𝗦𝗞𝗜𝗣    :: {failed_count} (Not Admin / Restricted)\n"
            "╚══════════════════════════════════════════╝\n"
            "```"
        )
        await status.edit(result)

    # --- .gmute <user/reply> ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.gmute(?:\s+(.+))?'))
    async def global_mute(event):
        reply = await event.get_reply_message()
        user_arg = event.pattern_match.group(1)
        target = None

        if reply:
            target = await reply.get_sender()
        elif user_arg:
            try:
                target = await client.get_entity(int(user_arg) if user_arg.isdigit() else user_arg)
            except Exception as e:
                await event.edit(f"```text\n[!] User not found: {e}\n```")
                return
        else:
            await event.edit("```text\n[!] Usage: .gmute <user/reply>\n```")
            return

        status = await event.edit(f"```text\n┌───「 🔇 𝗚𝗟𝗢𝗕𝗔𝗟 𝗠𝗨𝗧𝗘 𝗜𝗡𝗜𝗧𝗜𝗔𝗧𝗘𝗗 」\n└─ 🎯 Target: {target.id}\n```")
        muted_count = 0
        failed_count = 0

        mute_rights = ChatBannedRights(until_date=None, send_messages=True, send_media=True, send_stickers=True, send_gifs=True)

        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                try:
                    await client(EditBannedRequest(dialog.id, target.id, mute_rights))
                    muted_count += 1
                    await asyncio.sleep(0.1)
                except Exception:
                    failed_count += 1

        result = (
            "```text\n"
            "╔════「 ⚡ 𝗚𝗟𝗢𝗕𝗔𝗟 𝗠𝗨𝗧𝗘 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗 」════╗\n"
            f"╠─ 👤 𝗧𝗔𝗥𝗚𝗘𝗧 :: {getattr(target, 'first_name', 'User')} ({target.id})\n"
            f"╠─ 🔇 𝗠𝗨𝗧𝗘𝗗  :: {muted_count} chats\n"
            f"╠─ 🛡️ 𝗦𝗞𝗜𝗣    :: {failed_count} (Not Admin)\n"
            "╚══════════════════════════════════════════╝\n"
            "```"
        )
        await status.edit(result)

    # --- .gpin (Reply to message) ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.gpin$'))
    async def global_pin(event):
        reply = await event.get_reply_message()
        if not reply:
            await event.edit("```text\n[!] Reply to any message to Global Pin across all your groups.\n```")
            return

        status = await event.edit("```text\n┌───「 📌 𝗚𝗟𝗢𝗕𝗔𝗟 𝗣𝗜𝗡 𝗜𝗡𝗜𝗧𝗜𝗔𝗧𝗘𝗗... 」\n└───「 Broadcasting & Pinning 」\n```")
        pinned_count = 0
        failed_count = 0

        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                try:
                    forwarded = await client.forward_messages(dialog.id, reply)
                    await client.pin_message(dialog.id, forwarded.id, notify=True)
                    pinned_count += 1
                    await asyncio.sleep(0.2)
                except Exception:
                    failed_count += 1

        result = (
            "```text\n"
            "╔════「 ⚡ 𝗚𝗟𝗢𝗕𝗔𝗟 𝗣𝗜𝗡 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗 」════╗\n"
            f"╠─ 📌 𝗣𝗜𝗡𝗡𝗘𝗗 :: {pinned_count} groups\n"
            f"╠─ 🛡️ 𝗦𝗞𝗜𝗣   :: {failed_count} (No Pin Rights)\n"
            "╚═════════════════════════════════════════╝\n"
            "```"
        )
        await status.edit(result)
