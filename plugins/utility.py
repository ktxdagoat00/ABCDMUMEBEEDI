import time
import asyncio
from telethon import events

CMD_MANUAL = {
    "alive": {"usage": ".alive", "desc": "Check userbot system status and uptime.", "example": ".alive"},
    "ping": {"usage": ".ping", "desc": "Measure cloud server response latency in milliseconds.", "example": ".ping"},
    "song": {"usage": ".song <query/link>", "desc": "Search and download high-bitrate MP3 audio with tags.", "example": ".song Kesariya"},
    "trim": {"usage": ".trim <start> <end> (reply)", "desc": "Fast lossless video/audio trimming by start & end timestamps.", "example": "Reply to video -> .trim 01:01 11:39"},
    "save": {"usage": ".save (reply)", "desc": "Transfer any replied media, restricted text, or link to Saved Messages.", "example": "Reply to media -> .save"},
    "spymode": {"usage": ".spymode on | off", "desc": "Automatically capture and store View-Once / Self-destruct media secretly.", "example": ".spymode on"},
    "pfp": {"usage": ".pfp (reply)", "desc": "Directly set replied image as your Telegram profile photo.", "example": "Reply to image -> .pfp"},
    "ytdl": {"usage": ".ytdl <link>", "desc": "Download direct video file from YouTube, Shorts, or Reels link.", "example": ".ytdl https://youtu.be/..."},
    "tts": {"usage": ".tts <text/reply>", "desc": "Convert written text into a playable voice message note.", "example": ".tts Hello bhai kaise ho"},
    "afk": {"usage": ".afk <reason>", "desc": "Set dynamic AFK status. Auto-logs all mentions and DMs while you're away.", "example": ".afk Busy studying"},
    "clone": {"usage": ".clone <user/reply>", "desc": "Completely clone target user's Name, Bio, PFP, and stealth username.", "example": ".clone @target"},
    "revert": {"usage": ".revert", "desc": "Restore your original profile identity (Name, Bio, Username, PFP).", "example": ".revert"},
    "ghost": {"usage": ".ghost <seconds> <text>", "desc": "Send a message that self-destructs after specified seconds.", "example": ".ghost 5 Secret message"},
    "antitag": {"usage": ".antitag <user/reply>", "desc": "Auto-deletes any incoming message from target if they mention/reply to you.", "example": ".antitag @spammer"},
    "unantitag": {"usage": ".unantitag <user/reply>", "desc": "Remove anti-tag deletion rule from target user.", "example": ".unantitag @spammer"},
    "tagall": {"usage": ".tagall <message>", "desc": "Tag all members in the current group with custom text.", "example": ".tagall Important meeting!"},
    "cancel": {"usage": ".cancel", "desc": "Stop ongoing active .tagall loop immediately.", "example": ".cancel"},
    "spam": {"usage": ".spam <count> <delay> <text>", "desc": "Send loop messages with controlled delay (max 20).", "example": ".spam 5 1 Hello"},
    "promote": {"usage": ".promote <1-3> (reply)", "desc": "Promote replied member to Admin with tiered permissions (1=Basic, 3=Full).", "example": "Reply -> .promote 2"},
    "demote": {"usage": ".demote (reply/user)", "desc": "Revoke admin rights of replied user back to normal member.", "example": "Reply -> .demote"},
    "ban": {"usage": ".ban <id/reply> <reason>", "desc": "Ban user permanently from group with logged reason.", "example": ".ban @spammer Raid"},
    "unban": {"usage": ".unban <id>", "desc": "Remove ban restriction from specified user ID/username.", "example": ".unban 12345678"},
    "lock": {"usage": ".lock <id/reply>", "desc": "Continuously delete every message sent by target user in chat.", "example": ".lock @annoying"},
    "unlock": {"usage": ".unlock <id/reply>", "desc": "Remove continuous auto-delete lock from target user.", "example": ".unlock @annoying"},
    "gclock": {"usage": ".gclock", "desc": "Full lockdown: Restrict all group members from sending messages.", "example": ".gclock"},
    "gcunlock": {"usage": ".gcunlock", "desc": "Release group lockdown: Allow members to talk again.", "example": ".gcunlock"},
    "taglock": {"usage": ".taglock <msg_link>", "desc": "Auto-delete any user replying to target message thread.", "example": ".taglock https://t.me/c/.../10"},
    "untaglock": {"usage": ".untaglock", "desc": "Lift reply restrictions on the locked thread.", "example": ".untaglock"},
    "del": {"usage": ".del (reply)", "desc": "Instantly delete replied message.", "example": "Reply -> .del"},
    "delall": {"usage": ".delall (reply)", "desc": "Purge all recent messages sent by replied user in current group.", "example": "Reply -> .delall"},
    "purgeme": {"usage": ".purgeme", "desc": "Purge all your own messages sent in the current chat.", "example": ".purgeme"},
    "purge": {"usage": ".purge (reply)", "desc": "Batch purge all messages from replied message till current.", "example": "Reply -> .purge"},
    "info": {"usage": ".info <user/reply>", "desc": "Extract user intel, DC info, registration estimate and usernames.", "example": ".info @username"},
    "type": {"usage": ".type <text>", "desc": "Animate typewriter effect in message letter-by-letter.", "example": ".type System online."},
    "tr": {"usage": ".tr <text/reply>", "desc": "Translate target message into Hindi instantly.", "example": ".tr How are you?"},
    "calc": {"usage": ".calc <math>", "desc": "Safe mathematical calculation evaluator.", "example": ".calc 45*120/(3+7)"},
    "eval": {"usage": ".eval <code>", "desc": "Execute Python expression asynchronously on the fly.", "example": ".eval 2**10"}
}

