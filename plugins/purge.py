import asyncio
from telethon import events
from telethon.errors import FloodWaitError, MessageDeleteForbiddenError

def setup(client):

    # Fast Single Message Delete: .del
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.del$'))
    async def delete_target(event):
        reply = await event.get_reply_message()
        await event.delete()
        if reply:
            try:
                await reply.delete()
            except Exception:
                pass

    # Universal Deep Purge: .purge [count] (or reply to start point)
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.purge(?:\s+(\d+))?$'))
    async def fast_purge(event):
        chat = await event.get_input_chat()
        reply = await event.get_reply_message()
        count_arg = event.pattern_match.group(1)

        msg_ids = []

        if reply:
            start_id = reply.id
            end_id = event.id
            # Reply message se lekar current .purge message tak sab collect karo
            async for msg in client.iter_messages(chat, min_id=start_id - 1, max_id=end_id + 1):
                msg_ids.append(msg.id)
        elif count_arg:
            limit = int(count_arg)
            async for msg in client.iter_messages(chat, limit=limit + 1):
                msg_ids.append(msg.id)
        else:
            await event.edit("```text\n[!] Reply to a starting message or provide count: .purge 50\n```")
            await asyncio.sleep(3)
            await event.delete()
            return

        if not msg_ids:
            await event.edit("```text\n[!] No messages found to purge.\n```")
            await asyncio.sleep(2)
            await event.delete()
            return

        status_msg = await event.edit(f"```text\n[~] Purging {len(msg_ids)} messages...\n```")

        # Telegram bulk delete limit is 100 per request
        deleted_count = 0
        chunk_size = 100

        for i in range(0, len(msg_ids), chunk_size):
            chunk = msg_ids[i:i + chunk_size]
            try:
                await client.delete_messages(chat, chunk)
                deleted_count += len(chunk)
            except FloodWaitError as e:
                await asyncio.sleep(e.seconds + 1)
                try:
                    await client.delete_messages(chat, chunk)
                    deleted_count += len(chunk)
                except Exception:
                    pass
            except MessageDeleteForbiddenError:
                # Agar group me rights nahi hain aur sirf apne delete ho sakte hain
                for m_id in chunk:
                    try:
                        await client.delete_messages(chat, m_id)
                        deleted_count += 1
                    except Exception:
                        pass
            except Exception:
                pass

        card = (
            "```text\n"
            "╔═════「 🧹 CHAT PURGED CLEAN 」═════╗\n"
            "║\n"
            f"╠─ 🗑️ DELETED :: {deleted_count} messages\n"
            "╠─ ⚡ STATUS  :: Cleared successfully\n"
            "║\n"
            "╚═════════════════════════════════════╝\n"
            "```"
        )
        try:
            await status_msg.edit(card)
            await asyncio.sleep(3)
            await status_msg.delete()
        except Exception:
            pass
