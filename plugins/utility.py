import time
import asyncio
from telethon import events
from telethon.tl.types import User

# In-memory history tracking database
USER_NAME_HISTORY = {}
USER_UNAME_HISTORY = {}

CMD_MANUAL = {
    "alive": {"usage": ".alive", "desc": "Check userbot system status and uptime.", "example": ".alive"},
    "ping": {"usage": ".ping", "desc": "Measure cloud server response latency in milliseconds.", "example": ".ping"},
    "song": {"usage": ".song <query/link>", "desc": "Search and download high-bitrate MP3 audio with tags.", "example": ".song Kesariya"},
    "trim": {"usage": ".trim <start> <end> (reply)", "desc": "Fast lossless video/audio trimming by timestamps.", "example": "Reply -> .trim 01:01 11:39"},
    "save": {"usage": ".save (reply)", "desc": "Transfer replied media/text directly to Saved Messages.", "example": "Reply -> .save"},
    "spymode": {"usage": ".spymode on | off", "desc": "Capture and store View-Once media secretly to Saved Messages.", "example": ".spymode on"},
    "pfp": {"usage": ".pfp (reply)", "desc": "Directly set replied image as your profile photo.", "example": "Reply -> .pfp"},
    "ytdl": {"usage": ".ytdl <link>", "desc": "Download direct video from YouTube, Shorts, Reels link.", "example": ".ytdl https://youtu.be/..."},
    "tts": {"usage": ".tts <text/reply>", "desc": "Convert text into a playable voice message note.", "example": ".tts Hello bhai"},
    "afk": {"usage": ".afk <reason>", "desc": "Set dynamic AFK status with mention & DM logging.", "example": ".afk Out for dinner"},
    "ghost": {"usage": ".ghost <sec> <text>", "desc": "Self-destruct message supporting decimals (e.g. 0.5s).", "example": ".ghost 0.5 Poof!"},
    "gban": {"usage": ".gban <user/reply>", "desc": "Global Ban: Ban target user across all groups where you are admin.", "example": ".gban @spammer"},
    "gmute": {"usage": ".gmute <user/reply>", "desc": "Global Mute: Mute target user across all your groups.", "example": ".gmute @spammer"},
    "gpin": {"usage": ".gpin (reply)", "desc": "Global Pin: Forward & pin replied message across all your groups.", "example": "Reply -> .gpin"},
    "clone": {"usage": ".clone <user/reply>", "desc": "Clone target user's Name, Bio, and PFP.", "example": ".clone @target"},
    "revert": {"usage": ".revert", "desc": "Restore your original profile identity.", "example": ".revert"},
    "info": {"usage": ".info <user/reply>", "desc": "User intel with logged past name/username changes.", "example": ".info @user"},
    "purge": {"usage": ".purge (reply)", "desc": "Batch purge all messages from replied message till latest.", "example": "Reply -> .purge"}
}

