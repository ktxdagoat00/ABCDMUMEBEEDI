import asyncio
from telethon import events
from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantsBots

def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.audit(?:\s+(.+))?'))
    async def group_audit(event):
        if not event.is_group:
            await event.edit("```text\n[!] .audit command can only be used in groups/supergroups!\n```")
            return

        arg = (event.pattern_match.group(1) or "").strip().lower()
        chat = await event.get_input_chat()

        # Mode: .audit clean (Kicking deleted accounts)
        if arg == "clean":
            status = await event.edit("```text\n┌───「 🧹 𝗦𝗧𝗘𝗔𝗟𝗧𝗛 𝗔𝗨𝗗𝗜𝗧 𝗖𝗟𝗘𝗔𝗡 」\n└───「 Hunting & purging ghost accounts... 」\n```")
            cleaned_count = 0
            
            try:
                async for user in client.iter_participants(chat):
                    if user.deleted:
                        try:
                            await client.kick_participant(chat, user.id)
                            cleaned_count += 1
                            await asyncio.sleep(0.1)
                        except Exception:
                            pass

                card = (
                    "```text\n"
                    "╔════「 ⚡ 𝗔𝗨𝗗𝗜𝗧 𝗣𝗨𝗥𝗚𝗘 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗 」════╗\n"
                    "║\n"
                    "╠─ 👤 MASTER   :: K E S H A V\n"
                    f"╠─ 💀 REMOVED  :: {cleaned_count} ghost/deleted accounts\n"
                    "║\n"
                    "╚══════════════════════════════════════╝\n"
                    "```"
                )
                await status.edit(card)
            except Exception as e:
                await status.edit(f"```text\n[!] Clean Error: {e}\nEnsure you have ban/kick rights!\n```")
            return

        # Mode: Standard .audit (Chat X-Ray)
        status = await event.edit("```text\n┌───「 🔍 𝗖𝗛𝗔𝗧 𝗫-𝗥𝗔𝗬 𝗦𝗖𝗔𝗡𝗡𝗜𝗡𝗚... 」\n└───「 Aggregating members & permission layers 」\n```")

        total_members = 0
        deleted_users = 0
        bot_users = 0
        premium_users = 0

        try:
            async for user in client.iter_participants(chat):
                total_members += 1
                if user.deleted:
                    deleted_users += 1
                if getattr(user, 'bot', False):
                    bot_users += 1
                if getattr(user, 'premium', False):
                    premium_users += 1

            # Count Admins
            admins_count = 0
            async for admin in client.iter_participants(chat, filter=ChannelParticipantsAdmins):
                admins_count += 1

            human_users = total_members - bot_users - deleted_users
            dead_ratio = round((deleted_users / total_members * 100), 1) if total_members else 0

            card = (
                "```text\n"
                "╔════「 ⚡ 𝗖𝗛𝗔𝗧 𝗫-𝗥𝗔𝗬 𝗔𝗨𝗗𝗜𝗧 ⚡ 」════╗\n"
                "║\n"
                "╠─ 👤 MASTER     :: K E S H A V\n"
                f"╠─ 👥 TOTAL      :: {total_members}\n"
                f"╠─ 🧑 HUMANS     :: {human_users}\n"
                f"╠─ 🤖 BOTS       :: {bot_users}\n"
                f"╠─ ⭐ PREMIUM    :: {premium_users}\n"
                f"╠─ 🛡️ ADMINS     :: {admins_count}\n"
                f"╠─ 💀 DELETED    :: {deleted_users} ({dead_ratio}% dead weight)\n"
                "║\n"
                "╠─ 💡 Run: .audit clean to purge deleted users\n"
                "╚═════════════════════════════════════╝\n"
                "```"
            )
            await status.edit(card)

        except Exception as e:
            await status.edit(f"```text\n[!] Audit Scan Error: {e}\n```")
