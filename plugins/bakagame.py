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


def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.bkr$'))
    async def baka_auto_rob(event):
        reply = await event.get_reply_message()
        if not reply:
            return

        chat = await event.get_input_chat()
        target_msg_id = reply.id

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

        # 1. Stealth delete trigger
        await event.delete()

        # 2. Step 1: /bal on target
        bal_msg = await client.send_message(chat, "/bal", reply_to=target_msg_id)
        bal_resp = await wait_response(bal_msg, ("coin", "$", "status"))
        if not bal_resp:
            return

        bal_content = clean_text(bal_resp.raw_text)

        # 3. Check Status -> Alive
        if "alive" not in bal_content:
            return

        # 4. Read coins
        coins = extract_coins(bal_resp.raw_text)

        # 5. Step 2: /kill on target
        kill_msg = await client.send_message(chat, "/kill", reply_to=target_msg_id)
        kill_resp = await wait_response(kill_msg)

        # 6. Check Protection -> If protected then STOP
        if kill_resp and "protect" in clean_text(kill_resp.raw_text):
            return

        # 7. Step 3: /rob with exact coins (Max 10000)
        if not coins or coins <= 0:
            return

        rob_amount = min(coins, MAX_ROB)
        await asyncio.sleep(0.2)
        await client.send_message(chat, f"/rob {rob_amount}", reply_to=target_msg_id)
