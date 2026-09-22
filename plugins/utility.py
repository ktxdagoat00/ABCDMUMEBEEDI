import time
from telethon import events

CMD_MANUAL = {
    # SYSTEM & STATUS
    "alive": "System online status, uptime & telemetry.",
    "ping": "Cloud server latency check.",
    "help": "Command manual & dynamic interactive list.",
    
    # STEALTH & IDENTITY
    "clone": "Spoof full target identity (PFP, bio, name).",
    "revert": "Restore 100% original profile settings.",
    "ghost": "Timed self-destructing message (e.g. .ghost 5s).",
    "antitag": "Auto-delete target user mentions continuously.",
    "unantitag": "Remove target anti-tag lock.",
    
    # MEDIA & CAPTURE
    "song": "Download high-quality MP3 audio track.",
    "trim": "Fast lossless video/audio trimmer.",
    "save": "Save replied media/text cleanly to Saved Messages.",
    "spymode": "Intercept and save View-Once media.",
    "pfp": "Set replied media as profile picture.",
    "tts": "Convert text into voice note audio.",
    
    # AUTOMATION & AFK
    "afk": "Dynamic AFK mode with reason & mention logger.",
    "tagall": "Mention all group members with custom text.",
    "cancel": "Abort active tagall/mention loop.",
    "spam": "Controlled flood spam loop (.spam <count> <delay>).",
    
    # CHAT & ADMIN SECURITY
    "gban": "Globally ban a target user across all managed chats.",
    "ungban": "Revoke global ban for a target user across all chats.",
    "gmute": "Mute a target globally across all managed chats.",
    "ungmute": "Unmute a target user globally across all managed chats.",
    "gpin": "Broadcast and pin a replied message across all groups.",
    "ungpin": "Unpin all pinned messages across all managed chats.",
    "promote": "Promote target member with custom permissions (1-3).",
    "demote": "Revoke admin rights of a target user.",
    "ban": "Ban user from group with reason.",
    "unban": "Revoke ban restriction of user.",
    "lock": "Continuous wipe of target user's messages.",
    "unlock": "Release user message deletion lock.",
    "gclock": "Total group shutdown (mute all members).",
    "gcunlock": "Lift group shutdown (restore permissions).",
    "taglock": "Block replies to a specific target message.",
    "untaglock": "Release locked thread replies.",
    
    # PURGE & CLEANUP
    "del": "Instant delete replied message.",
    "delall": "Purge all messages from a specific user.",
    "purgeme": "Purge own sent chat history.",
    "purge": "Batch purge messages from replied message.",
    
    # UTILITIES & CODE
    "info": "Fetch user SangMata history & profile intel.",
    "type": "Typewriter terminal text animation.",
    "tr": "Instant translation to Hindi / target language.",
    "calc": "Compute mathematical expressions instantly.",
    "eval": "Execute asynchronous Python code safely.",

    # STICKERS & CONVERSION
    "q": "Convert replied text message to a Quotly sticker.",
    "q r": "Quote replied message including parent context in Quotly.",
    "kang": "Kang replied sticker/image into personal K E S H A V pack.",

    # AUDIT & SCANNER
    "audit": "Run deep chat X-Ray scanning (deleted, bots, humans, admins).",
    "audit clean": "Mass-kick all ghost/deleted accounts from the group.",
    "readall": "Mark all unread chats and channels as read in one click.",
    "secret": "Drop encrypted cipher message (.secret pwd | msg). Reply .unlock pwd."
}

