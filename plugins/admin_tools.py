import asyncio
from telethon import events
from telethon.tl.types import ChatBannedRights
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.functions.messages import UpdatePinnedMessageRequest, UnpinAllMessagesRequest

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
        banned_count, failed_count = 0, 0
        ban_rights = ChatBannedRights(until_date=None, view_messages=True, send_messages=True)

        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                try:
                    await client(EditBannedRequest(dialog.id, target.id, ban_rights))
                    banned_count += 1
                    await asyncio.sleep(0.08)
                except Exception:
                    failed_count += 1

        await status.edit(
            "```text\n"
            "╔════「 ⚡ 𝗚𝗟𝗢𝗕𝗔𝗟 𝗕𝗔𝗡 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗 」════╗\n"
            f"╠─ 👤 𝗧𝗔𝗥𝗚𝗘𝗧 :: {getattr(target, 'first_name', 'User')} ({target.id})\n"
            f"╠─ 🔨 𝗕𝗔𝗡𝗡𝗘𝗗 :: {banned_count} chats\n"
            f"╠─ 🛡️ 𝗦𝗞𝗜𝗣    :: {failed_count} (Not Admin)\n"
            "╚══════════════════════════════════════════╝\n"
            "```"
        )

    # --- .ungban <user/reply> ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ungban(?:\s+(.+))?'))
    async def global_unban(event):
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
            await event.edit("```text\n[!] Usage: .ungban <user/reply>\n```")
            return

        status = await event.edit(f"```text\n┌───「 🕊️ 𝗚𝗟𝗢𝗕𝗔𝗟 𝗨𝗡𝗕𝗔𝗡 𝗜𝗡𝗜𝗧𝗜𝗔𝗧𝗘𝗗 」\n└─ 🎯 Target: {target.id}\n```")
        unbanned_count, failed_count = 0, 0
        unban_rights = ChatBannedRights(until_date=None, view_messages=False, send_messages=False)

        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                try:
                    await client(EditBannedRequest(dialog.id, target.id, unban_rights))
                    unbanned_count += 1
                    await asyncio.sleep(0.08)
                except Exception:
                    failed_count += 1

        await status.edit(
            "```text\n"
            "╔════「 ⚡ 𝗚𝗟𝗢𝗕𝗔𝗟 𝗨𝗡𝗕𝗔𝗡 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗 」════╗\n"
            f"╠─ 👤 𝗧𝗔𝗥𝗚𝗘𝗧 :: {getattr(target, 'first_name', 'User')} ({target.id})\n"
            f"╠─ 🕊️ 𝗨𝗡𝗕𝗔𝗡   :: {unbanned_count} chats\n"
            f"╠─ 🛡️ 𝗦𝗞𝗜𝗣    :: {failed_count} (Not Admin)\n"
            "╚══════════════════════════════════════════╝\n"
            "```"
        )

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
        muted_count, failed_count = 0, 0
        mute_rights = ChatBannedRights(until_date=None, send_messages=True, send_media=True, send_stickers=True, send_gifs=True)

        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                try:
                    await client(EditBannedRequest(dialog.id, target.id, mute_rights))
                    muted_count += 1
                    await asyncio.sleep(0.08)
                except Exception:
                    failed_count += 1

        await status.edit(
            "```text\n"
            "╔════「 ⚡ 𝗚𝗟𝗢𝗕𝗔𝗟 𝗠𝗨𝗧𝗘 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗 」════╗\n"
            f"╠─ 👤 𝗧𝗔𝗥𝗚𝗘𝗧 :: {getattr(target, 'first_name', 'User')} ({target.id})\n"
            f"╠─ 🔇 𝗠𝗨𝗧𝗘𝗗  :: {muted_count} chats\n"
            f"╠─ 🛡️ 𝗦𝗞𝗜𝗣    :: {failed_count} (Not Admin)\n"
            "╚══════════════════════════════════════════╝\n"
            "```"
        )

    # --- .ungmute <user/reply> ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ungmute(?:\s+(.+))?'))
    async def global_unmute(event):
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
            await event.edit("```text\n[!] Usage: .ungmute <user/reply>\n```")
            return

        status = await event.edit(f"```text\n┌───「 🔊 𝗚𝗟𝗢𝗕𝗔𝗟 𝗨𝗡𝗠𝗨𝗧𝗘 𝗜𝗡𝗜𝗧𝗜𝗔𝗧𝗘𝗗 」\n└─ 🎯 Target: {target.id}\n```")
        unmuted_count, failed_count = 0, 0
        unmute_rights = ChatBannedRights(until_date=None, send_messages=False, send_media=False, send_stickers=False, send_gifs=False)

        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                try:
                    await client(EditBannedRequest(dialog.id, target.id, unmute_rights))
                    unmuted_count += 1
                    await asyncio.sleep(0.08)
                except Exception:
                    failed_count += 1

        await status.edit(
            "```text\n"
            "╔════「 ⚡ 𝗚𝗟𝗢𝗕𝗔𝗟 𝗨𝗡𝗠𝗨𝗧𝗘 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗 」════╗\n"
            f"╠─ 👤 𝗧𝗔𝗥𝗚𝗘𝗧 :: {getattr(target, 'first_name', 'User')} ({target.id})\n"
            f"╠─ 🔊 𝗨𝗡𝗠𝗨𝗧𝗘 :: {unmuted_count} chats\n"
            f"╠─ 🛡️ 𝗦𝗞𝗜𝗣    :: {failed_count} (Not Admin)\n"
            "╚══════════════════════════════════════════╝\n"
            "```"
        )

    # --- .gpin (Reply to message) ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.gpin$'))
    async def global_pin(event):
        reply = await event.get_reply_message()
        if not reply:
            await event.edit("```text\n[!] Reply to any message to Global Pin.\n```")
            return

        status = await event.edit("```text\n┌───「 📌 𝗚𝗟𝗢𝗕𝗔𝗟 𝗣𝗜𝗡 𝗜𝗡𝗜𝗧𝗜𝗔𝗧𝗘𝗗... 」\n└───「 Broadcasting & Pinning 」\n```")
        pinned_count, failed_count = 0, 0

        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                try:
                    forwarded = await client.forward_messages(dialog.id, reply)
                    await client.pin_message(dialog.id, forwarded.id, notify=True)
                    pinned_count += 1
                    await asyncio.sleep(0.15)
                except Exception:
                    failed_count += 1

        await status.edit(
            "```text\n"
            "╔════「 ⚡ 𝗚𝗟𝗢𝗕𝗔𝗟 𝗣𝗜𝗡 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗 」════╗\n"
            f"╠─ 📌 𝗣𝗜𝗡𝗡𝗘𝗗 :: {pinned_count} groups\n"
            f"╠─ 🛡️ 𝗦𝗞𝗜𝗣   :: {failed_count} (No Pin Rights)\n"
            "╚═════════════════════════════════════════╝\n"
            "```"
        )

    # --- .ungpin ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ungpin$'))
    async def global_unpin(event):
        status = await event.edit("```text\n┌───「 🔓 𝗚𝗟𝗢𝗕𝗔𝗟 𝗨𝗡𝗣𝗜𝗡 𝗜𝗡𝗜𝗧𝗜𝗔𝗧𝗘𝗗... 」\n└───「 Clearing pinned messages 」\n```")
        unpinned_count, failed_count = 0, 0

        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                try:
                    await client(UnpinAllMessagesRequest(dialog.id))
                    unpinned_count += 1
                    await asyncio.sleep(0.1)
                except Exception:
                    failed_count += 1

        await status.edit(
            "```text\n"
            "╔════「 ⚡ 𝗚𝗟𝗢𝗕𝗔𝗟 𝗨𝗡𝗣𝗜𝗡 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗 」════╗\n"
            f"╠─ 🔓 𝗨𝗡𝗣𝗜𝗡𝗡𝗘𝗗 :: {unpinned_count} groups\n"
            f"╠─ 🛡️ 𝗦𝗞𝗜𝗣     :: {failed_count} (No Admin Rights)\n"
            "╚═══════════════════════════════════════════╝\n"
            "```"
        )
