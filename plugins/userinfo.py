import asyncio
from telethon import events
from telethon.tl.types import User

SANGMATA_BOTS = ["SangMataInfo_bot", "SangMata_Beta_bot"]

def build_native_fallback_card(user: User, note="Sangmata Daily Quota Reached / Busy"):
    first = getattr(user, 'first_name', '') or 'None'
    last = getattr(user, 'last_name', '') or ''
    full_name = f"{first} {last}".strip()
    username = f"@{user.username}" if user.username else "No Username"
    dc_id = getattr(getattr(user, 'photo', None), 'dc_id', 'Unknown')
    is_premium = "Yes ⭐" if getattr(user, 'premium', False) else "No"
    is_bot = "Yes 🤖" if getattr(user, 'bot', False) else "No"
    is_scam = "YES ⚠️" if getattr(user, 'scam', False) else "Clean"

    return (
        "```text\n"
        "╔═════「 👤 USER PROFILE CARD 」═════╗\n"
        "║\n"
        f"╠─ 🆔 USER ID   :: {user.id}\n"
        f"╠─ 🏷️ FULL NAME :: {full_name}\n"
        f"╠─ 🌐 USERNAME  :: {username}\n"
        f"╠─ 🛰️ DC ID     :: {dc_id}\n"
        f"╠─ ⭐ PREMIUM   :: {is_premium}\n"
        f"╠─ 🤖 IS BOT    :: {is_bot}\n"
        f"╠─ 🛡️ SCAM/FAKE :: {is_scam}\n"
        f"╠─ ⚠️ NOTICE    :: {note}\n"
        "║\n"
        "╚════════════════════════════════════╝\n"
        "```"
    )

def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.info(?:\s+(.+))?'))
    async def get_user_info(event):
        reply = await event.get_reply_message()
        target_entity = None

        if reply:
            target_entity = await reply.get_sender()
        else:
            arg = event.pattern_match.group(1)
            if arg:
                try:
                    query = int(arg.strip()) if arg.strip().isdigit() else arg.strip()
                    target_entity = await client.get_entity(query)
                except Exception as e:
                    await event.edit(f"```text\n[!] User not found: {e}\n```")
                    return

        if not target_entity:
            await event.edit("```text\n[!] Reply to a user or pass .info <username/id>\n```")
            return

        if not isinstance(target_entity, User):
            await event.edit("```text\n[!] Target is a channel/chat, not a user.\n```")
            return

        target_id = target_entity.id
        await event.edit("```text\n[~] Querying user history...\n```")

        # 1. Query Sangmata Bot
        sangmata_response = None
        for s_bot in SANGMATA_BOTS:
            try:
                async with client.conversation(s_bot, timeout=5) as conv:
                    # Send solely target numeric ID
                    query_msg = await conv.send_message(str(target_id))
                    resp = await conv.get_response()
                    txt = resp.raw_text or ""

                    # Quota / Error keywords detection
                    lower_txt = txt.lower()
                    if any(w in lower_txt for w in ["limit", "quota", "exceeded", "try again tomorrow", "busy"]):
                        continue
                    if "user" in lower_txt or "name" in lower_txt or "history" in lower_txt or str(target_id) in txt:
                        sangmata_response = txt
                        break
            except Exception:
                continue

        # 2. Render Sangmata response if obtained cleanly
        if sangmata_response:
            formatted_card = (
                "```text\n"
                "╔═════「 👤 USER HISTORY (SANGMATA) 」═════╗\n"
                "║\n"
                f"{sangmata_response}\n"
                "║\n"
                "╚══════════════════════════════════════════╝\n"
                "```"
            )
            await event.edit(formatted_card)
            return

        # 3. Quota exhausted or no response -> Trigger native detailed fallback
        fallback_card = build_native_fallback_card(target_entity, note="Sangmata Quota Over / Fallback Active")
        await event.edit(fallback_card)
