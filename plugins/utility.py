import time
import asyncio
from telethon import events

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

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.help$'))
    async def help_menu(event):
        reply_text = (
            "```text\n"
            "╔════════「 🛠️ 𝗞𝗘𝗦𝗛𝗔𝗩 𝗖𝗢𝗡𝗧𝗥𝗢𝗟 𝗣𝗔𝗡𝗘𝗟 」════════╗\n"
            "║\n"
            "╠══「 ⚡ 𝗦𝗬𝗦𝗧𝗘𝗠 & 𝗦𝗧𝗔𝗧𝗨𝗦 」══\n"
            "╠─ 01. .alive          :: System online & telemetry\n"
            "╠─ 02. .ping           :: Cloud server latency\n"
            "╠─ 03. .help           :: Show categorized manual\n"
            "║\n"
            "╠══「 🕵️ 𝗦𝗧𝗘𝗔𝗟𝗧𝗛 & 𝗜𝗗𝗘𝗡𝗧𝗜𝗧𝗬 」══\n"
            "╠─ 04. .clone <user>   :: Spoof full target identity\n"
            "╠─ 05. .revert         :: Restore 100% original profile\n"
            "╠─ 06. .ghost <sec>    :: Timed self-destruct message\n"
            "╠─ 07. .antitag <user> :: Auto-delete target's mentions\n"
            "╠─ 08. .unantitag <u>  :: Remove target anti-tag lock\n"
            "║\n"
            "╠══「 📥 𝗠𝗘𝗗𝗜𝗔 & 𝗖𝗔𝗣𝗧𝗨𝗥𝗘 」══\n"
            "╠─ 09. .save           :: Save replied media/text to Saved\n"
            "╠─ 10. .spymode <o/f>  :: Intercept & save View-Once media\n"
            "╠─ 11. .pfp            :: Set replied media as PFP\n"
            "╠─ 12. .ytdl <link>    :: Video/Shorts/Reel downloader\n"
            "╠─ 13. .tts <text>     :: Text-to-Speech voice note\n"
            "║\n"
            "╠══「 💤 𝗔𝗨𝗧𝗢𝗠𝗔𝗧𝗜𝗢𝗡 & 𝗔𝗙𝗞 」══\n"
            "╠─ 14. .afk <reason>   :: Dynamic AFK & mention logger\n"
            "╠─ 15. .tagall <msg>   :: Mention group members\n"
            "╠─ 16. .cancel         :: Abort active tagall process\n"
            "╠─ 17. .spam <c> <d>   :: Controlled flood loop (max 20)\n"
            "║\n"
            "╠══「 🛡️ 𝗖𝗛𝗔𝗧 & 𝗔𝗗𝗠𝗜𝗡 𝗦𝗘𝗖𝗨𝗥𝗜𝗧𝗬 」══\n"
            "╠─ 18. .promote <1-3>  :: Member promotion (3 tiers)\n"
            "╠─ 19. .demote <user>  :: Revoke admin rights\n"
            "╠─ 20. .ban <id/rep>   :: Ban entity with reason\n"
            "╠─ 21. .unban <id>     :: Revoke ban restriction\n"
            "╠─ 22. .lock <id/rep>  :: Continuous wipe of user's msgs\n"
            "╠─ 23. .unlock <id>    :: Release user deletion lock\n"
            "╠─ 24. .gclock         :: Total group shutdown\n"
            "╠─ 25. .gcunlock       :: Lift group shutdown\n"
            "╠─ 26. .taglock <url>  :: Block replies to target message\n"
            "╠─ 27. .untaglock      :: Release locked thread replies\n"
            "║\n"
            "╠══「 🧹 𝗣𝗨𝗥𝗚𝗘 & 𝗖𝗟𝗘𝗔𝗡𝗨𝗣 」══\n"
            "╠─ 28. .del            :: Instant delete replied message\n"
            "╠─ 29. .delall         :: Purge all messages from user\n"
            "╠─ 30. .purgeme        :: Purge own chat history\n"
            "╠─ 31. .purge          :: Batch purge from replied msg\n"
            "║\n"
            "╠══「 🛠️ 𝗨𝗧𝗜𝗟𝗜𝗧𝗜𝗘𝗦 & 𝗖𝗢𝗗𝗘 」══\n"
            "╠─ 32. .info <user>    :: Intel extraction & history\n"
            "╠─ 33. .type <text>    :: Typewriter terminal animation\n"
            "╠─ 34. .tr <text>      :: Instant Hindi translation\n"
            "╠─ 35. .calc <math>    :: Compute math expressions\n"
            "╠─ 36. .eval <code>    :: Execute asynchronous Python\n"
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
