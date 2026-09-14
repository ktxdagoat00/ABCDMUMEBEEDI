import asyncio
from telethon import events

def setup(client):
    # .alive command
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.alive$'))
    async def alive(event):
        me = await client.get_me()
        caption = (
            "⚡ **Userbot is Active & Online** ⚡\n\n"
            f"👤 **Master:** KESHAV \n"
            "⚙️ **Engine:** Telethon \n"
            "🚀 **Status:** All systems operational!"
        )
        await event.edit(caption)

    # .purge command (Reply to a message to delete everything below it)
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.purge$'))
    async def purge(event):
        reply = await event.get_reply_message()
        if not reply:
            return await event.edit("⚠️ Kisi message ko reply karke `.purge` likho!")
        
        await event.edit("🗑️ **Purging messages...**")
        msg_id = reply.id
        chat = await event.get_input_chat()
        
        messages = []
        async for msg in client.iter_messages(chat, min_id=msg_id - 1):
            messages.append(msg)
            if len(messages) >= 100:
                await client.delete_messages(chat, messages)
                messages = []
        if messages:
            await client.delete_messages(chat, messages)

    # .type command (Typewriter effect: .type your text)
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.type (.+)'))
    async def typewriter(event):
        text = event.pattern_match.group(1)
        typing_symbol = "▌"
        current_text = ""
        
        for char in text:
            current_text += char
            try:
                await event.edit(current_text + typing_symbol)
                await asyncio.sleep(0.08)
            except Exception:
                pass
        await event.edit(current_text)
