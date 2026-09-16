import asyncio
from telethon import events

running_tags = {}

def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.tagall(?:\s+(.*))?'))
    async def tagall(event):
        chat = await event.get_chat()
        chat_id = event.chat_id
        custom_msg = event.pattern_match.group(1) or "Attention everyone!"

        running_tags[chat_id] = True
        await event.delete()

        header = (
            "```text\n"
            "┌───「 ⚡ 𝗠𝗘𝗡𝗧𝗜𝗢𝗡 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 ⚡ 」\n"
            f"└─ 📢 𝗠𝗘𝗦𝗦𝗔𝗚𝗘 :: {custom_msg}\n"
            "```\n"
        )
        await event.respond(header)

        mentions = []
        async for user in client.iter_participants(chat):
            if not running_tags.get(chat_id, False):
                break
            if user.bot or user.deleted:
                continue
            
            name = user.first_name or "Member"
            mentions.append(f"[{name}](tg://user?id={user.id})")

            if len(mentions) == 5:
                await event.respond(" • " + " • ".join(mentions))
                mentions = []
                await asyncio.sleep(1.8)

        if mentions and running_tags.get(chat_id, False):
            await event.respond(" • " + " • ".join(mentions))

        running_tags[chat_id] = False

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.(?:cancel|stop)$'))
    async def stop_tag(event):
        chat_id = event.chat_id
        if running_tags.get(chat_id, False):
            running_tags[chat_id] = False
            await event.edit("```text\n[!] Tagall process stopped by user.\n```")
        else:
            await event.edit("```text\n[!] No active tagall process here.\n```")
