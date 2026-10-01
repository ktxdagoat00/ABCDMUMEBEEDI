import asyncio
from telethon import events
from telethon.tl.types import User

# Exact primary bot target
PRIMARY_BOT = "SangMata_BOT"
BACKUP_BOTS = ["SangMata_Beta_bot", "SangMataInfo_bot"]

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
        await event.edit("```text\n[~] Querying @SangMata_BOT history...\n```")

        sangmata_response = None
        bot_list = [PRIMARY_BOT] + BACKUP_BOTS

        for bot in bot_list:
            try:
                async with client.conversation(bot, timeout=6) as conv:
                    # Sirf numeric user id send karni hai
                    await conv.send_message(str(target_id))
                    
                    # Wait for primary response
                    resp = await conv.get_response()
                    txt = resp.raw_text or ""
                    lower_txt = txt.lower()

                    # Check for quota exhausted or flood wait
                    if any(w in lower_txt for w in ["limit", "quota", "exceeded", "try again", "busy", "cooldown"]):
                        continue

                    # Sangmata can send history in 1 or 2 parts, gather if available
                    collected_texts = [txt]
                    try:
                        second_resp = await asyncio.wait_for(conv.get_response(), timeout=1.5)
                        if second_resp and second_resp.raw_text:
                            collected_texts.append(second_resp.raw_text)
                    except asyncio.TimeoutError:
                        pass

                    sangmata_response = "\n\n".join(collected_texts)
                    if sangmata_response:
                        break
            except Exception:
                continue

        # Output result
        if sangmata_response:
            formatted_card = (
                "```text\n"
                "╔═════「 👤 USER HISTORY (@SangMata_BOT) 」═════╗\n"
                "║\n"
                f"{sangmata_response.strip()}\n"
                "║\n"
                "╚═══════════════════════════════════════════════╝\n"
                "```"
            )
            await event.edit(formatted_card)
            return

        # Quota Over ya No Response ke case me Fallback
        fallback_card = build_native_fallback_card(target_entity, note="SangMata Limit Reached / Fallback Mode")
        await event.edit(fallback_card)