def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ping$'))
    async def ping(event):
        start = time.time()
        msg = await event.edit("```text\n┌───「 ⚡ 𝗣𝗜𝗡𝗚𝗜𝗡𝗚... 」\n└───「 🛰️ 𝗦𝗘𝗡𝗗𝗜𝗡𝗚 𝗣𝗔𝗖𝗞𝗘𝗧𝗦 」\n```")
        end = time.time()
        ms = round((end - start) * 1000, 2)
        reply_text = (
            "```text\n"
            "┌───「 ⚡ 𝗣𝗢𝗡𝗚 ⚡ 」\n"
            "│\n"
            f"├─ ⚡ 𝗟𝗔𝗧𝗘𝗡𝗖𝗬 :: {ms} ms\n"
            "├─ 🛰️ 𝗦𝗘𝗥𝗩𝗘𝗥  :: Render Cloud\n"
            "├─ 🛡️ 𝗦𝗧𝗔𝗧𝗨𝗦  :: 100% Stable\n"
            "│\n"
            "└───「 🔥 𝗞𝗘𝗦𝗛𝗔𝗩-𝗨𝗦𝗘𝗥𝗕𝗢𝗧 」\n"
            "```"
        )
        await msg.edit(reply_text)

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.alive$'))
    async def alive(event):
        reply_text = (
            "```text\n"
            "┌───「 ⚡ 𝗦𝗬𝗦𝗧𝗘𝗠 𝗢𝗡𝗟𝗜𝗡𝗘 ⚡ 」\n"
            "│\n"
            "├─ 👤 𝗠𝗔𝗦𝗧𝗘𝗥   :: K E S H A V\n"
            "├─ ⚙️ 𝗘𝗡𝗚𝗜𝗡𝗘   :: Telethon v1.34\n"
            "├─ 🌐 𝗨𝗣𝗧𝗜𝗠𝗘   :: 24/7 Active\n"
            "├─ 🛡️ 𝗦𝗘𝗖𝗨𝗥𝗜𝗧𝗬 :: Encrypted\n"
            "│\n"
            "└───「 ⚡ 𝗔𝗟𝗟 𝗦𝗬𝗦𝗧𝗘𝗠𝗦 𝗚𝗢 」\n"
            "```"
        )
        await event.edit(reply_text)

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.help(?:\s+([a-zA-Z0-9_]+))?$'))
    async def help_menu(event):
        cmd_query = event.pattern_match.group(1)

        if cmd_query:
            cmd = cmd_query.lower().lstrip(".")
            if cmd in CMD_MANUAL:
                info = CMD_MANUAL[cmd]
                manual_card = (
                    "```text\n"
                    f"╔════════「 📖 MANUAL: .{cmd.upper()} 」════════╗\n"
                    "║\n"
                    f"╠─ 📌 𝗨𝗦𝗔𝗚𝗘   :: {info['usage']}\n"
                    f"╠─ 📝 𝗜𝗡𝗙𝗢    :: {info['desc']}\n"
                    f"╠─ 💡 𝗘𝗫𝗔𝗠𝗣𝗟𝗘 :: {info['example']}\n"
                    "║\n"
                    "╚══════════════════════════════════════════╝\n"
                    "```"
                )
                await event.edit(manual_card)
                return
            else:
                await event.edit(f"```text\n[!] Unknown command '.{cmd}'. Use .help to list all commands.\n```")
                return

        reply_text = (
            "```text\n"
            "╔════════「 🛠️ 𝗞𝗘𝗦𝗛𝗔𝗩 𝗖𝗢𝗡𝗧𝗥𝗢𝗟 𝗣𝗔𝗡𝗘𝗟 」════════╗\n"
            "║ 💡 Tip: Type .help <cmd> for usage & syntax\n"
            "║\n"
            "╠══「 ⚡ 𝗦𝗬𝗦𝗧𝗘𝗠 & 𝗦𝗧𝗔𝗧𝗨𝗦 」══\n"
            "╠─ 01. .alive          :: System online & telemetry\n"
            "╠─ 02. .ping           :: Cloud server latency\n"
            "╠─ 03. .help <cmd>     :: Command manual / list\n"
            "║\n"
            "╠══「 🕵️ 𝗦𝗧𝗘𝗔𝗟𝗧𝗛 & 𝗜𝗗𝗘𝗡𝗧𝗜𝗧𝗬 」══\n"
            "╠─ 04. .clone <user>   :: Spoof full target identity\n"
            "╠─ 05. .revert         :: Restore 100% original profile\n"
            "╠─ 06. .ghost <sec>    :: Timed self-destruct message\n"
            "╠─ 07. .antitag <user> :: Auto-delete target's mentions\n"
            "╠─ 08. .unantitag <u>  :: Remove target anti-tag lock\n"
            "║\n"
            "╠══「 📥 𝗠𝗘𝗗𝗜𝗔 & 𝗖𝗔𝗣𝗧𝗨𝗥𝗘 」══\n"
            "╠─ 09. .song <name>    :: Download high-quality MP3\n"
            "╠─ 10. .trim <s/e>     :: Fast lossless media trimmer\n"
            "╠─ 11. .save           :: Save replied media/text to Saved\n"
            "╠─ 12. .spymode <o/f>  :: Intercept & save View-Once\n"
            "╠─ 13. .pfp            :: Set replied media as PFP\n"
            "╠─ 14. .ytdl <link>    :: Video/Shorts/Reel downloader\n"
            "╠─ 15. .tts <text>     :: Text-to-Speech voice note\n"
            "║\n"
            "╠══「 💤 𝗔𝗨𝗧𝗢𝗠𝗔𝗧𝗜𝗢𝗡 & 𝗔𝗙𝗞 」══\n"
            "╠─ 16. .afk <reason>   :: Dynamic AFK & mention logger\n"
            "╠─ 17. .tagall <msg>   :: Mention group members\n"
            "╠─ 18. .cancel         :: Abort active tagall process\n"
            "╠─ 19. .spam <c> <d>   :: Controlled flood loop\n"
            "║\n"
            "╠══「 🛡️ 𝗖𝗛𝗔𝗧 & 𝗔𝗗𝗠𝗜𝗡 𝗦𝗘𝗖𝗨𝗥𝗜𝗧𝗬 」══\n"
            "╠─ 20. .promote <1-3>  :: Member promotion (3 tiers)\n"
            "╠─ 21. .demote <user>  :: Revoke admin rights\n"
            "╠─ 22. .ban <id/rep>   :: Ban entity with reason\n"
            "╠─ 23. .unban <id>     :: Revoke ban restriction\n"
            "╠─ 24. .lock <id/rep>  :: Continuous wipe of user's msgs\n"
            "╠─ 25. .unlock <id>    :: Release user deletion lock\n"
            "╠─ 26. .gclock         :: Total group shutdown\n"
            "╠─ 27. .gcunlock       :: Lift group shutdown\n"
            "╠─ 28. .taglock <url>  :: Block replies to target message\n"
            "╠─ 29. .untaglock      :: Release locked thread replies\n"
            "║\n"
            "╠══「 🧹 𝗣𝗨𝗥𝗚𝗘 & 𝗖𝗟𝗘𝗔𝗡𝗨𝗣 」══\n"
            "╠─ 30. .del            :: Instant delete replied message\n"
            "╠─ 31. .delall         :: Purge all messages from user\n"
            "╠─ 32. .purgeme        :: Purge own chat history\n"
            "╠─ 33. .purge          :: Batch purge from replied msg\n"
            "║\n"
            "╠══「 🛠️ 𝗨𝗧𝗜𝗟𝗜𝗧𝗜𝗘𝗦 & 𝗖𝗢𝗗𝗘 」══\n"
            "╠─ 34. .info <user>    :: Intel extraction & history\n"
            "╠─ 35. .type <text>    :: Typewriter terminal animation\n"
            "╠─ 36. .tr <text>      :: Instant Hindi translation\n"
            "╠─ 37. .calc <math>    :: Compute math expressions\n"
            "╠─ 38. .eval <code>    :: Execute asynchronous Python\n"
            "║\n"
            "╚═════════════「 ⚡ 𝗖𝗬𝗕𝗘𝗥-𝗘𝗫𝗘𝗖 ⚡ 」═════════════╝\n"
            "```"
        )
        await event.edit(reply_text)

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.calc\s+(.+)'))
    async def calculate(event):
        expr = event.pattern_match.group(1)
        try:
            allowed = set("0123456789+-*/(). ")
            if not all(c in allowed for c in expr):
                await event.edit("```text\n[!] ERROR: Invalid math syntax\n```")
                return
            result = eval(expr)
            reply_text = (
                "```text\n"
                "┌───「 🧮 𝗠𝗔𝗧𝗛 𝗖𝗢𝗥𝗘 」\n"
                f"├─ 𝗜𝗡𝗣𝗨𝗧  :: {expr}\n"
                f"├─ 𝗢𝗨𝗧𝗣𝗨𝗧 :: {result}\n"
                "└───「 ⚡ 𝗖𝗢𝗠𝗣𝗨𝗧𝗘𝗗 」\n"
                "```"
            )
            await event.edit(reply_text)
        except Exception as e:
            await event.edit(f"```text\n[!] EXCEPTION: {e}\n```")

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.purge$'))
    async def purge(event):
        reply = await event.get_reply_message()
        if not reply:
            await event.edit("```text\n[!] Reply to a message to purge from!\n```")
            return
        
        chat = await event.get_input_chat()
        from_id = reply.id
        total_deleted = 0
        batch = []

        await event.delete()

        async for msg in client.iter_messages(chat, min_id=from_id - 1, reverse=True):
            batch.append(msg.id)
            if len(batch) >= 100:
                await client.delete_messages(chat, batch)
                total_deleted += len(batch)
                batch = []
                await asyncio.sleep(0.3)

        if batch:
            await client.delete_messages(chat, batch)
            total_deleted += len(batch)

        notice = await client.send_message(
            chat,
            "```text\n"
            "┌───「 🧹 𝗧𝗢𝗧𝗔𝗟 𝗣𝗨𝗥𝗚𝗘 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘 」\n"
            f"└─ 🗑️ Cleaned :: {total_deleted} messages\n"
            "```"
        )
        await asyncio.sleep(2)
        await notice.delete()
