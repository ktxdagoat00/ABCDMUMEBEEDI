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

def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.bkr$'))
    async def baka_auto_rob(event):
        reply = await event.get_reply_message()
        if not reply:
            return

        chat = event.chat_id
        target_msg_id = reply.id

        # Delete command quietly
        await event.delete()

        # Send /bal
        bal_msg = await client.send_message(chat, "/bal", reply_to=target_msg_id)

        # 1. Capture Bakabot response via live event listener
        future_bal = asyncio.get_event_loop().create_future()

        @client.on(events.NewMessage(chats=chat))
        async def bal_catcher(e):
            if not future_bal.done():
                txt = clean_text(e.raw_text)
                if ("coin" in txt or "status" in txt) and e.id > bal_msg.id:
                    future_bal.set_result(e)

        try:
            baka_bal_resp = await asyncio.wait_for(future_bal, timeout=8.0)
        except asyncio.TimeoutError:
            client.remove_event_handler(bal_catcher)
            return
        finally:
            client.remove_event_handler(bal_catcher)

        raw_bal = baka_bal_resp.raw_text
        c_bal = clean_text(raw_bal)

        # Status check - check if not dead
        # Bakabot me status 'alive' hota hai ya status field me 'dead' nahi hota
        if "dead" in c_bal or ("alive" not in c_bal and "status" in c_bal):
            return

        # Extract coins
        w_coins = extract_coins(raw_bal)

        # Send /kill
        kill_msg = await client.send_message(chat, "/kill", reply_to=target_msg_id)

        # 2. Capture Bakabot response to /kill
        future_kill = asyncio.get_event_loop().create_future()

        @client.on(events.NewMessage(chats=chat))
        async def kill_catcher(e):
            if not future_kill.done():
                if e.id > kill_msg.id:
                    txt = clean_text(e.raw_text)
                    if "protect" in txt or "victim" in txt or "kill" in txt or "died" in txt or "cooldown" in txt:
                        future_kill.set_result(e)

        try:
            baka_kill_resp = await asyncio.wait_for(future_kill, timeout=8.0)
        except asyncio.TimeoutError:
            client.remove_event_handler(kill_catcher)
            baka_kill_resp = None
        finally:
            client.remove_event_handler(kill_catcher)

        if baka_kill_resp:
            k_txt = clean_text(baka_kill_resp.raw_text)
            if "protect" in k_txt or "check protection" in k_txt:
                return

        # 3. Send /rob
        if w_coins > 0:
            rob_amount = 10000 if w_coins >= 10000 else w_coins
            await asyncio.sleep(0.1)
            await client.send_message(chat, f"/rob {rob_amount}", reply_to=target_msg_id)
