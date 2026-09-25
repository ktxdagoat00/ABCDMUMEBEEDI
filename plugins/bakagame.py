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

    # Line by line parsing - robust against fancy fonts
    for line in raw_text.splitlines():
        c_line = clean_text(line)
        if "coin" in c_line:
            # Match digits inside that specific line
            digits = re.findall(r'\d+', c_line.replace(",", ""))
            if digits:
                return int(digits[0])

    # Fallback search across entire text
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

        chat = await event.get_input_chat()
        target_msg_id = reply.id

        # 1. Stealth delete
        await event.delete()

        # 2. Send /bal
        bal_msg = await client.send_message(chat, "/bal", reply_to=target_msg_id)

        # 3. Wait for /bal response from Bakabot
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

        # 4. Extract coins accurately
        coins = extract_coins(baka_bal_resp.raw_text)
        if coins <= 0:
            return

        rob_amount = min(coins, 10000)

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

        # 7. Execute /rob with exact parsed value
        await asyncio.sleep(0.3)
        await client.send_message(chat, f"/rob {rob_amount}", reply_to=target_msg_id)
