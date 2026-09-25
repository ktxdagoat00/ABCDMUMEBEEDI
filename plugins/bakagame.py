import asyncio
import re
import unicodedata
from telethon import events

def clean_text(text):
    if not text:
        return ""
    # Strip invisible zero-width spaces and convert small-caps to standard ascii
    text = text.replace("\u200b", "").replace("\u200c", "").replace("\u200d", "").replace("\ufeff", "")
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if not unicodedata.combining(c)).lower()

def extract_coins(raw_text):
    if not raw_text:
        return 0
    for line in raw_text.splitlines():
        c_line = clean_text(line)
        if "coin" in c_line:
            # Extract numbers following coins
            digits = re.findall(r'\d+', c_line.replace(",", ""))
            if digits:
                return int(digits[0])
    cleaned = clean_text(raw_text)
    match = re.search(r'coin[^\d]*(\d+)', cleaned.replace(",", ""))
    if match:
        return int(match.group(1))
    return 0

def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.bkr$'))
    async def baka_auto_rob(event):
        reply = await event.get_reply_message()
        if not reply:
            return

        chat = event.chat_id
        target_msg_id = reply.id

        # 1. Instantly delete .bkr so nobody sees bot usage
        await event.delete()

        # 2. Dispatch /bal on the target message immediately
        bal_msg = await client.send_message(chat, "/bal", reply_to=target_msg_id)

        # 3. Fast listener for @im_bakabot response to /bal
        baka_bal_resp = None
        for _ in range(30):  # 6 seconds maximum wait
            await asyncio.sleep(0.15)
            async for msg in client.iter_messages(chat, limit=6):
                if msg.id > bal_msg.id:
                    c = clean_text(msg.raw_text)
                    if "coin" in c or "status" in c:
                        baka_bal_resp = msg
                        break
            if baka_bal_resp:
                break

        if not baka_bal_resp:
            return

        bal_content = clean_text(baka_bal_resp.raw_text)

        # Check if target is alive
        if "alive" not in bal_content:
            return

        # 4. Extract coin value (W)
        w_coins = extract_coins(baka_bal_resp.raw_text)

        # 5. Dispatch /kill immediately on the same target message
        kill_msg = await client.send_message(chat, "/kill", reply_to=target_msg_id)

        # 6. Fast listener for Bakabot reply to /kill
        baka_kill_resp = None
        for _ in range(30):
            await asyncio.sleep(0.15)
            async for msg in client.iter_messages(chat, limit=6):
                if msg.id > kill_msg.id:
                    c = clean_text(msg.raw_text)
                    if "protect" in c or "kill" in c or "victim" in c:
                        baka_kill_resp = msg
                        break
            if baka_kill_resp:
                break

        # Check if victim is protected
        if baka_kill_resp:
            kill_content = clean_text(baka_kill_resp.raw_text)
            if "protect" in kill_content or "check protection" in kill_content:
                return

        # 7. Rob Calculation:
        # If W > 0, rob min(W, 10000)
        if w_coins > 0:
            rob_amount = 10000 if w_coins >= 10000 else w_coins
            await asyncio.sleep(0.1)
            await client.send_message(chat, f"/rob {rob_amount}", reply_to=target_msg_id)
