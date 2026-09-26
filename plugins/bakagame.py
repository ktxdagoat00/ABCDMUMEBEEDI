import asyncio
import re
import unicodedata
from telethon import events

MAX_ROB = 10000
WAIT_TRIES = 20
WAIT_DELAY = 0.3
COIN_WORDS = "(?:coins?|соины|монеты)"
COIN_PATTERNS = (
    rf"{COIN_WORDS}[^0-9]{{0,15}}([0-9][0-9,._]*)\s*([km])?",
    r"\$\s*([0-9][0-9,._]*)\s*([km])?",
    r":\s*\$?\s*([0-9][0-9,._]*)\s*([km])?",
)

# In-memory target watchlist: {chat_id: set(target_user_ids)}
TARGET_WATCHLIST = {}

def clean_text(text):
    if not text:
        return ""
    out = []
    for ch in unicodedata.normalize("NFKC", text):
        if unicodedata.combining(ch):
            continue
        digit = unicodedata.decimal(ch, None)
        out.append(str(digit) if digit is not None else ch.lower())
    return "".join(out)

def _to_int(number, multiplier=1):
    number = number.replace(",", "").replace("_", "").strip()
    try:
        return int(float(number) * multiplier)
    except (ValueError, TypeError):
        return None

def extract_coins(raw_text):
    cleaned = clean_text(raw_text)
    for pattern in COIN_PATTERNS:
        match = re.search(pattern, cleaned)
        if not match:
            continue
        mult = {"k": 1000, "m": 1000000}.get(match.group(2), 1)
        value = _to_int(match.group(1), mult)
        if value:
            return value
    return None

async def execute_bkr_sequence(client, chat, target_msg_id):
    """Core Bal -> Kill -> Rob sequence executed on target_msg_id."""
    async def wait_response(cmd_msg, keywords=()):
        for _ in range(WAIT_TRIES):
            await asyncio.sleep(WAIT_DELAY)
            async for msg in client.iter_messages(chat, limit=15):
                if msg.id <= cmd_msg.id or msg.out:
                    continue
                if msg.reply_to_msg_id not in (None, cmd_msg.id):
                    continue
                content = clean_text(msg.raw_text)
                if keywords and not any(key in content for key in keywords):
                    continue
                return msg
        return None

    # 1. /bal on target
    bal_msg = await client.send_message(chat, "/bal", reply_to=target_msg_id)
    bal_resp = await wait_response(bal_msg, ("coin", "$", "status"))
    if not bal_resp:
        return

    bal_content = clean_text(bal_resp.raw_text)

    # 2. Check Status -> Alive
    if "alive" not in bal_content:
        return

    # 3. Read coins
    coins = extract_coins(bal_resp.raw_text)

    # 4. /kill on target
    kill_msg = await client.send_message(chat, "/kill", reply_to=target_msg_id)
    kill_resp = await wait_response(kill_msg)

    # 5. Check Protection -> If protected then stop
    if kill_resp and "protect" in clean_text(kill_resp.raw_text):
        return

    # 6. /rob with exact coins (Max 10000)
    if not coins or coins <= 0:
        return

    rob_amount = min(coins, MAX_ROB)
    await asyncio.sleep(0.2)
    await client.send_message(chat, f"/rob {rob_amount}", reply_to=target_msg_id)

def setup(client):

    # Manual trigger on reply: .bkr
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.bkr$'))
    async def baka_manual_rob(event):
        reply = await event.get_reply_message()
        if not reply:
            await event.edit("```text\n[!] Reply to a user's message with .bkr\n```")
            return

        chat = await event.get_input_chat()
        target_msg_id = reply.id
        await event.delete()
        await execute_bkr_sequence(client, chat, target_msg_id)

    # Register target to watch: .gcm <user>
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.gcm(?:\s+(.+))?'))
    async def add_gcm_target(event):
        target_user = None
        reply = await event.get_reply_message()
        if reply:
            target_user = await reply.get_sender()
        else:
            arg = event.pattern_match.group(1)
            if arg:
                try:
                    target_user = await client.get_entity(arg.strip())
                except Exception:
                    await event.edit("```text\n[!] User entity not found.\n```")
                    return

        if not target_user:
            await event.edit("```text\n[!] Provide username/ID or reply to user message.\nUsage: .gcm @username\n```")
            return

        chat_id = event.chat_id
        if chat_id not in TARGET_WATCHLIST:
            TARGET_WATCHLIST[chat_id] = set()

        TARGET_WATCHLIST[chat_id].add(target_user.id)

        card = (
            "```text\n"
            "╔════「 🎯 𝗧𝗔𝗥𝗚𝗘𝗧 𝗪𝗔𝗧𝗖𝗛𝗘𝗥 𝗟𝗢𝗖𝗞𝗘𝗗 」════╗\n"
            "║\n"
            "╠─ 👤 MASTER :: K E S H A V\n"
            f"╠─ 🎯 TARGET :: {getattr(target_user, 'first_name', '')} ({target_user.id})\n"
            "╠─ ⚡ TRIGGER:: Auto .bkr on arrival/message\n"
            "║\n"
            "╚═══════════════════════════════════════╝\n"
            "```"
        )
        await event.edit(card)

    # Remove target from watch: .ungcm <user>
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ungcm(?:\s+(.+))?'))
    async def remove_gcm_target(event):
        chat_id = event.chat_id
        target_id = None
        reply = await event.get_reply_message()
        if reply:
            target_id = reply.sender_id
        else:
            arg = event.pattern_match.group(1)
            if arg:
                try:
                    entity = await client.get_entity(arg.strip())
                    target_id = entity.id
                except Exception:
                    pass

        if chat_id in TARGET_WATCHLIST and target_id in TARGET_WATCHLIST[chat_id]:
            TARGET_WATCHLIST[chat_id].remove(target_id)
            await event.edit(f"```text\n[✓] Released target {target_id} from auto-hunt.\n```")
        else:
            await event.edit("```text\n[!] Target is not in the active watcher list.\n```")

    # Incoming listener: Triggers when target sends any message
    @client.on(events.NewMessage(incoming=True))
    async def gcm_watcher(event):
        chat_id = event.chat_id
        if chat_id not in TARGET_WATCHLIST:
            return

        sender_id = event.sender_id
        if sender_id in TARGET_WATCHLIST[chat_id]:
            chat_input = await event.get_input_chat()
            # Fire bkr sequence directly onto the target's new message
            await execute_bkr_sequence(client, chat_input, event.id)
