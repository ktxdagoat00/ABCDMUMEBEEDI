import time
import asyncio
from telethon import events

def setup(client):
    
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ping$'))
    async def ping(event):
        start = time.time()
        msg = await event.edit("🏓 **Pinging...**")
        end = time.time()
        ms = round((end - start) * 1000, 2)
        await msg.edit(f"🔥 **Pong!**\n⚡ Latency: `{ms} ms`")

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.alive$'))
    async def alive(event):
        await event.edit(
            "⚡ **Userbot is Active & Online** ⚡\n\n"
            f"👤 **Master:** KESHAV\n"
            f"⚙️ **Engine:** Telethon\n"
            f"🚀 **Status:** All systems operational!"
        )

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.help$'))
    async def help_menu(event):
        help_text = (
            "🛠️ **KESHAV's Userbot Help Menu** 🛠️\n\n"
            "• `.alive` - Check if bot is running\n"
            "• `.ping` - Check server latency\n"
            "• `.tagall <text>` - Tag group members in batches\n"
            "• `.cancel` - Stop ongoing tagall process\n"
            "• `.purge` - Delete multiple messages quickly\n"
            "• `.afk <reason>` - Set status as Away From Keyboard\n"
            "• `.calc <expr>` - Basic mathematical calculations\n"
            "• `.help` - Show this help menu"
        )
        await event.edit(help_text)

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.calc\s+(.+)'))
    async def calculate(event):
        expr = event.pattern_match.group(1)
        try:
            # Safe evaluation for basic math
            allowed_chars = set("0123456789+-*/(). ")
            if not all(c in allowed_chars for c in expr):
                await event.edit("❌ **Invalid characters in expression!**")
                return
            result = eval(expr)
            await event.edit(f"🧮 **Calculation:**\n`{expr} = {result}`")
        except Exception as e:
            await event.edit(f"❌ **Error:** `{e}`")

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.purge$'))
    async def purge(event):
        reply = await event.get_reply_message()
        if not reply:
            await event.edit("❌ **Kisi message ko reply karke .purge likho!**")
            return
        
        chat = await event.get_input_chat()
        messages_to_delete = []
        async for msg in client.iter_messages(chat, min_id=reply.id - 1):
            messages_to_delete.append(msg.id)
            if len(messages_to_desktop >= 100):  # safety batch limit
                break
        
        # Delete messages in chunks
        if messages_to_delete:
            await client.delete_messages(chat, messages_to_delete)
        
        notification = await event.respond(f"🧹 **Purged {len(messages_to_delete)} messages successfully!**")
        await asyncio.sleep(3)
        await notification.delete()
