import asyncio
import re
import unicodedata
from telethon import events

def clean_text(text):
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if not unicodedata.combining(c)).lower()

def extract_coins(raw_text):
    cleaned = clean_text(raw_text)
    # Check for K suffix (e.g., 5k, 10k)
    k_match = re.search(r'coins?[:\s]*\$?([\d\.]+)\s*k', cleaned)
    if k_match:
        try:
            return int(float(k_match.group(1)) * 1000)
        except ValueError:
            pass

    # Standard numeric match (e.g., $1,000 or 5000)
    match = re.search(r'coins?[:\s]*\$?([\d,]+)', cleaned)
    if match:
        num_str = match.group(1).replace(",", "")
        try:
            return int(num_str)
        except ValueError:
            pass

    # Search any dollar amount if 'coins' word exists
    if "coin" in cleaned:
        num_any = re.search(r'\$?([\d,]{2,})', cleaned)
        if num_any:
            try:
                return int(num_any.group(1).replace(",", ""))
            except ValueError:
                pass
    return 10000  # Fallback to max rob so the script never stops

def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.bkr$'))
    async def baka_auto_rob(event):
        reply = await event.get_reply_message()
        if not reply:
            await event.edit("```text\n[!] Reply to target user message with .bkr\n```")
            return

        chat = await event.get_input_chat()
        target_msg_id = reply.id

        # 1. Stealth delete
        await event.delete()

        # 2. Send /bal
        bal_msg = await client.send_message(chat, "/bal", reply_to=target_msg_id)

        # 3. Wait for /bal response
        baka_bal_resp = None
        for _ in range(35):
            await asyncio.sleep(0.2)
            async for msg in client.iter_messages(chat, limit=5):
                c = clean_text(msg.raw_text)
                if msg.reply_to_msg_id == bal_msg.id or ("coin" in c and msg.id > bal_msg.id):
                    baka_bal_resp = msg
                    break
            if baka_bal_resp:
                break

        if not baka_bal_resp:
            return

        bal_content = clean_text(baka_bal_resp.raw_text)

        # Target must be alive
        if "alive" not in bal_content:
            return

        # 4. Extract coins right away
        coins = extract_coins(baka_bal_resp.raw_text)
        rob_amount = min(coins, 10000) if coins > 0 else 10000

        # 5. Send /kill
        kill_msg = await client.send_message(chat, "/kill", reply_to=target_msg_id)

        # 6. Wait for /kill response
        baka_kill_resp = None
        for _ in range(35):
            await asyncio.sleep(0.2)
            async for msg in client.iter_messages(chat, limit=5):
                c = clean_text(msg.raw_text)
                if msg.reply_to_msg_id == kill_msg.id or ("protect" in c and msg.id > kill_msg.id) or msg.id > kill_msg.id:
                    baka_kill_resp = msg
                    break
            if baka_kill_resp:
                break

        # Check protection
        if baka_kill_resp:
            kill_content = clean_text(baka_kill_resp.raw_text)
            if "protect" in kill_content or "check protection" in kill_content:
                return

        # 7. Execute /rob instantly
        await asyncio.sleep(0.3)
        await client.send_message(chat, f"/rob {rob_amount}", reply_to=target_msg_id)
