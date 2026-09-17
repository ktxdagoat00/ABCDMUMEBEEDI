import asyncio
from telethon import events

def setup(client):

    # --- .del (Delete single replied message) ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.del$'))
    async def delete_single(event):
        reply = await event.get_reply_message()
        await event.delete()
        if reply:
            try:
                await reply.delete()
            except Exception:
                pass

    # --- .delall (Delete all messages from a replied user in this group) ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.delall$'))
    async def delete_all_from_user(event):
        reply = await event.get_reply_message()
        if not reply:
            await event.edit("```text\n[!] Reply to a user to purge all their messages!\n```")
            return

        target_user = reply.sender_id
        chat = await event.get_input_chat()
        await event.delete()

        status_msg = await event.respond("```text\n[🧹] Scanning & purging user messages...\n```")
        deleted_count = 0
        batch = []

        async for msg in client.iter_messages(chat, from_user=target_user, limit=500):
            batch.append(msg.id)
            if len(batch) >= 100:
                await client.delete_messages(chat, batch)
                deleted_count += len(batch)
                batch = []
                await asyncio.sleep(0.5)

        if batch:
            await client.delete_messages(chat, batch)
            deleted_count += len(batch)

        await status_msg.edit(
            "```text\n"
            "┌───「 🧹 𝗗𝗘𝗟𝗔𝗟𝗟 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘 」\n"
            f"├─ 👤 𝗧𝗔𝗥𝗚𝗘𝗧 :: {target_user}\n"
            f"└─ 🗑️ 𝗣𝗨𝗥𝗚𝗘𝗗 :: {deleted_count} messages\n"
            "```"
        )
        await asyncio.sleep(3)
        await status_msg.delete()

    # --- .purgeme (Purge own messages in the chat) ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.purgeme(?:\s+(\d+))?'))
    async def purge_my_messages(event):
        limit = int(event.pattern_match.group(1) or 100)
        chat = await event.get_input_chat()
        await event.delete()

        status_msg = await event.respond(f"```text\n[🧹] Purging your last {limit} messages...\n```")
        batch = []
        count = 0

        async for msg in client.iter_messages(chat, from_user="me", limit=limit):
            batch.append(msg.id)
            if len(batch) >= 100:
                await client.delete_messages(chat, batch)
                count += len(batch)
                batch = []
                await asyncio.sleep(0.5)

        if batch:
            await client.delete_messages(chat, batch)
            count += len(batch)

        await status_msg.edit(
            "```text\n"
            "┌───「 🧹 𝗣𝗨𝗥𝗚𝗘𝗠𝗘 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘 」\n"
            f"└─ 🗑️ Cleaned :: {count} own messages\n"
            "```"
        )
        await asyncio.sleep(3)
        await status_msg.delete()
