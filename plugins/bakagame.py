import asyncio
import re
import unicodedata
from datetime import datetime, timedelta, timezone
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

TARGET_WATCHLIST = {}
# Active scheduled tasks list for .stopadv
ACTIVE_ADVROB_TASKS = []

# Indian Standard Time (UTC + 5:30)
IST = timezone(timedelta(hours=5, minutes=30))

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
            return
        chat = await event.get_input_chat()
        target_msg_id = reply.id
        await event.delete()
        await execute_bkr_sequence(client, chat, target_msg_id)

    # Target Watcher: .gcm <user>
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
            await event.edit("```text\n[!] Usage: .gcm @username (or reply to msg)\n```")
            return

        chat_id = event.chat_id
        if chat_id not in TARGET_WATCHLIST:
            TARGET_WATCHLIST[chat_id] = set()
        TARGET_WATCHLIST[chat_id].add(target_user.id)
        await event.edit(f"```text\n[✓] Locked Target: {getattr(target_user, 'first_name', '')} ({target_user.id}) for auto .bkr\n```")

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
            await event.edit(f"```text\n[✓] Released target {target_id} from watchlist.\n```")
        else:
            await event.edit("```text\n[!] Target not found in watchlist.\n```")

    @client.on(events.NewMessage(incoming=True))
    async def gcm_watcher(event):
        chat_id = event.chat_id
        if chat_id not in TARGET_WATCHLIST:
            return
        if event.sender_id in TARGET_WATCHLIST[chat_id]:
            chat_input = await event.get_input_chat()
            await execute_bkr_sequence(client, chat_input, event.id)

    # Cancel All Scheduled Tasks: .stopadv
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.stopadv$'))
    async def stop_all_advrob(event):
        cancelled_count = 0
        for task in ACTIVE_ADVROB_TASKS:
            if not task.done():
                task.cancel()
                cancelled_count += 1
        ACTIVE_ADVROB_TASKS.clear()
        await event.edit(f"```text\n[✓] Successfully terminated {cancelled_count} scheduled .advrob task(s)!\n```")

    # Advanced Scheduled Rob: .advrob <user> | <time> | <chatid/here>
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.advrob\s+(.+)'))
    async def adv_rob_schedule(event):
        raw_args = event.pattern_match.group(1).strip()
        parts = [p.strip() for p in raw_args.split("|")]
        if len(parts) < 3:
            space_parts = raw_args.split()
            if len(space_parts) >= 4:
                target_arg = space_parts[0]
                time_arg = f"{space_parts[1]} {space_parts[2]}"
                chat_arg = space_parts[3]
            else:
                await event.edit("```text\n[!] Usage:\n.advrob <user> | <HH:MM:SS AM/PM> | <chat_id/here>\nExample:\n.advrob @target | 10:10:12 PM | -1001234567890\n```")
                return
        else:
            target_arg = parts[0]
            time_arg = parts[1]
            chat_arg = parts[2]

        try:
            if target_arg.isdigit() or (target_arg.startswith("-") and target_arg[1:].isdigit()):
                target_user = await client.get_entity(int(target_arg))
            else:
                target_user = await client.get_entity(target_arg)
        except Exception as e:
            await event.edit(f"```text\n[!] Target user not found: {e}\n```")
            return

        try:
            if chat_arg.lower() == "here":
                target_chat = await event.get_input_chat()
            elif chat_arg.lstrip("-").isdigit():
                target_chat = await client.get_input_entity(int(chat_arg))
            else:
                target_chat = await client.get_input_entity(chat_arg)
        except Exception as e:
            await event.edit(f"```text\n[!] Target chat not found: {e}\n```")
            return

        # Parse Time in IST (Indian Standard Time)
        now_ist = datetime.now(IST)
        target_dt = None
        for fmt in ("%I:%M:%S %p", "%I:%M %p", "%H:%M:%S", "%H:%M"):
            try:
                parsed_t = datetime.strptime(time_arg.upper(), fmt).time()
                target_dt = datetime.combine(now_ist.date(), parsed_t, tzinfo=IST)
                break
            except ValueError:
                continue

        if not target_dt:
            await event.edit("```text\n[!] Invalid time format. Use HH:MM:SS AM/PM\n```")
            return

        # Agar time 1 minute se pehle ka nikal chuka hai tabhi agle din karega, warna aaj hi trigger hoga
        if (target_dt - now_ist).total_seconds() < -30:
            target_dt += timedelta(days=1)

        diff = (target_dt - now_ist).total_seconds()
        if diff < 0:
            diff = 0

        status_card = (
            "```text\n"
            "╔════「 ⏰ 𝗔𝗗𝗩𝗔𝗡𝗖𝗘𝗗 𝗦𝗡𝗜𝗣𝗘𝗥 𝗟𝗢𝗖𝗞𝗘𝗗 」════╗\n"
            "║\n"
            f"╠─ 🎯 TARGET :: {getattr(target_user, 'first_name', '')} ({target_user.id})\n"
            f"╠─ 🕒 TIME   :: {target_dt.strftime('%I:%M:%S %p')} (IST)\n"
            f"╠─ ⏳ REMAIN :: {int(diff)}s remaining\n"
            "╠─ ⚡ ACTION :: Auto-scan latest msg & .bkr\n"
            "╠─ 🛑 CANCEL :: .stopadv\n"
            "║\n"
            "╚═══════════════════════════════════════╝\n"
            "```"
        )
        await event.edit(status_card)

        # Background Task
        async def scheduled_snipe_task():
            try:
                wait_sec = (target_dt - datetime.now(IST)).total_seconds()
                if wait_sec > 0:
                    await asyncio.sleep(wait_sec)

                # Scan chat for latest message from target
                target_msg = None
                async for m in client.iter_messages(target_chat, limit=100):
                    if m.sender_id == target_user.id:
                        target_msg = m
                        break

                if not target_msg:
                    return

                await execute_bkr_sequence(client, target_chat, target_msg.id)
            except asyncio.CancelledError:
                pass

        t = asyncio.create_task(scheduled_snipe_task())
        ACTIVE_ADVROB_TASKS.append(t)
