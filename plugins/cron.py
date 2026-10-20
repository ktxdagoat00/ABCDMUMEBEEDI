import asyncio
import time
import re
from datetime import datetime, timedelta, timezone
from telethon import events

IST = timezone(timedelta(hours=5, minutes=30))

def setup(client):

    # 1. Manual Precision Cron (.cron)
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.cron\s+(?:at\s+)?([^\s]+(?:\s+[^\s]+){0,1})\s+([^\s]+)\s+(.+)'))
    async def precision_cron(event):
        time_raw = event.pattern_match.group(1).strip()
        target_raw = event.pattern_match.group(2).strip()
        message_to_send = event.pattern_match.group(3).strip()
        await schedule_task(event, time_raw, target_raw, message_to_send)

    # 2. Smart AI-Style Giveaway Parser (.c on reply) - Multi-Pattern Support
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.c\$'))
    async def smart_giveaway_parser(event):
        if not event.is_reply:
            await event.edit("```text\n[!] Giveaway ke message par reply karke .c likho!\n```")
            return

        reply_msg = await event.get_reply_message()
        text = reply_msg.text or ""

        # --- SMART MULTI-PATTERN EXTRACTION ---

        # 1. Time Extraction (Catches 9:00 PM, 9 PM, 21:00, 09:30:00 etc.)
        time_match = re.search(r'(?:at|time|timing|sharp)?[\s:-]*(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?|\d{1,2}\s*(?:AM|PM|am|pm))', text, re.IGNORECASE)
        
        # 2. Username Extraction (Catches @username or dm username)
        user_match = re.search(r'(?:dm|to|send|@)[\s:-]*@([A-Za-z0-9_]{5,32})', text, re.IGNORECASE)
        if not user_match:
            # Fallback: find any @username in the text
            user_match = re.search(r'@([A-Za-z0-9_]{5,32})', text)

        # 3. Code/Message Extraction (Catches quotes, code keyword, or words after 'code is')
        code_match = re.search(r'(?:code|msg|text|send|reply|say)[:\s]*[\"\'`]([^\'"`]+)[\"\'`]', text, re.IGNORECASE)
        if not code_match:
            # Fallback 1: Any text inside quotes single/double
            code_match = re.search(r'[\"\'`]([^\'"`]+)[\"\'`]', text)
        if not code_match:
            # Fallback 2: Look for words right after 'code' keyword without quotes
            code_match = re.search(r'code\s+([A-Za-z0-9_#-]+)', text, re.IGNORECASE)

        # Diagnostics agar kuch miss ho jaye
        missing = []
        if not time_match: missing.endswith("Time") # wait, python list append
        
        missing_list = []
        if not time_match: missing_list.append("Time")
        if not user_match: missing_list.append("Username")
        if not code_match: missing_list.append("Code/Message")

        if missing_list:
            await event.edit(
                f"```text\n"
                f"[!] Smart Parse Incomplete!\n"
                f"Could not automatically detect: {', '.join(missing_list)}\n\n"
                f"Tip: Use manual format -> .cron 9:00 PM @username YourCode\n"
                f"```"
            )
            return

        time_raw = time_match.group(1).strip()
        target_raw = f"@{user_match.group(1)}"
        message_to_send = code_match.group(1).strip()

        await schedule_task(event, time_raw, target_raw, message_to_send, is_smart=True)

    # Core Scheduling Logic
    async def schedule_task(event, time_raw, target_raw, message_to_send, is_smart=False):
        command_chat_id = event.chat_id
        now_ist = datetime.now(IST)
        target_dt = None

        try:
            time_raw = time_raw.upper()
            parts = time_raw.split()
            time_part = parts[0]
            ampm_part = parts[1] if len(parts) > 1 else ""

            if time_raw.endswith("PM") or time_raw.endswith("AM"):
                if time_raw.endswith("PM"):
                    ampm_part = "PM"
                    time_part = time_raw[:-2]
                else:
                    ampm_part = "AM"
                    time_part = time_raw[:-2]

            if "." in time_part:
                hms, ms_str = time_part.split(".", 1)
                ms = int(ms_str.ljust(3, "0")[:3])
            else:
                hms = time_part
                ms = 0

            hms_parts = hms.split(":")
            if len(hms_parts) == 2:
                hms = f"{hms}:00"

            time_str = f"{hms} {ampm_part}".strip()
            fmt = "%I:%M:%S %p" if ampm_part else "%H:%M:%S"
            parsed = datetime.strptime(time_str, fmt)

            target_dt = now_ist.replace(
                hour=parsed.hour,
                minute=parsed.minute,
                second=parsed.second,
                microsecond=ms * 1000
            )

            if target_dt <= now_ist:
                target_dt += timedelta(days=1)

        except Exception as e:
            await event.edit(f"```text\n[!] Time parse error: {e}\n```")
            return

        # Target Resolution
        target_dest = None
        reply_msg_id = None
        dest_label = target_raw

        try:
            if target_raw.lower() == "here":
                target_dest = event.chat_id
                dest_label = "Current Chat"
            else:
                target_dest = await client.get_entity(target_raw)
                dest_label = str(target_raw)
        except Exception as e:
            await event.edit(f"```text\n[!] Target resolution failed: {e}\n```")
            return

        wait_sec = (target_dt - now_ist).total_seconds()

        mode_title = "⚡ SMART GIVEAWAY PARSER (.C) ⚡" if is_smart else "⚡ ATOMIC MS-ACCURATE CRON ⚡"
        card = (
            "```text\n"
            f"╔════「 {mode_title} 」════╗\n"
            "║\n"
            "╠─ 👤 MASTER   :: K E S H A V\n"
            f"╠─ 🎯 TARGET   :: {dest_label}\n"
            f"╠─ 💬 CODE     :: {message_to_send}\n"
            f"╠─ ⏰ EXECUTE  :: {target_dt.strftime('%I:%M:%S.%f')[:-3]} {target_dt.strftime('%p')} (IST)\n"
            f"╠─ ⏳ DELAY    :: {round(max(0, wait_sec), 3)}s remaining\n"
            "║\n"
            "╚════════════════════════════════════════════════╝\n"
            "```"
        )
        await event.edit(card)

        # High-Precision Spin-Lock Dispatcher
        async def atomic_dispatcher():
            try:
                target_epoch = target_dt.timestamp()

                while True:
                    remaining = target_epoch - time.time()
                    if remaining <= 0:
                        break
                    if remaining > 0.15:
                        await asyncio.sleep(remaining - 0.05)
                    else:
                        await asyncio.sleep(0.0001)

                await client.send_message(target_dest, message_to_send)

            except Exception as err:
                await client.send_message(command_chat_id, f"```text\n[!] GIVEAWAY SNIPER FAILED!\nError: {err}\n```")

        asyncio.create_task(atomic_dispatcher())
