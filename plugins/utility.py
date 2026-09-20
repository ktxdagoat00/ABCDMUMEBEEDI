import time
import asyncio
from telethon import events
from telethon.tl.types import User

CMD_MANUAL = {
    "alive": {"usage": ".alive", "desc": "Check system online status and telemetry.", "example": ".alive"},
    "ping": {"usage": ".ping", "desc": "Measure cloud server response latency.", "example": ".ping"},
    "song": {"usage": ".song <name>", "desc": "Download high-bitrate MP3 audio.", "example": ".song Kesariya"},
    "trim": {"usage": ".trim <start> <end>", "desc": "Fast lossless media trimmer.", "example": ".trim 00:10 00:40"},
    "save": {"usage": ".save (reply)", "desc": "Transfer any media/text to Saved Messages.", "example": "Reply -> .save"},
    "spymode": {"usage": ".spymode on | off", "desc": "Capture View-Once media secretly to Saved.", "example": ".spymode on"},
    "pfp": {"usage": ".pfp (reply)", "desc": "Directly set replied image as profile photo.", "example": "Reply -> .pfp"},
    "tts": {"usage": ".tts <text>", "desc": "Convert text into a playable voice note.", "example": ".tts Namaste bhai"},
    "afk": {"usage": ".afk <reason>", "desc": "Dynamic AFK status with mention logs.", "example": ".afk Lunch break"},
    "ghost": {"usage": ".ghost <sec> <text>", "desc": "Timed self-destructing text (e.g. 0.5s).", "example": ".ghost 0.5 Boom"},
    "gban": {"usage": ".gban <user/reply>", "desc": "Global Ban: Ban user from all your admin groups.", "example": ".gban @spammer"},
    "ungban": {"usage": ".ungban <user/reply>", "desc": "Global Unban: Lift ban across all your admin groups.", "example": ".ungban @user"},
    "gmute": {"usage": ".gmute <user/reply>", "desc": "Global Mute: Mute user in all your admin groups.", "example": ".gmute @spammer"},
    "ungmute": {"usage": ".ungmute <user/reply>", "desc": "Global Unmute: Allow user to talk again in all chats.", "example": ".ungmute @user"},
    "gpin": {"usage": ".gpin (reply)", "desc": "Global Pin: Forward & pin replied message across all your groups.", "example": "Reply -> .gpin"},
    "ungpin": {"usage": ".ungpin (reply)", "desc": "Global Unpin: Unpin messages across all your groups.", "example": "Reply -> .ungpin"},
    "clone": {"usage": ".clone <user/reply>", "desc": "Clone target user's Name, Bio, and PFP.", "example": ".clone @target"},
    "revert": {"usage": ".revert", "desc": "Restore original profile identity.", "example": ".revert"},
    "info": {"usage": ".info <user/reply>", "desc": "Deep user intel with real-time SangMata history.", "example": ".info @user"},
    "purge": {"usage": ".purge (reply)", "desc": "Batch purge all messages from replied message till latest.", "example": "Reply -> .purge"}
}

def setup(client):

    # --- .info with Direct SangMata Input Engine ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.info(?:\s+(.+))?'))
    async def user_info(event):
        reply = await event.get_reply_message()
        user_arg = event.pattern_match.group(1)
        user = None

        status = await event.edit("```text\n┌───「 🕵️ 𝗙𝗘𝗧𝗖𝗛𝗜𝗡𝗚 𝗜𝗡𝗧𝗘𝗟... 」\n└───「 🛰️ Scanning SangMata Records 」\n```")

        if reply:
            user = await reply.get_sender()
        elif user_arg:
            try:
                user = await client.get_entity(int(user_arg) if user_arg.isdigit() else user_arg)
            except Exception as e:
                await status.edit(f"```text\n[!] User not found: {e}\n```")
                return
        else:
            user = await event.get_sender()

        if not user or not isinstance(user, User):
            await status.edit("```text\n[!] Please specify or reply to a valid Telegram user.\n```")
            return

        uid = user.id
        first_name = user.first_name or "N/A"
        last_name = user.last_name or ""
        full_name = f"{first_name} {last_name}".strip()
        username = f"@{user.username}" if getattr(user, 'username', None) else "None"
        dc_id = getattr(user.photo, 'dc_id', 'Unknown') if getattr(user, 'photo', None) else "No PFP"
        is_bot = "Yes 🤖" if getattr(user, 'bot', False) else "No 👤"
        is_scam = "YES ⚠️" if getattr(user, 'scam', False) else "Clean 🛡️"

        # Direct Input Query to SangMata (Sending raw UID / username)
        history_text = "No history recorded for this user."
        target_bots = ["@SangMata_beta_bot", "@SangMata_BOT"]

        for sbot in target_bots:
            try:
                async with client.conversation(sbot, timeout=6) as conv:
                    # Send direct raw User ID
                    await conv.send_message(str(uid))
                    resp = await conv.get_response()
                    await conv.mark_read()
                    
                    if resp and resp.text:
                        raw = resp.text.strip()
                        # If bot asks to /start first, handle it
                        if "/start" in raw:
                            await conv.send_message("/start")
                            await conv.get_response()
                            await conv.send_message(str(uid))
                            resp = await conv.get_response()
                            raw = resp.text.strip() if resp else ""
                        
                        if raw:
                            history_text = raw
                            break
            except Exception:
                continue

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
            "╠══「 📜 𝗦𝗔𝗡𝗚𝗠𝗔𝗧𝗔 𝗛𝗜𝗦𝗧𝗢𝗥𝗬 」══\n"
            f"{history_text}\n"
            "║\n"
            "╚══════════════════════════════════════════╝\n"
            "```"
        )
        await status.edit(card)

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
