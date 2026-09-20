import asyncio
from telethon import events
from telethon.tl.types import MessageEntityMention, MessageEntityMentionName

ANTITAG_USERS = set()
MY_ID = None
MY_USERNAMES = []

async def init_identity(client):
    global MY_ID, MY_USERNAMES
    if MY_ID is None:
        me = await client.get_me()
        MY_ID = me.id
        names = []
        if getattr(me, 'username', None):
            names.append(me.username.lower())
        if hasattr(me, 'usernames') and me.usernames:
            for u in me.usernames:
                if getattr(u, 'username', None):
                    names.append(u.username.lower())
        MY_USERNAMES = list(set(names))

def setup(client):

    # --- .ghost <seconds> <text> ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ghost(?:\s+([0-9]+(?:\.[0-9]+)?))?(?:\s+(.*))?'))
    async def ghost_message(event):
        sec_str = event.pattern_match.group(1)
        text = event.pattern_match.group(2)

        if not sec_str or not text:
            await event.edit("```text\n[!] Usage: .ghost <seconds> <text>\nExample: .ghost 0.5 Secret message\n```")
            return

        try:
            wait_time = float(sec_str)
        except ValueError:
            await event.edit("```text\n[!] Invalid time format. Use seconds e.g. 0.5 or 3\n```")
            return

        await event.edit(text)
        await asyncio.sleep(wait_time)
        try:
            await event.delete()
        except Exception:
            pass

    # --- .antitag <user/reply> ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.antitag(?:\s+(.+))?'))
    async def enable_antitag(event):
        global ANTITAG_USERS
        reply = await event.get_reply_message()
        user_arg = event.pattern_match.group(1)
        target = None

        if reply:
            target = await reply.get_sender()
        elif user_arg:
            try:
                target = await client.get_entity(int(user_arg) if user_arg.isdigit() else user_arg)
            except Exception as e:
                await event.edit(f"```text\n[!] User not found: {e}\n```")
                return
        else:
            await event.edit("```text\n[!] Reply to user or provide username/ID.\nUsage: .antitag @user\n```")
            return

        ANTITAG_USERS.add(target.id)
        name = getattr(target, 'first_name', 'User')
        uname = f"@{target.username}" if getattr(target, 'username', None) else f"ID: {target.id}"

        card = (
            "```text\n"
            "┌───「 🛡️ 𝗔𝗡𝗧𝗜-𝗧𝗔𝗚 𝗔𝗖𝗧𝗜𝗩𝗔𝗧𝗘𝗗 」\n"
            f"├─ 👤 𝗧𝗔𝗥𝗚𝗘𝗧 :: {name} ({uname})\n"
            "├─ 🔒 𝗔𝗖𝗧𝗜𝗢𝗡 :: Auto-purge mentions & replies\n"
            "└───「 🔥 𝗧𝗵𝗿𝗲𝗮𝘁 𝗟𝗼𝗰𝗸𝗲𝗱 」\n"
            "```"
        )
        await event.edit(card)
        await asyncio.sleep(2)
        await event.delete()

    # --- .unantitag <user/reply> ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.unantitag(?:\s+(.+))?'))
    async def disable_antitag(event):
        global ANTITAG_USERS
        reply = await event.get_reply_message()
        user_arg = event.pattern_match.group(1)
        target = None

        if reply:
            target = await reply.get_sender()
        elif user_arg:
            try:
                target = await client.get_entity(int(user_arg) if user_arg.isdigit() else user_arg)
            except Exception as e:
                await event.edit(f"```text\n[!] User not found: {e}\n```")
                return
        else:
            await event.edit("```text\n[!] Reply to user or provide username/ID.\nUsage: .unantitag @user\n```")
            return

        if target.id in ANTITAG_USERS:
            ANTITAG_USERS.remove(target.id)
            status_text = "Target removed from Anti-Tag watch."
        else:
            status_text = "Target was not on the Anti-Tag list."

        name = getattr(target, 'first_name', 'User')
        card = (
            "```text\n"
            "┌───「 🕊️ 𝗔𝗡𝗧𝗜-𝗧𝗔𝗚 𝗗𝗘𝗔𝗖𝗧𝗜𝗩𝗔𝗧𝗘𝗗 」\n"
            f"├─ 👤 𝗧𝗔𝗥𝗚𝗘𝗧 :: {name} ({target.id})\n"
            f"└─ 🔓 𝗦𝗧𝗔𝗧𝗨𝗦 :: {status_text}\n"
            "```"
        )
        await event.edit(card)
        await asyncio.sleep(2)
        await event.delete()

    # --- Anti-Tag Background Watcher ---
    @client.on(events.NewMessage(incoming=True))
    async def antitag_watcher(event):
        global ANTITAG_USERS
        if not ANTITAG_USERS:
            return

        sender_id = event.sender_id
        if sender_id not in ANTITAG_USERS:
            return

        await init_identity(client)
        is_targeting_me = False

        # Check 1: Reply to my message
        if event.is_reply:
            try:
                reply_msg = await event.get_reply_message()
                if reply_msg and reply_msg.sender_id == MY_ID:
                    is_targeting_me = True
            except Exception:
                pass

        # Check 2: Direct Username Mention in text
        if not is_targeting_me and event.raw_text:
            text_lower = event.raw_text.lower()
            for u in MY_USERNAMES:
                if f"@{u}" in text_lower:
                    is_targeting_me = True
                    break

        # Check 3: Text Entity Mentions (clickable text mentions)
        if not is_targeting_me and event.entities:
            for ent in event.entities:
                if isinstance(ent, MessageEntityMentionName) and ent.user_id == MY_ID:
                    is_targeting_me = True
                    break

        # If target tried to tag or reply to me -> Delete immediately
        if is_targeting_me:
            try:
                await event.delete()
            except Exception:
                pass
