import asyncio
import re
import unicodedata
from telethon import events

def normalize(text):
    if not text:
        return ""
    # Zero-width spaces clean karo aur fancy small-caps ko normal letters me badlo
    text = text.replace("\u200b", "").replace("\u200c", "").replace("\u200d", "").replace("\ufeff", "")
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()

def parse_coins(text):
    clean = normalize(text)
    # Search coins row: 💰 Coins: $12345
    for line in clean.splitlines():
        if "coin" in line:
            digits = re.findall(r'\d+', line.replace(",", ""))
            if digits:
                return int(digits[0])
    # Fallback search
    digits = re.findall(r'\d+', clean.replace(",", ""))
    return int(digits[0]) if digits else 0

def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.bkr$'))
    async def baka_runner(event):
        reply = await event.get_reply_message()
        if not reply:
            return

        chat = event.chat_id
        original_msg_id = reply.id

        # 1. Delete .bkr trigger
        await event.delete()

        # 2. Original message par /bal bhejte hain
        bal_cmd = await client.send_message(chat, "/bal", reply_to=original_msg_id)

        # 3. Bakabot ke /bal reply ka wait karo (Max 6 seconds)
        bal_resp = None
        for _ in range(30):
            await asyncio.sleep(0.2)
            async for m in client.iter_messages(chat, limit=6):
                # Bakabot ya toh /bal ko reply karega ya direct coin card bhejega
                if m.id > bal_cmd.id and ("coin" in normalize(m.raw_text) or "status" in normalize(m.raw_text)):
                    bal_resp = m
                    break
            if bal_resp:
                break

        if not bal_resp:
            return

        norm_bal = normalize(bal_resp.raw_text)

        # 4. Status Check -> must be ALIVE
        if "alive" not in norm_bal:
            return

        # 5. Coins read karo
        coins_xyz = parse_coins(bal_resp.raw_text)

        # 6. Original message par /kill bhejte hain
        kill_cmd = await client.send_message(chat, "/kill", reply_to=original_msg_id)

        # 7. Bakabot ke /kill reply ka wait karo
        kill_resp = None
        for _ in range(30):
            await asyncio.sleep(0.2)
            async for m in client.iter_messages(chat, limit=6):
                if m.id > kill_cmd.id:
                    norm_m = normalize(m.raw_text)
                    if "protect" in norm_m or "victim" in norm_m or "died" in norm_m or "kill" in norm_m:
                        kill_resp = m
                        break
            if kill_resp:
                break

        # 8. Protection check: agar protected hai toh STOP
        if kill_resp:
            norm_kill = normalize(kill_resp.raw_text)
            if "protect" in norm_kill or "check protection" in norm_kill:
                return

        # 9. Rob logic execute karo original message par
        if coins_xyz > 0:
            rob_val = 10000 if coins_xyz > 10000 else coins_xyz
            await asyncio.sleep(0.1)
            await client.send_message(chat, f"/rob {rob_val}", reply_to=original_msg_id)