def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ping$'))
    async def ping_handler(event):
        start = time.time()
        msg = await event.edit("```text\n┌───「 ⚡ PINGING SYSTEM... 」\n└───「 Probing Telethon Loop 」\n```")
        delta = round((time.time() - start) * 1000)
        card = (
            "```text\n"
            "╔════「 ⚡ �K E S H A V ⚡ 」════╗\n"
            "║\n"
            f"╠─ ⚡ LATENCY :: {delta}ms\n"
            "╠─ 👤 MASTER  :: K E S H A V\n"
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

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.help(?:\s+(.+))?'))
    async def help_handler(event):
        query = event.pattern_match.group(1)
        if query:
            q_clean = query.strip().lower()
            if q_clean.startswith("."):
                q_clean = q_clean[1:]
            if q_clean in CMD_MANUAL:
                doc = (
                    "```text\n"
                    f"╔════「 ⚡ 𝗠𝗔𝗡𝗨𝗔𝗟 :: .{q_clean} ⚡ 」════╗\n"
                    "║\n"
                    f"╠─ 📖 USAGE :: {CMD_MANUAL[q_clean]}\n"
                    "║\n"
                    "╚════════════════════════════════════╝\n"
                    "```"
                )
                await event.edit(doc)
            else:
                await event.edit(f"```text\n[!] Command '.{query}' not found in registry.\n```")
            return

        panel = (
            "```text\n"
            "╔════════「 🛠️ 𝗞𝗘𝗦𝗛𝗔𝗩 𝗖𝗢𝗡𝗧𝗥𝗢𝗟 𝗣𝗔𝗡𝗘𝗟 」════════╗\n"
            "║ 💡 Tip: Type .help <cmd> for usage & syntax\n"
            "║\n"
            "╠══「 ⚡️ 𝗦𝗬𝗦𝗧𝗘𝗠 & 𝗦𝗧𝗔𝗧𝗨𝗦 」══\n"
            "╠─ 01. .alive          :: System online & telemetry\n"
            "╠─ 02. .ping           :: Cloud server latency\n"
            "╠─ 03. .help <cmd>     :: Command manual / list\n"
            "║\n"
            "╠══「 🕵️ 𝗦𝗧𝗘𝗔𝗟𝗧𝗛 & 𝗜𝗗𝗘𝗡𝗧𝗜𝗧𝗬 」══\n"
            "╠─ 04. .clone <user>   :: Spoof full target identity\n"
            "╠─ 05. .revert         :: Restore 100% original profile\n"
            "╠─ 06. .ghost <s/ms>   :: Timed self-destruct (0.5s ok)\n"
            "╠─ 07. .antitag <user> :: Auto-delete target's mentions\n"
            "╠─ 08. .unantitag <u>  :: Remove target anti-tag lock\n"
            "║\n"
            "╠══「 📥 𝗠𝗘𝗗𝗜𝗔 & 𝗖𝗔𝗣𝗧𝗨𝗥𝗘 」══\n"
            "╠─ 09. .song <name>    :: Download high-quality MP3\n"
            "╠─ 10. .trim <s/e>     :: Fast lossless media trimmer\n"
            "╠─ 11. .save           :: Save replied media/text to Saved\n"
            "╠─ 12. .spymode <o/f>  :: Intercept & save View-Once\n"
            "╠─ 13. .pfp            :: Set replied media as PFP\n"
            "╠─ 14. .tts <text>     :: Text-to-Speech voice note\n"
            "║\n"
            "╠══「 💤 𝗔𝗨𝗧𝗢𝗠𝗔𝗧𝗜𝗢𝗡 & 𝗔𝗙𝗞 」══\n"
            "╠─ 15. .afk <reason>   :: Dynamic AFK & mention logger\n"
            "╠─ 16. .tagall <msg>   :: Mention group members\n"
            "╠─ 17. .cancel         :: Abort active tagall process\n"
            "╠─ 18. .spam <c> <d>   :: Controlled flood loop\n"
            "║\n"
            "╠══「 🛡️ 𝗖𝗛𝗔𝗧 & 𝗔𝗗𝗠𝗜𝗡 𝗦𝗘𝗖𝗨𝗥𝗜𝗧𝗬 」══\n"
            "╠─ 19. .gban <user>    :: Global Ban across all your chats\n"
            "╠─ 20. .ungban <user>  :: Global Unban across all your chats\n"
            "╠─ 21. .gmute <user>   :: Global Mute across all your chats\n"
            "╠─ 22. .ungmute <user> :: Global Unmute across all your chats\n"
            "╠─ 23. .gpin           :: Global Pin replied msg everywhere\n"
            "╠─ 24. .ungpin         :: Global Unpin across all chats\n"
            "╠─ 25. .promote <1-3>  :: Member promotion (3 tiers)\n"
            "╠─ 26. .demote <user>  :: Revoke admin rights\n"
            "╠─ 27. .ban <id/rep>   :: Ban entity with reason\n"
            "╠─ 28. .unban <id>     :: Revoke ban restriction\n"
            "╠─ 29. .lock <id/rep>  :: Continuous wipe of user's msgs\n"
            "╠─ 30. .unlock <id>    :: Release user deletion lock\n"
            "╠─ 31. .gclock         :: Total group shutdown\n"
            "╠─ 32. .gcunlock       :: Lift group shutdown\n"
            "╠─ 33. .taglock <url>  :: Block replies to target message\n"
            "╠─ 34. .untaglock      :: Release locked thread replies\n"
            "║\n"
            "╠══「 🧹 𝗣𝗨𝗥𝗚𝗘 & 𝗖𝗟𝗘𝗔𝗡𝗨𝗣 」══\n"
            "╠─ 35. .del            :: Instant delete replied message\n"
            "╠─ 36. .delall         :: Purge all messages from user\n"
            "╠─ 37. .purgeme        :: Purge own chat history\n"
            "╠─ 38. .purge          :: Batch purge from replied msg\n"
            "║\n"
            "╠══「 🛠️ 𝗨𝗧𝗜𝗟𝗜𝗧𝗜𝗘𝗦 & 𝗖𝗢𝗗𝗘 」══\n"
            "╠─ 39. .info <user>    :: SangMata history & intel\n"
            "╠─ 40. .type <text>    :: Typewriter terminal animation\n"
            "╠─ 41. .tr <text>      :: Instant Hindi translation\n"
            "╠─ 42. .calc <math>    :: Compute math expressions\n"
            "╠─ 43. .eval <code>    :: Execute asynchronous Python\n"
            "║\n"
            "╠══「 🎨 𝗦𝗧𝗜𝗖𝗞𝗘𝗥𝗦 & 𝗖𝗢𝗡𝗩𝗘𝗥𝗧 」══\n"
            "╠─ 44. .q              :: Convert text to Quotly sticker\n"
            "╠─ 45. .q r            :: Quotly sticker with parent reply\n"
            "╠─ 46. .kang <emoji>   :: Kang sticker/photo to KESHAV pack\n"
            "║\n"
            "╠══「 🔍 𝗔𝗨𝗗𝗜𝗧 & 𝗫-𝗥𝗔𝗬 」══\n"
            "╠─ 47. .audit          :: Full chat X-Ray (bots/humans/ghosts)\n"
            "╠─ 48. .audit clean    :: Purge deleted accounts from chat\n"
            "║\n"
            "╠══「 🔐 𝗦𝗘𝗖𝗨𝗥𝗜𝗧𝗬 & 𝗦𝗧𝗘𝗔𝗟𝗧𝗛 𝗧𝗢𝗢𝗟𝗦 」══\n"
            "╠─ 49. .readall       :: Mark all unread chats as read\n"
            "╠─ 50. .secret <p|m>  :: Self-decrypting password cipher\n"
            "║\n"
            "╚═════════════「 ⚡️ 𝗖𝗬𝗕𝗘𝗥-𝗘𝗫𝗘𝗖 ⚡️ 」═════════════╝\n"
            "```"
        )
        await event.edit(panel)
