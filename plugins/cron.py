import asyncio
import time
import aiohttp
from datetime import datetime, timedelta, timezone
from telethon import events

UTC = timezone.utc
IST = timezone(timedelta(hours=5, minutes=30))

async def get_accurate_now():
    """Fetch live accurate IST time from world time API to bypass Render clock skew"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://worldtimeapi.org/api/timezone/Asia/Kolkata", timeout=2) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    dt_str = data["datetime"] # e.g. 2026-10-21T19:30:00.123456+05:30
                    return datetime.fromisoformat(dt_str)
    except Exception:
        pass
    # Fallback to local system time if API fails
    return datetime.now(IST)

def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.cron\s+(?:at\s+)?([^\s]+(?:\s+[^\s]+){0,1})\s+([^\s]+)\s+(.+)'))
    async def precision_cron(event):
        time_raw = event.pattern_match.group(1).strip()
        target_raw = event.pattern_match.group(2).strip()
        message_to_send = event.pattern_match.group(3).strip()
        command_chat_id = event.chat_id

        # Get exact network synchronized IST time
        now_ist = await get_accurate_now()
        target_dt_ist = None

        # Mode A: Relative countdown (e.g., in 10s, in 500ms)
        if time_raw.lower().startswith("in "):
            try:
                val_str = time_raw.lower().replace("in ", "").strip()
                if val_str.endswith("ms"):
                    val = float(val_str[:-2]) / 1000.0
                elif val_str.endswith("s"):
                    val = float(val_str[:-1])
                elif val_str.endswith("m"):
                    val = float(val_str[:-1]) * 60.0
                elif val_str.endswith("h"):
                    val = float(val_str[:-1]) * 3600.0
                else:
                    raise ValueError("Unknown unit")
                target_dt_ist = now_ist + timedelta(seconds=val)
            except Exception:
                await event.edit("```text\n[!] Format error. Try: .cron in 10s here Giveaway Msg!\n```")
                return
        else:
            # Mode B: Clock Time (e.g., 9:00 PM, 03:30:00.500 PM)
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

                target_dt_ist = now_ist.replace(
                    hour=parsed.hour,
                    minute=parsed.minute,
                    second=parsed.second,
                    microsecond=ms * 1000
                )

                if target_dt_ist <= now_ist:
                    target_dt_ist += timedelta(days=1)

            except Exception as e:
                await event.edit(f"```text\n[!] Time error: {e}\nTry: .cron 9:00 PM @username YourMsg!\n```")
                return

        # Target Pre-Fetching
        target_dest = None
        reply_msg_id = None
        dest_label = target_raw

        try:
            if target_raw.lower() == "here":
                target_dest = await client.get_input_entity(event.chat_id)
                dest_label = "Current Chat"
            elif "t.me/" in target_raw:
                clean_link = target_raw.split("t.me/")[-1].strip("/")
                parts = clean_link.split("/")
                
                if parts[0] == "c" and len(parts) >= 3:
                    internal_chat_id = int("-100" + parts[1])
                    reply_msg_id = int(parts[2])
                    target_dest = await client.get_input_entity(internal_chat_id)
                    dest_label = f"Reply to Msg #{reply_msg_id} (Private Chat)"
                elif len(parts) >= 2 and not parts[0].lstrip("-").isdigit():
                    group_username = parts[0]
                    reply_msg_id = int(parts[1])
                    target_dest = await client.get_input_entity(group_username)
                    dest_label = f"Reply to Msg #{reply_msg_id} in @{group_username}"
                else:
                    raise ValueError("Invalid Message Link structure")
            else:
                if target_raw.startswith("@"):
                    target_dest = await client.get_input_entity(target_raw)
                elif target_raw.lstrip("-").isdigit():
                    target_dest = await client.get_input_entity(int(target_raw))
                else:
                    target_dest = await client.get_input_entity(target_raw)
                dest_label = str(target_raw)
        except Exception as e:
            await event.edit(f"```text\n[!] Target resolution failed: {e}\n```")
            return

        wait_sec = (target_dt_ist - now_ist).total_seconds()

        card = (
            "```text\n"
            "╔════「 ⚡ SYNCED ATOMIC SNIPER ⚡ 」════╗\n"
            "║\n"
            "╠─ 👤 MASTER   :: K E S H A V\n"
            f"╠─ 🎯 TARGET   :: {dest_label}\n"
            f"╠─ ⏰ EXECUTE  :: {target_dt_ist.strftime('%I:%M:%S.%f')[:-3]} {target_dt_ist.strftime('%p')} (IST)\n"
            f"╠─ ⏳ DELAY    :: {round(max(0, wait_sec), 3)}s remaining\n"
            "║\n"
            "╚════════════════════════════════════════════════╝\n"
            "```"
        )
        await event.edit(card)

        # High-Precision Atomic Dispatcher with Clock Offset Compensation
        async def atomic_dispatcher():
            try:
                # Calculate server clock offset dynamically against network time
                local_sys_time = datetime.now(IST).timestamp()
                network_sync_time = (await get_accurate_now()).timestamp()
                server_clock_skew = network_sync_time - local_sys_time

                target_utc = target_dt_ist.astimezone(UTC)
                target_epoch = target_utc.timestamp()

                while True:
                    # Apply server skew adjustment to epoch comparison
                    current_adjusted_time = time.time() + server_clock_skew
                    remaining = target_epoch - current_adjusted_time
                    
                    if remaining <= 0:
                        break
                    if remaining > 0.1:
                        await asyncio.sleep(remaining - 0.02)
                    else:
                        await asyncio.sleep(0.0001)

                # Fire immediately without any delay
                if reply_msg_id:
                    await client.send_message(target_dest, message_to_send, reply_to=reply_msg_id)
                else:
                    await client.send_message(target_dest, message_to_send)

            except Exception as err:
                await client.send_message(command_chat_id, f"```text\n[!] CRON FAILED!\nError: {err}\n```")

        asyncio.create_task(atomic_dispatcher())
