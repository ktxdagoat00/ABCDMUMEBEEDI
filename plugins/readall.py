from telethon import events

def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.readall$'))
    async def mark_all_read(event):
        status = await event.edit("```text\n┌───「 🧹 𝗦𝗧𝗘𝗔𝗟𝗧𝗛 𝗠𝗔𝗥𝗞-𝗥𝗘𝗔𝗗... 」\n└───「 Clearing unread counters 」\n```")
        cleared = 0

        async for dialog in client.iter_dialogs():
            if dialog.unread_count > 0:
                await client.send_read_acknowledge(dialog.entity)
                cleared += 1

        card = (
            "```text\n"
            "╔════「 ⚡ 𝗥𝗘𝗔𝗗-𝗔𝗟𝗟 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘 ⚡ 」════╗\n"
            "║\n"
            "╠─ 👤 MASTER  :: K E S H A V\n"
            f"╠─ 📬 CLEARED :: {cleared} unread conversations\n"
            "║\n"
            "╚══════════════════════════════════════╝\n"
            "```"
        )
        await status.edit(card)
