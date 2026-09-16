import time
import asyncio
from telethon import events

afk_state = {
    "is_afk": False,
    "reason": "",
    "time": 0
}

def get_readable_time(seconds):
    count = int(seconds)
    m, s = divmod(count, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}h {m}m {s}s"
    elif m > 0:
        return f"{m}m {s}s"
    return f"{s}s"

def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.afk(?:\s+(.*))?'))
    async def set_afk(event):
        reason = event.pattern_match.group(1) or "Busy right now."
        afk_state["is_afk"] = True
        afk_state["reason"] = reason
        afk_state["time"] = time.time()
        
        reply_text = (
            "```text\n"
            "┌───「 💤 𝗔𝗙𝗞 𝗠𝗢𝗗𝗘 𝗔𝗖𝗧𝗜𝗩𝗔𝗧𝗘𝗗 」\n"
            "│\n"
            f"├─ 📝 𝗥𝗘𝗔𝗦𝗢𝗡 :: {reason}\n"
            "├─ 🛰️ 𝗦𝗧𝗔𝗧𝗨𝗦 :: Offline / Inactive\n"
            "│\n"
            "└───「 ⚡ 𝗦𝗡𝗢𝗢𝗭𝗘 𝗖𝗢𝗥𝗘 」\n"
            "```"
        )
        await event.edit(reply_text)

    @client.on(events.NewMessage(incoming=True))
    async def afk_reply(event):
        if not afk_state["is_afk"]:
            return
        
        if event.is_private or event.mentioned:
            elapsed = get_readable_time(time.time() - afk_state["time"])
            reply_text = (
                "```text\n"
                "┌───「 ⚠️ 𝗨𝗦𝗘𝗥 𝗜𝗦 𝗖𝗨𝗥𝗥𝗘𝗡𝗧𝗟𝗬 𝗔𝗙𝗞 」\n"
                "│\n"
                "├─ 👤 𝗠𝗔𝗦𝗧𝗘𝗥 :: K E S H A V\n"
                f"├─ ⏳ 𝗦𝗜𝗡𝗖𝗘  :: {elapsed}\n"
                f"├─ 📝 𝗥𝗘𝗔𝗦𝗢𝗡 :: {afk_state['reason']}\n"
                "│\n"
                "└───「 🛰️ 𝗔𝗨𝗧𝗢-𝗥𝗘𝗦𝗣𝗢𝗡𝗗𝗘𝗥 」\n"
                "```"
            )
            await event.reply(reply_text)

    @client.on(events.NewMessage(outgoing=True))
    async def auto_unafk(event):
        if event.raw_text.startswith(".afk"):
            return
        
        if afk_state["is_afk"]:
            elapsed = get_readable_time(time.time() - afk_state["time"])
            afk_state["is_afk"] = False
            notice = await event.respond(
                "```text\n"
                "┌───「 ⚡ 𝗕𝗔𝗖𝗞 𝗢𝗡𝗟𝗜𝗡𝗘 ⚡ 」\n"
                "│\n"
                f"├─ ⏳ 𝗔𝗙𝗞 𝗧𝗜𝗠𝗘 :: {elapsed}\n"
                "├─ 🛡️ 𝗦𝗧𝗔𝗧𝗨𝗦   :: Fully Responsive\n"
                "│\n"
                "└───「 🔥 𝗞𝗘𝗦𝗛𝗔𝗩-𝗨𝗦𝗘𝗥𝗕𝗢𝗧 」\n"
                "```"
            )
            await asyncio.sleep(4)
            await notice.delete()
