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
    if not raw_text:
        return 0
    for line in raw_text.splitlines():
        c_line = clean_text(line)
        if "coin" in c_line:
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
            await event.edit("```text\n[!] Reply to target user message with .bkr\n```")
            return

        chat = event.chat_id
        target_msg_id = reply.id

        # 1. Send /bal first as reply to victim
        bal_msg = await client.send_message(chat, "/bal", reply_to=target_msg_id)

        # 2. Wait for Bakabot reply to /bal
        baka_bal_resp = None
        for _ in range(40):
            await asyncio.sleep(0.2)
            async for msg in client.iter_messages(chat, limit=8):
                if msg.id > bal_msg.id:
                    c = clean_text(msg.raw_text)
                    if "coin" in c or "status" in c or "rank" in c:
                        baka_bal_resp = msg
                        break
            if baka_bal_resp:
                break

        if not baka_bal_resp:
            return

        bal_content = clean_text(baka_bal_resp.raw_text)

        # Stop if victim is not alive
        if "alive" not in bal_content:
            await event.delete()
            return

        # 3. Target is alive -> calculate coins
        coins = extract_coins(baka_bal_resp.raw_text)
        rob_amount = min(coins, 10000) if coins > 0 else 0

        # 4. Send /kill
        kill_msg = await client.send_message(chat, "/kill", reply_to=target_msg_id)

        # 5. Wait for Bakabot reply to /kill
        baka_kill_resp = None
        for _ in range(40):
            await asyncio.sleep(0.2)
            async for msg in client.iter_messages(chat, limit=8):
                if msg.id > kill_msg.id:
                    c = clean_text(msg.raw_text)
                    if "protect" in c or "kill" in c or "victim" in c:
                        baka_kill_resp = msg
                        break
            if baka_kill_resp:
                break

        # Check protection
        if baka_kill_resp:
            kill_content = clean_text(baka_kill_resp.raw_text)
            if "protect" in kill_content or "check protection" in kill_content:
                await event.delete()
                return

        # 6. Send /rob if coins > 0
        if rob_amount > 0:
            await asyncio.sleep(0.3)
            await client.send_message(chat, f"/rob {rob_amount}", reply_to=target_msg_id)

        # 7. Clean up original .bkr command trigger at the very end
        try:
            await event.delete()
        except Exception:
            pass
