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
        
        total_scanned = 0
        success_chats = []
        failed_chats = []

        ban_rights = ChatBannedRights(until_date=None, view_messages=True, send_messages=True)

        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                total_scanned += 1
                cname = dialog.name[:18]
                try:
                    await client(EditBannedRequest(dialog.id, target.id, ban_rights))
                    success_chats.append(cname)
                    await asyncio.sleep(0.08)
                except Exception:
                    failed_chats.append(cname)

        success_log = "\n".join([f"╠─  • {name}" for name in success_chats[:6]]) or "╠─  None"
        if len(success_chats) > 6:
            success_log += f"\n╠─  ...and {len(success_chats) - 6} more"

        card = (
            "```text\n"
            "╔════「 ⚡ 𝗚𝗟𝗢𝗕𝗔𝗟 𝗕𝗔𝗡 𝗔𝗨𝗗𝗜𝗧 ⚡ 」════╗\n"
            "║\n"
            f"╠─ 🎯 𝗧𝗔𝗥𝗚𝗘𝗧    :: {getattr(target, 'first_name', 'User')} ({target.id})\n"
            f"╠─ 🌐 𝗧𝗢𝗧𝗔𝗟 𝗚𝗖𝗦  :: {total_scanned} groups scanned\n"
            f"╠─ 🔨 𝗕𝗔𝗡𝗡𝗘𝗗     :: {len(success_chats)} chats\n"
            f"╠─ 🛡️ 𝗙𝗔𝗜𝗟𝗘𝗗     :: {len(failed_chats)} (No Ban Rights)\n"
            "║\n"
            "╠══「 📋 𝗦𝗨𝗖𝗖𝗘𝗦𝗦 𝗖𝗛𝗔𝗧𝗦 」══\n"
            f"{success_log}\n"
            "║\n"
            "╚════════════════════════════════════╝\n"
            "```"
        )
        await status.edit(card)

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
        
        total_scanned = 0
        success_chats = []
        failed_chats = []

        unban_rights = ChatBannedRights(until_date=None, view_messages=False, send_messages=False)

        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                total_scanned += 1
                cname = dialog.name[:18]
                try:
                    await client(EditBannedRequest(dialog.id, target.id, unban_rights))
                    success_chats.append(cname)
                    await asyncio.sleep(0.08)
                except Exception:
                    failed_chats.append(cname)

        success_log = "\n".join([f"╠─  • {name}" for name in success_chats[:6]]) or "╠─  None"
        if len(success_chats) > 6:
            success_log += f"\n╠─  ...and {len(success_chats) - 6} more"

        card = (
            "```text\n"
            "╔════「 ⚡ 𝗚𝗟𝗢𝗕𝗔𝗟 𝗨𝗡𝗕𝗔𝗡 𝗔𝗨𝗗𝗜𝗧 ⚡ 」════╗\n"
            "║\n"
            f"╠─ 🎯 𝗧𝗔𝗥𝗚𝗘𝗧    :: {getattr(target, 'first_name', 'User')} ({target.id})\n"
            f"╠─ 🌐 𝗧𝗢𝗧𝗔𝗟 𝗚𝗖𝗦  :: {total_scanned} groups scanned\n"
            f"╠─ 🕊️ 𝗨𝗡𝗕𝗔𝗡𝗡𝗘𝗗   :: {len(success_chats)} chats\n"
            f"╠─ 🛡️ 𝗙𝗔𝗜𝗟𝗘𝗗     :: {len(failed_chats)} (No Admin Rights)\n"
            "║\n"
            "╠══「 📋 𝗦𝗨𝗖𝗖𝗘𝗦𝗦 𝗖𝗛𝗔𝗧𝗦 」══\n"
            f"{success_log}\n"
            "║\n"
            "╚═════════════════════════════════════╝\n"
            "```"
        )
        await status.edit(card)

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
        
        total_scanned = 0
        success_chats = []
        failed_chats = []

        mute_rights = ChatBannedRights(until_date=None, send_messages=True, send_media=True, send_stickers=True, send_gifs=True)

        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                total_scanned += 1
                cname = dialog.name[:18]
                try:
                    await client(EditBannedRequest(dialog.id, target.id, mute_rights))
                    success_chats.append(cname)
                    await asyncio.sleep(0.08)
                except Exception:
                    failed_chats.append(cname)

        success_log = "\n".join([f"╠─  • {name}" for name in success_chats[:6]]) or "╠─  None"
        if len(success_chats) > 6:
            success_log += f"\n╠─  ...and {len(success_chats) - 6} more"

        card = (
            "```text\n"
            "╔════「 ⚡ 𝗚𝗟𝗢𝗕𝗔𝗟 𝗠𝗨𝗧𝗘 𝗔𝗨𝗗𝗜𝗧 ⚡ 」════╗\n"
            "║\n"
            f"╠─ 🎯 𝗧𝗔𝗥𝗚𝗘𝗧    :: {getattr(target, 'first_name', 'User')} ({target.id})\n"
            f"╠─ 🌐 𝗧𝗢𝗧𝗔𝗟 𝗚𝗖𝗦  :: {total_scanned} groups scanned\n"
            f"╠─ 🔇 𝗠𝗨𝗧𝗘𝗗      :: {len(success_chats)} chats\n"
            f"╠─ 🛡️ 𝗙𝗔𝗜𝗟𝗘𝗗     :: {len(failed_chats)} (No Admin Rights)\n"
            "║\n"
            "╠══「 📋 𝗦𝗨𝗖𝗖𝗘𝗦𝗦 𝗖𝗛𝗔𝗧𝗦 」══\n"
            f"{success_log}\n"
            "║\n"
            "╚═════════════════════════════════════╝\n"
            "```"
        )
        await status.edit(card)

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
        
        total_scanned = 0
        success_chats = []
        failed_chats = []

        unmute_rights = ChatBannedRights(until_date=None, send_messages=False, send_media=False, send_stickers=False, send_gifs=False)

        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                total_scanned += 1
                cname = dialog.name[:18]
                try:
                    await client(EditBannedRequest(dialog.id, target.id, unmute_rights))
                    success_chats.append(cname)
                    await asyncio.sleep(0.08)
                except Exception:
                    failed_chats.append(cname)

        success_log = "\n".join([f"╠─  • {name}" for name in success_chats[:6]]) or "╠─  None"
        if len(success_chats) > 6:
            success_log += f"\n╠─  ...and {len(success_chats) - 6} more"

        card = (
            "```text\n"
            "╔════「 ⚡ 𝗚𝗟𝗢𝗕𝗔𝗟 𝗨𝗡𝗠𝗨𝗧𝗘 𝗔𝗨𝗗𝗜𝗧 ⚡ 」════╗\n"
            "║\n"
            f"╠─ 🎯 𝗧𝗔𝗥𝗚𝗘𝗧    :: {getattr(target, 'first_name', 'User')} ({target.id})\n"
            f"╠─ 🌐 𝗧𝗢𝗧𝗔𝗟 𝗚𝗖𝗦  :: {total_scanned} groups scanned\n"
            f"╠─ 🔊 𝗨𝗡𝗠𝗨𝗧𝗘𝗗    :: {len(success_chats)} chats\n"
            f"╠─ 🛡️ 𝗙𝗔𝗜𝗟𝗘𝗗     :: {len(failed_chats)} (No Admin Rights)\n"
            "║\n"
            "╠══「 📋 𝗦𝗨𝗖𝗖𝗘𝗦𝗦 𝗖𝗛𝗔𝗧𝗦 」══\n"
            f"{success_log}\n"
            "║\n"
            "╚══════════════════════════════════════╝\n"
            "```"
        )
        await status.edit(card)

    # --- .gpin (Reply to message) ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.gpin$'))
    async def global_pin(event):
        reply = await event.get_reply_message()
        if not reply:
            await event.edit("```text\n[!] Reply to any message to Global Pin.\n```")
            return

        status = await event.edit("```text\n┌───「 📌 𝗚𝗟𝗢𝗕𝗔𝗟 𝗣𝗜𝗡 𝗜𝗡𝗜𝗧𝗜𝗔𝗧𝗘𝗗... 」\n└───「 Broadcasting & Pinning 」\n```")
        
        total_scanned = 0
        success_chats = []
        failed_chats = []

        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                total_scanned += 1
                cname = dialog.name[:18]
                try:
                    forwarded = await client.forward_messages(dialog.id, reply)
                    await client.pin_message(dialog.id, forwarded.id, notify=True)
                    success_chats.append(cname)
                    await asyncio.sleep(0.15)
                except Exception:
                    failed_chats.append(cname)

        success_log = "\n".join([f"╠─  • {name}" for name in success_chats[:6]]) or "╠─  None"
        if len(success_chats) > 6:
            success_log += f"\n╠─  ...and {len(success_chats) - 6} more"

        card = (
            "```text\n"
            "╔════「 ⚡ 𝗚𝗟𝗢𝗕𝗔𝗟 𝗣𝗜𝗡 𝗔𝗨𝗗𝗜𝗧 ⚡ 」════╗\n"
            "║\n"
            f"╠─ 🌐 𝗧𝗢𝗧𝗔𝗟 𝗚𝗖𝗦  :: {total_scanned} groups scanned\n"
            f"╠─ 📌 𝗣𝗜𝗡𝗡𝗘𝗗     :: {len(success_chats)} chats\n"
            f"╠─ 🛡️ 𝗙𝗔𝗜𝗟𝗘𝗗     :: {len(failed_chats)} (No Pin Rights)\n"
            "║\n"
            "╠══「 📋 𝗦𝗨𝗖𝗖𝗘𝗦𝗦 𝗖𝗛𝗔𝗧𝗦 」══\n"
            f"{success_log}\n"
            "║\n"
            "╚════════════════════════════════════╝\n"
            "```"
        )
        await status.edit(card)

    # --- .ungpin ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ungpin$'))
    async def global_unpin(event):
        status = await event.edit("```text\n┌───「 🔓 𝗚𝗟𝗢𝗕𝗔𝗟 𝗨𝗡𝗣𝗜𝗡 𝗜𝗡𝗜𝗧𝗜𝗔𝗧𝗘𝗗... 」\n└───「 Clearing pinned messages 」\n```")
        
        total_scanned = 0
        success_chats = []
        failed_chats = []

        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                total_scanned += 1
                cname = dialog.name[:18]
                try:
                    await client(UnpinAllMessagesRequest(dialog.id))
                    success_chats.append(cname)
                    await asyncio.sleep(0.1)
                except Exception:
                    failed_chats.append(cname)

        success_log = "\n".join([f"╠─  • {name}" for name in success_chats[:6]]) or "╠─  None"
        if len(success_chats) > 6:
            success_log += f"\n╠─  ...and {len(success_chats) - 6} more"

        card = (
            "```text\n"
            "╔════「 ⚡ 𝗚𝗟𝗢𝗕𝗔𝗟 𝗨𝗡𝗣𝗜𝗡 𝗔𝗨𝗗𝗜𝗧 ⚡ 」════╗\n"
            "║\n"
            f"╠─ 🌐 𝗧𝗢𝗧𝗔𝗟 𝗚𝗖𝗦  :: {total_scanned} groups scanned\n"
            f"╠─ 🔓 𝗨𝗡𝗣𝗜𝗡𝗡𝗘𝗗   :: {len(success_chats)} chats\n"
            f"╠─ 🛡️ 𝗙𝗔𝗜𝗟𝗘𝗗     :: {len(failed_chats)} (No Admin Rights)\n"
            "║\n"
            "╠══「 📋 𝗦𝗨𝗖𝗖𝗘𝗦𝗦 𝗖𝗛𝗔𝗧𝗦 」══\n"
            f"{success_log}\n"
            "║\n"
            "╚══════════════════════════════════════╝\n"
            "```"
        )
        await status.edit(card)
