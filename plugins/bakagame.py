import asyncio
import re
import unicodedata
from telethon import events

def clean_text(text):
    if not text:
        return ""
    # Normalize fancy unicode/small-caps to standard ascii
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if not unicodedata.combining(c)).lower()

def extract_coins(raw_text):
    # Match patterns like: Coins: $12,345 or Coins: 5000
    cleaned = clean_text(raw_text)
    match = re.search(r'coins?:\s*\$?([\d,]+)', cleaned)
    if match:
        num_str = match.group(1).replace(",", "")
        try:
            return int(num_str)
        except ValueError:
            return 0
    return 0

def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.bkr$'))
    async def baka_auto_rob(event):
        reply = await event.get_reply_message()
        if not reply:
            await event.edit("```text\n[!] Reply to target user's message with .bkr\n```")
            return

        chat = await event.get_input_chat()
        target_msg_id = reply.id

        # 1. Stealth mode: delete command trigger so nobody sees bot syntax
        await event.delete()

        # 2. Send /bal as a direct reply to the target
        bal_msg = await client.send_message(chat, "/bal", reply_to=target_msg_id)

        # 3. Wait for @im_bakabot's response to /bal
        baka_bal_resp = None
        for _ in range(40):  # 8 seconds max wait (0.2s poll)
            await asyncio.sleep(0.2)
            async for msg in client.iter_messages(chat, limit=6):
                # Ensure it is replying to /bal or mentions victim/coins
                if msg.reply_to_msg_id == bal_msg.id or ("coins" in clean_text(msg.raw_text) and msg.id > bal_msg.id):
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

        # 4. Target is alive -> send /kill to target
        kill_msg = await client.send_message(chat, "/kill", reply_to=target_msg_id)

        # 5. Wait for @im_bakabot's response to /kill
        baka_kill_resp = None
        for _ in range(40):
            await asyncio.sleep(0.2)
            async for msg in client.iter_messages(chat, limit=6):
                if msg.reply_to_msg_id == kill_msg.id or ("protected" in clean_text(msg.raw_text) and msg.id > kill_msg.id):
                    baka_kill_resp = msg
                    break
            if baka_kill_resp:
                break

        if not baka_kill_resp:
            return

        kill_content = clean_text(baka_kill_resp.raw_text)

        # If protected right now -> stop immediately
        if "victim is protected" in kill_content or "check protection time" in kill_content or "protected right now" in kill_content:
            return

        # 6. Check coins and Rob
        coins = extract_coins(baka_bal_resp.raw_text)
        if coins > 0:
            rob_amount = min(coins, 10000)
            await client.send_message(chat, f"/rob {rob_amount}", reply_to=target_msg_id)