def setup(client):

    # --- Live Name & Username History Tracker ---
    @client.on(events.NewMessage())
    async def history_logger(event):
        try:
            sender = await event.get_sender()
            if not isinstance(sender, User):
                return
            uid = sender.id
            curr_name = f"{sender.first_name or ''} {sender.last_name or ''}".strip()
            curr_uname = f"@{sender.username}" if sender.username else None

            if uid not in USER_NAME_HISTORY:
                USER_NAME_HISTORY[uid] = []
            if curr_name and curr_name not in USER_NAME_HISTORY[uid]:
                USER_NAME_HISTORY[uid].append(curr_name)

            if uid not in USER_UNAME_HISTORY:
                USER_UNAME_HISTORY[uid] = []
            if curr_uname and curr_uname not in USER_UNAME_HISTORY[uid]:
                USER_UNAME_HISTORY[uid].append(curr_uname)
        except Exception:
            pass

    # --- .info <user/reply> with History ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.info(?:\s+(.+))?'))
    async def user_info(event):
        reply = await event.get_reply_message()
        user_arg = event.pattern_match.group(1)
        user = None

        if reply:
            user = await reply.get_sender()
        elif user_arg:
            try:
                user = await client.get_entity(int(user_arg) if user_arg.isdigit() else user_arg)
            except Exception as e:
                await event.edit(f"```text\n[!] User not found: {e}\n```")
                return
        else:
            user = await event.get_sender()

        if not user:
            await event.edit("```text\n[!] Unable to fetch entity.\n```")
            return

        uid = user.id
        first_name = user.first_name or "N/A"
        last_name = user.last_name or ""
        full_name = f"{first_name} {last_name}".strip()
        username = f"@{user.username}" if getattr(user, 'username', None) else "None"
        dc_id = getattr(user.photo, 'dc_id', 'Unknown') if getattr(user, 'photo', None) else "No PFP"
        is_bot = "Yes 🤖" if getattr(user, 'bot', False) else "No 👤"
        is_scam = "YES ⚠️" if getattr(user, 'scam', False) else "Clean 🛡️"

        names = USER_NAME_HISTORY.get(uid, [full_name])
        unames = USER_UNAME_HISTORY.get(uid, [username])

        name_hist_str = " ➔ ".join(names[-3:]) if names else full_name
        uname_hist_str = " ➔ ".join(unames[-3:]) if unames else username

        card = (
            "```text\n"
            "╔════════「 🕵️ 𝗨𝗦𝗘𝗥 𝗜𝗡𝗧𝗘𝗟 𝗥𝗘𝗣𝗢𝗥𝗧 」════════╗\n"
            "║\n"
            f"╠─ 🆔 𝗨𝗦𝗘𝗥 𝗜𝗗    :: {uid}\n"
            f"╠─ 👤 𝗙𝗨𝗟𝗟 𝗡𝗔𝗠𝗘  :: {full_name}\n"
            f"╠─ 🏷️ 𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘  :: {username}\n"
            f"╠─ 🛰️ 𝗗𝗖 𝗜𝗗      :: {dc_id}\n"
            f"╠─ 🤖 𝗜𝗦 𝗕𝗢𝗧     :: {is_bot}\n"
            f"╠─ 🚨 𝗦𝗖𝗔𝗠/𝗙𝗔𝗞𝗘  :: {is_scam}\n"
            "║\n"
            "╠══「 📜 𝗥𝗘𝗖𝗢𝗥𝗗𝗘𝗗 𝗛𝗜𝗦𝗧𝗢𝗥𝗬 」══\n"
            f"╠─ 📝 𝗡𝗔𝗠𝗘𝗦     :: {name_hist_str}\n"
            f"╠─ 🔖 𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘𝗦 :: {uname_hist_str}\n"
            "║\n"
            "╚══════════════════════════════════════════╝\n"
            "```"
        )
        await event.edit(card)

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
            "╠─ 20. .gban <user>    :: Global Ban across all your chats\n"
            "╠─ 21. .gmute <user>   :: Global Mute across all your chats\n"
            "╠─ 22. .gpin           :: Global Pin replied msg everywhere\n"
            "╠─ 23. .promote <1-3>  :: Member promotion (3 tiers)\n"
            "╠─ 24. .demote <user>  :: Revoke admin rights\n"
            "╠─ 25. .ban <id/rep>   :: Ban entity with reason\n"
            "╠─ 26. .unban <id>     :: Revoke ban restriction\n"
            "╠─ 27. .lock <id/rep>  :: Continuous wipe of user's msgs\n"
            "╠─ 28. .unlock <id>    :: Release user deletion lock\n"
            "╠─ 29. .gclock         :: Total group shutdown\n"
            "╠─ 30. .gcunlock       :: Lift group shutdown\n"
            "╠─ 31. .taglock <url>  :: Block replies to target message\n"
            "╠─ 32. .untaglock      :: Release locked thread replies\n"
            "║\n"
            "╠══「 🧹 𝗣𝗨𝗥𝗚𝗘 & 𝗖𝗟𝗘𝗔𝗡𝗨𝗣 」══\n"
            "╠─ 33. .del            :: Instant delete replied message\n"
            "╠─ 34. .delall         :: Purge all messages from user\n"
            "╠─ 35. .purgeme        :: Purge own chat history\n"
            "╠─ 36. .purge          :: Batch purge from replied msg\n"
            "║\n"
            "╠══「 🛠️ 𝗨𝗧𝗜𝗟𝗜𝗧𝗜𝗘𝗦 & 𝗖𝗢𝗗𝗘 」══\n"
            "╠─ 37. .info <user>    :: Intel extraction & live history\n"
            "╠─ 38. .type <text>    :: Typewriter terminal animation\n"
            "╠─ 39. .tr <text>      :: Instant Hindi translation\n"
            "╠─ 40. .calc <math>    :: Compute math expressions\n"
            "╠─ 41. .eval <code>    :: Execute asynchronous Python\n"
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
            await event.edit(f"```text\n┌───「 🧮 𝗠𝗔𝗧𝗛 𝗖𝗢𝗥𝗘 」\n├─ 𝗜𝗡𝗣𝗨𝗧  :: {expr}\n├─ 𝗢𝗨𝗧𝗣𝗨𝗧 :: {result}\n└───「 ⚡ 𝗖𝗢𝗠𝗣𝗨𝗧𝗘𝗗 」\n```")
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
        notice = await client.send_message(chat, f"```text\n┌───「 🧹 𝗧𝗢𝗧𝗔𝗟 𝗣𝗨𝗥𝗚𝗘 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘 」\n└─ 🗑️ Cleaned :: {total_deleted} messages\n```")
        await asyncio.sleep(2)
        await notice.delete()
