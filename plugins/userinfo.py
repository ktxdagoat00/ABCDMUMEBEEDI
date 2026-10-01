import asyncio
from telethon import events
from telethon.tl.types import User

TARGET_BOTS = ["SangMata_BOT", "SangMata_beta_bot"]

def build_native_fallback_card(user: User, note="SangMata Quota Limit / No History"):
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
        await event.edit("```text\n[~] Fetching history from @SangMata_BOT...\n```")

        sangmata_final_text = None

        for bot_username in TARGET_BOTS:
            try:
                bot_entity = await client.get_input_entity(bot_username)
                async with client.conversation(bot_entity, timeout=10) as conv:
                    # Sirf plain numeric user ID bhejni hai, kuch aur nahi
                    query_msg = await conv.send_message(str(target_id))

                    gathered_messages = []
                    # Bot replies ko listen karo (searchis/searching ko ignore karo)
                    for _ in range(4):
                        try:
                            resp = await asyncio.wait_for(conv.get_response(), timeout=3.5)
                            txt = resp.raw_text or ""
                            low = txt.lower()

                            # Agar intermediate status message hai, skip karo
                            if any(k in low for k in ["search", "please wait", "processing"]):
                                continue

                            # Agar quota limit ya wait alert hai
                            if any(k in low for k in ["limit", "quota", "exceeded", "cooldown"]):
                                break

                            gathered_messages.append(txt)
                            
                            # Agar bot ne username aur name history bhej di
                            if len(gathered_messages) >= 2:
                                break
                        except asyncio.TimeoutError:
                            break

                    if gathered_messages:
                        sangmata_final_text = "\n\n".join(gathered_messages)
                        break
            except Exception:
                continue

        # Agar result mil gaya to print karo
        if sangmata_final_text:
            output_card = (
                "```text\n"
                "╔═════「 👤 USER HISTORY (@SangMata_BOT) 」═════╗\n"
                "║\n"
                f"{sangmata_final_text.strip()}\n"
                "║\n"
                "╚═══════════════════════════════════════════════╝\n"
                "```"
            )
            await event.edit(output_card)
            return

        # Quota exceed hone par ya result na milne par native card
        fallback_card = build_native_fallback_card(
            target_entity,
            note="SangMata Quota Exceeded / History Not Found"
        )
        await event.edit(fallback_card)
