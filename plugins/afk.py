import time
from telethon import events

AFK_DATA = {
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
    if m > 0:
        return f"{m}m {s}s"
    return f"{s}s"

def setup(client):

    # Set AFK
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.afk(?:\s+(.+))?'))
    async def set_afk(event):
        reason = event.pattern_match.group(1) or "Busy right now."
        AFK_DATA["is_afk"] = True
        AFK_DATA["reason"] = reason.strip()
        AFK_DATA["time"] = time.time()

        card = (
            "```text\n"
            "╔════「 💤 𝗔𝗙𝗞 𝗠𝗢𝗗𝗘 𝗔𝗖𝗧𝗜𝗩𝗔𝗧𝗘𝗗 」════╗\n"
            "║\n"
            "╠─ 👤 MASTER :: K E S H A V\n"
            f"╠─ 📝 REASON :: {AFK_DATA['reason']}\n"
            "║\n"
            "╚═════════════════════════════════════╝\n"
            "```"
        )
        await event.edit(card)

    # Disable AFK when owner sends any new message
    @client.on(events.NewMessage(outgoing=True))
    async def unset_afk(event):
        if AFK_DATA["is_afk"] and not event.raw_text.startswith(".afk"):
            elapsed = get_readable_time(time.time() - AFK_DATA["time"])
            AFK_DATA["is_afk"] = False
            msg = await event.respond(f"```text\n[✓] Master K E S H A V is back online!\nAFK duration: {elapsed}\n```")
            AFK_DATA["reason"] = ""

    # Responder for mentions and private DMs
    @client.on(events.NewMessage(incoming=True))
    async def afk_notifier(event):
        if not AFK_DATA["is_afk"]:
            return

        is_dm = event.is_private
        is_tag = event.mentioned

        if is_dm or is_tag:
            elapsed = get_readable_time(time.time() - AFK_DATA["time"])
            card = (
                "```text\n"
                "╔════「 ⚡ 𝗠𝗔𝗦𝗧𝗘𝗥 𝗜𝗦 𝗔𝗙𝗞 ⚡ 」════╗\n"
                "║\n"
                "╠─ 👤 USER   :: K E S H A V\n"
                f"╠─ 📝 REASON :: {AFK_DATA['reason']}\n"
                f"╠─ ⏳ SINCE  :: {elapsed} ago\n"
                "║\n"
                "╚══════════════════════════════════╝\n"
                "```"
            )
            await event.reply(card)
