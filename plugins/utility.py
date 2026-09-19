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
            "╔════「 🛠️ 𝗞𝗘𝗦𝗛𝗔𝗩 𝗖𝗢𝗡𝗧𝗥𝗢𝗟 𝗣𝗔𝗡𝗘𝗟 」════╗\n"
            "║\n"
            "╠─ • .alive          :: Check system status\n"
            "╠─ • .ping           :: Check server ping\n"
            "╠─ • .ghost <sec>    :: Self-destructing msg\n"
            "╠─ • .antitag <user> :: Purge user replies/tags\n"
            "╠─ • .unantitag <u>  :: Remove anti-tag rule\n"
            "╠─ • .info <user>    :: User intel & name history\n"
            "╠─ • .type <text>    :: Typewriter terminal text\n"
            "╠─ • .del            :: Delete replied msg\n"
            "╠─ • .delall         :: Purge all msgs from user\n"
            "╠─ • .purgeme        :: Purge own msgs all-time\n"
            "╠─ • .purge          :: Purge replied msgs batch\n"
            "╠─ • .promote <1-3>  :: Promote member (3 tiers)\n"
            "╠─ • .demote <user>  :: Demote admin to member\n"
            "╠─ • .ban <id/rep>   :: Ban member with reason\n"
            "╠─ • .unban <id>     :: Unban member\n"
            "╠─ • .lock <id/rep>  :: Auto-delete user's msgs\n"
            "╠─ • .unlock <id>    :: Release user lock\n"
            "╠─ • .gclock         :: Total chat lockdown\n"
            "╠─ • .gcunlock       :: Release chat lockdown\n"
            "╠─ • .taglock <url>  :: Lock replies to target msg\n"
            "╠─ • .untaglock      :: Release locked replies\n"
            "╠─ • .tagall <msg>   :: Tag all members\n"
            "╠─ • .cancel         :: Stop active tagall\n"
            "╠─ • .spam <c> <d>   :: Flood msgs (max 20)\n"
            "╠─ • .tr <text>      :: Translate into Hindi\n"
            "╠─ • .calc <math>    :: Safe calculations\n"
            "╠─ • .eval <code>    :: Execute python code\n"
            "╠─ • .help           :: Show this panel\n"
            "║\n"
            "╚════════「 ⚡ 𝗖𝗬𝗕𝗘𝗥-𝗘𝗫𝗘𝗖 ⚡ 」════════╝\n"
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
        messages_to_delete = []
        async for msg in client.iter_messages(chat, min_id=reply.id - 1):
            messages_to_delete.append(msg.id)
            if len(messages_to_delete) >= 100:
                break
        
        if messages_to_delete:
            await client.delete_messages(chat, messages_to_delete)
        
        notice = await event.respond(
            "```text\n"
            "┌───「 🧹 𝗣𝗨𝗥𝗚𝗘 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘 」\n"
            f"└─ 🗑️ Cleaned :: {len(messages_to_delete)} messages\n"
            "```"
        )
        await asyncio.sleep(3)
        await notice.delete()
