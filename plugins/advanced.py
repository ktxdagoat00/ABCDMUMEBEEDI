import asyncio
import time
import math
from telethon import events

AFK_DATA = {"status": False, "reason": None, "time": None}
TAG_ACTIVE = {}

def setup(client):
    # .tagall command
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.tagall(?:\s+(.*))?'))
    async def tagall(event):
        if not event.is_group:
            return await event.edit("⚠️ Ye command sirf groups me kaam karti hai!")
        
        chat_id = event.chat_id
        TAG_ACTIVE[chat_id] = True
        
        custom_text = event.pattern_match.group(1) or "Hello everyone!"
        await event.delete()
        
        mentions = ""
        count = 0
        
        async for user in client.iter_participants(chat_id):
            # Check if stopped by .cancel / .stoptag
            if not TAG_ACTIVE.get(chat_id, False):
                await client.send_message(chat_id, "🛑 **Tagging stopped!**")
                return
            
            if user.bot or user.deleted:
                continue
                
            mentions += f"[\u2063](tg://user?id={user.id})"
            count += 1
            
            if count >= 5:
                await client.send_message(chat_id, f"📢 **{custom_text}**" + mentions)
                mentions = ""
                count = 0
                await asyncio.sleep(1.5)  # Flood ban se bachne ke liye safe delay
        
        if mentions and TAG_ACTIVE.get(chat_id, False):
            await client.send_message(chat_id, f"📢 **{custom_text}**" + mentions)
            
        TAG_ACTIVE[chat_id] = False

    # .cancel ya .stoptag to abort tagging
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.(?:cancel|stoptag)$'))
    async def stop_tag(event):
        chat_id = event.chat_id
        if TAG_ACTIVE.get(chat_id, False):
            TAG_ACTIVE[chat_id] = False
            await event.edit("🛑 **Stopping tagall...**")
        else:
            await event.edit("⚠️ **Koi tagall active nahi hai!**")

    # .afk command
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.afk(?:\s+(.*))?'))
    async def afk_on(event):
        reason = event.pattern_match.group(1) or "Busy right now"
        AFK_DATA["status"] = True
        AFK_DATA["reason"] = reason
        AFK_DATA["time"] = time.time()
        await event.edit(f"💤 **I am going AFK.**\n📝 **Reason:** `{reason}`")

    # AFK auto-turnoff when you send a message
    @client.on(events.NewMessage(outgoing=True))
    async def afk_off(event):
        if AFK_DATA["status"] and not event.raw_text.startswith(".afk"):
            AFK_DATA["status"] = False
            spent = round(time.time() - AFK_DATA["time"])
            mins, secs = divmod(spent, 60)
            hrs, mins = divmod(mins, 60)
            time_str = f"{hrs}h {mins}m {secs}s" if hrs else (f"{mins}m {secs}s" if mins else f"{secs}s")
            await event.respond(f"⚡ **I'm back online!**\n⏳ **Was AFK for:** `{time_str}`")

    # AFK auto-reply when someone mentions or DMs you
    @client.on(events.NewMessage(incoming=True))
    async def afk_reply(event):
        if not AFK_DATA["status"]:
            return
        
        if event.is_private or event.mentioned:
            spent = round(time.time() - AFK_DATA["time"])
            mins, secs = divmod(spent, 60)
            hrs, mins = divmod(mins, 60)
            time_str = f"{hrs}h {mins}m {secs}s" if hrs else (f"{mins}m {secs}s" if mins else f"{secs}s")
            reply_text = (
                "🤖 **Auto-Reply:** Master is currently **AFK**.\n"
                f"📝 **Reason:** `{AFK_DATA['reason']}`\n"
                f"⏳ **Since:** `{time_str} ago`"
            )
            await event.reply(reply_text)

    # .calc command
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.calc (.+)'))
    async def calc(event):
        expr = event.pattern_match.group(1).strip()
        safe_dict = {"__builtins__": None, "math": math, "abs": abs, "round": round}
        try:
            res = eval(expr, safe_dict)
            await event.edit(f"🧮 **Expression:** `{expr}`\n🔢 **Result:** `{res}`")
        except Exception as e:
            await event.edit(f"⚠️ **Error:** `{e}`")
