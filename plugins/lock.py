from telethon import events

LOCKED_USERS = set()

def setup(client):

    # 1. Lock command (.lock on reply or .lock <id>)
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.lock(?:\s+(.+))?'))
    async def lock_user(event):
        target = None
        reply = await event.get_reply_message()
        if reply:
            target = reply.sender_id
        else:
            arg = event.pattern_match.group(1)
            if arg:
                try:
                    entity = await client.get_entity(arg.strip())
                    target = entity.id
                except Exception:
                    await event.edit("```text\n[!] Invalid user entity or ID.\n```")
                    return

        if not target:
            await event.edit("```text\n[!] Reply to a user or provide an ID to lock.\n```")
            return

        LOCKED_USERS.add(target)
        card = (
            "```text\n"
            "╔════「 🔒 𝗨𝗦𝗘𝗥 𝗟𝗢𝗖𝗞 𝗘𝗡𝗚𝗔𝗚𝗘𝗗 」════╗\n"
            "║\n"
            "╠─ 👤 MASTER :: K E S H A V\n"
            f"╠─ 🎯 TARGET :: {target}\n"
            "╠─ ⚡ STATUS :: Continuous wipe active\n"
            "║\n"
            "╚════════════════════════════════════╝\n"
            "```"
        )
        await event.edit(card)

    # 2. Unlock command (.unlock on reply or .unlock <id>)
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.unlock(?:\s+(.+))?'))
    async def unlock_user(event):
        target = None
        reply = await event.get_reply_message()
        if reply:
            target = reply.sender_id
        else:
            arg = event.pattern_match.group(1)
            if arg:
                try:
                    entity = await client.get_entity(arg.strip())
                    target = entity.id
                except Exception:
                    pass

        if target in LOCKED_USERS:
            LOCKED_USERS.remove(target)
            await event.edit(f"```text\n[✓] Released lock for user: {target}\n```")
        else:
            await event.edit("```text\n[!] Target is not in the lock registry.\n```")

    # 3. Message wipe watcher
    @client.on(events.NewMessage(incoming=True))
    async def lock_watcher(event):
        if event.sender_id in LOCKED_USERS:
            try:
                await event.delete()
            except Exception:
                pass
