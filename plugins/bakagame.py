import asyncio
import re
import unicodedata
from telethon import events

def clean_text(text):
    if not text:
        return ""
    text = text.replace("\u200b", "").replace("\u200c", "").replace("\u200d", "").replace("\ufeff", "")
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if not unicodedata.combining(c)).lower()

def extract_coins(raw_text):
    if not raw_text:
        return 0
    c_all = clean_text(raw_text)
    for line in c_all.splitlines():
        if "coin" in line:
            digits = re.findall(r'\d+', line.replace(",", ""))
            if digits:
                return int(digits[0])
    match = re.search(r'coin[^\d]*(\d+)', c_all.replace(",", ""))
    if match:
        return int(match.group(1))
    return 0

def is_alive_status(raw_text):
    c = clean_text(raw_text)
    # Check both whole text and line-by-line
    if "status" in c and "alive" in c:
        return True
    if "alive" in c and "dead" not in c:
        return True
    return False

def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.bkr$'))
    async def baka_auto_rob(event):
        reply = await event.get_reply_message()
        if not reply:
            return

        chat = event.chat_id
        target_msg_id = reply.id

        # 1. Silently delete trigger
        await event.delete()

        # 2. Dispatch /bal directly to target
        bal_msg = await client.send_message(chat, "/bal", reply_to=target_msg_id)

        # 3. Dedicated fast-wait loop using event queue
        baka_bal_resp = None
        for _ in range(50):  # 10s timeout (0.2s tick)
            await asyncio.sleep(0.2)
            # Fetch recent 4 messages fresh from chat
            async for m in client.iter_messages(chat, limit=4):
                if m.id > bal_msg.id:
                    txt = clean_text(m.raw_text)
                    if "coin" in txt or "status" in txt or "rank" in txt:
                        baka_bal_resp = m
                        break
            if baka_bal_resp:
                break

        if not baka_bal_resp:
            return

        # 4. Check alive status
        if not is_alive_status(baka_bal_resp.raw_text):
            return

        # 5. Extract Coins (W)
        w_coins = extract_coins(baka_bal_resp.raw_text)

        # 6. Dispatch /kill on target
        kill_msg = await client.send_message(chat, "/kill", reply_to=target_msg_id)

        # 7. Listen for response to /kill
        baka_kill_resp = None
        for _ in range(50):
            await asyncio.sleep(0.2)
            async for m in client.iter_messages(chat, limit=4):
                if m.id > kill_msg.id:
                    txt = clean_text(m.raw_text)
                    if "protect" in txt or "victim" in txt or "kill" in txt or "died" in txt:
                        baka_kill_resp = m
                        break
            if baka_kill_resp:
                break

        # Check protection
        if baka_kill_resp:
            k_txt = clean_text(baka_kill_resp.raw_text)
            if "protect" in k_txt or "check protection" in k_txt:
                return

        # 8. Dispatch /rob
        if w_coins > 0:
            rob_amount = 10000 if w_coins >= 10000 else w_coins
            await asyncio.sleep(0.15)
            await client.send_message(chat, f"/rob {rob_amount}", reply_to=target_msg_id)
