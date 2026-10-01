import asyncio
from telethon import events
from telethon.tl.types import User

# Mirrors list taaki agar ek busy/down/quota ho toh turant dusre se fetch ho sake
SANGMATA_BOTS = [
    "SangMata_BOT",
    "SangMataInfo_bot",
    "Sangmata_beta_bot"
]

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
        await event.edit("```text\n[~] Fetching name & username history from SangMata...\n```")

        sangmata_response = None

        for bot_username in SANGMATA_BOTS:
            try:
                bot_entity = await client.get_input_entity(bot_username)
                
                # Step 1: Ensure bot chat is initialized with /start if needed
                async with client.conversation(bot_entity, timeout=7) as conv:
                    # Send /start first to wake up bot session
                    await conv.send_message("/start")
                    try:
                        # Flush initial start welcome message
                        await asyncio.wait_for(conv.get_response(), timeout=1.5)
                    except Exception:
                        pass

                    # Step 2: Send solely the target User ID
                    query_msg = await conv.send_message(str(target_id))

                    collected_messages = []
                    # Wait up to 5 seconds to collect all parts (Name history + Username history)
                    for _ in range(4):
                        try:
                            resp = await asyncio.wait_for(conv.get_response(), timeout=2.0)
                            txt = resp.raw_text or ""
                            low = txt.lower()

                            # Quota check
                            if any(w in low for w in ["limit", "quota", "exceeded", "try again", "busy"]):
                                collected_messages = []
                                break
                            
                            # Filter out placeholder search messages
                            if "searching" in low or "please wait" in low:
                                continue

                            collected_messages.append(txt)
                        except asyncio.TimeoutError:
                            break

                    if collected_messages:
                        combined = "\n\n".join(collected_messages).strip()
                        # Make sure it actually has history or user info
                        if str(target_id) in combined or "name" in combined.lower() or "username" in combined.lower():
                            sangmata_response = combined
                            break
            except Exception:
                continue

        # If history fetched cleanly
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

        # If quota is finished or bot is silent -> Native profile details
        fallback_card = build_native_fallback_card(
            target_entity, 
            note="No Sangmata history / Daily quota reached"
        )
        await event.edit(fallback_card)
