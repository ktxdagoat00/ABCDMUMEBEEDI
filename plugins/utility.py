import time
from telethon import events

CMD_MANUAL = {
    "ping": "Test bot connection and live latency response.",
    "alive": "Display the master system status dashboard.",
    "help": "Display interactive command directory and usage.",
    "gban": "Globally ban a target user across all channels and groups.",
    "ungban": "Revoke global ban for a target user across all chats.",
    "gmute": "Mute a target globally across all managed chats.",
    "ungmute": "Unmute a target user globally across all managed chats.",
    "gpin": "Broadcast and pin a replied message across all groups.",
    "ungpin": "Unpin all pinned messages across all managed chats.",
    "q": "Convert any replied text message to a Quotly sticker.",
    "q r": "Quote replied message including parent context in Quotly.",
    "kang": "Kang replied sticker/image into personal K E S H A V pack.",
    "audit": "Run deep chat X-Ray scanning (deleted, bots, humans, admins).",
    "audit clean": "Mass-kick all ghost/deleted accounts from the group."
}

def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ping$'))
    async def ping_handler(event):
        start = time.time()
        msg = await event.edit("```text\n┌───「 ⚡ PINGING SYSTEM... 」\n└───「 Probing Telethon Loop 」\n```")
        delta = round((time.time() - start) * 1000)
        card = (
            "```text\n"
            "╔════「 ⚡ 𝗞 𝗘 𝗦 𝗛 𝗔 𝗩  𝗣 𝗢 𝗡 𝗚 ⚡ 」════╗\n"
            "║\n"
            f"╠─ ⚡ LATENCY :: {delta}ms\n"
            "╠─ 🛰️ HOST    :: Render Cloud (24/7)\n"
            "║\n"
            "╚══════════════════════════════════════╝\n"
            "```"
        )
        await msg.edit(card)

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.alive$'))
    async def alive_handler(event):
        card = (
            "```text\n"
            "╔════「 ⚡ 𝗞 𝗘 𝗦 𝗛 𝗔 𝗩  𝗨 𝗦 𝗘 𝗥 𝗕 𝗢 𝗧 ⚡ 」════╗\n"
            "║\n"
            "╠─ 👤 MASTER  :: K E S H A V\n"
            "╠─ 🛰️ ENGINE  :: Telethon v1.42 (Py 3.14)\n"
            "╠─ ⚡ STATUS  :: Fully Operational & Online\n"
            "╠─ 🌐 CLOUD   :: Render Active Webhook\n"
            "║\n"
            "╚═══════════════════════════════════════════╝\n"
            "```"
        )
        await event.edit(card)

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.help(?:\s+(\w+))?'))
    async def help_handler(event):
        query = event.pattern_match.group(1)
        if query:
            q_lower = query.lower()
            if q_lower in CMD_MANUAL:
                doc = (
                    "```text\n"
                    f"╔════「 ⚡ 𝗠𝗔𝗡𝗨𝗔𝗟 :: .{q_lower} ⚡ 」════╗\n"
                    "║\n"
                    f"╠─ 📖 USAGE :: {CMD_MANUAL[q_lower]}\n"
                    "║\n"
                    "╚════════════════════════════════════╝\n"
                    "```"
                )
                await event.edit(doc)
            else:
                await event.edit(f"```text\n[!] Command '.{query}' not found in registry.\n```")
            return

        card = (
            "```text\n"
            "╔════「 ⚡ 𝗞 𝗘 𝗦 𝗛 𝗔 𝗩  𝗖 𝗢 𝗠 𝗠 𝗔 𝗡 𝗗 𝗦 ⚡ 」════╗\n"
            "║\n"
            "╠─ ⚙️ SYSTEM   :: .ping | .alive | .help\n"
            "╠─ 🛡️ ADMIN    :: .gban | .ungban | .gmute | .ungmute\n"
            "╠─ 📌 PINS     :: .gpin | .ungpin\n"
            "╠─ 🎨 STICKERS :: .q | .q r | .kang <emoji>\n"
            "╠─ 🔍 AUDIT    :: .audit | .audit clean\n"
            "║\n"
            "╠─ 💡 Type .help <cmd> for full documentation\n"
            "╚════════════════════════════════════════════╝\n"
            "```"
        )
        await event.edit(card)
