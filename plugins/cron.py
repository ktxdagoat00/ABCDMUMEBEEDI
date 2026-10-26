import asyncio
import time
from datetime import datetime, timedelta, timezone
from telethon import events

IST = timezone(timedelta(hours=5, minutes=30))

def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.cron\s+([^|]+)\|([^|]+)\|(.+)'))
    async def precision_cron(event):
        time_raw = event.pattern_match.group(1).strip()
        target_raw = event.pattern_match.group(2).strip()
        message_to_send = event.pattern_match.group(3).strip()
        command_chat_id = event.chat_id

        now_ist = datetime.now(IST)
        target_dt = None

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
                target_dt = now_ist + timedelta(seconds=val)
            except Exception:
                await event.edit("```text\n[!] Relative time error. Try: .cron in 10s | here | Hi\n```")
                return
        else:
            # Mode B: Exact Clock Time with Milliseconds (e.g., 03:30:00.500 PM)
            try:
                parts = time_raw.split()
                time_part = parts[0]
                ampm_part = parts[1].upper() if len(parts) > 1 else ""

                if "." in time_part:
                    hms, ms_str = time_part.split(".", 1)
                    ms = int(ms_str.ljust(3, "0")[:3])
                else:
                    hms = time_part
                    ms = 0

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
                await event.edit(f"```text\n[!] Time format error: {e}\nTry: .cron 03:30:00.000 PM | here | msg\n```")
                return

        # Safe Target & Post Link Resolution
        target_dest = None
        reply_msg_id = None
        dest_label = target_raw

        try:
            if target_raw.lower() == "here":
                target_dest = event.chat_id
                dest_label = "Current Chat"
            elif "t.me/" in target_raw:
                clean_link = target_raw.split("t.me/")[-1].strip("/")
                parts = clean_link.split("/")
                
                if parts[0] == "c" and len(parts) >= 3:
                    target_dest = int("-100" + parts[1])
                    reply_msg_id = int(parts[2])
                    dest_label = f"Reply to Msg #{reply_msg_id} (Private)"
                elif len(parts) >= 2 and not parts[0].lstrip("-").isdigit():
                    target_dest = parts[0]
                    if not target_dest.startswith("@"):
                        target_dest = "@" + target_dest
                    reply_msg_id = int(parts[1])
                    dest_label = f"Reply to Msg #{reply_msg_id} in {target_dest}"
                else:
                    raise ValueError("Invalid Telegram link format")
            else:
                try:
                    target_dest = int(target_raw)
                except ValueError:
                    target_dest = target_raw
                dest_label = str(target_dest)
        except Exception as e:
            await event.edit(f"```text\n[!] Target/Link error: {e}\n```")
            return

        wait_sec = (target_dt - datetime.now(IST)).total_seconds()

        card = (
            "```text\n"
            "╔════「 ⚡️ ATOMIC MS-ACCURATE SCHEDULER ⚡️ 」════╗\n"
            "║\n"
            "╠─ 👤 MASTER   :: K E S H A V\n"
            f"╠─ 🎯 TARGET   :: {dest_label}\n"
            f"╠─ ⏰ EXECUTE  :: {target_dt.strftime('%I:%M:%S.%f')[:-3]} {target_dt.strftime('%p')} (IST)\n"
            f"╠─ ⏳ DELAY    :: {round(max(0, wait_sec), 3)}s remaining\n"
            "║\n"
            "╚════════════════════════════════════════════════╝\n"
            "```"
        )
        await event.edit(card)

        # Zero-Lag Background Dispatcher with High-Precision Spin-Lock
        async def atomic_dispatcher():
            try:
                target_epoch = target_dt.timestamp()
                while True:
                    remaining = target_epoch - time.time()
                    if remaining <= 0:
                        break
                    
                    if remaining > 0.2:
                        await asyncio.sleep(remaining - 0.1)
                    else:
                        await asyncio.sleep(0.001)

                # Send or reply to specific post instantly on exact microsecond match
                if reply_msg_id:
                    await client.send_message(target_dest, message_to_send, reply_to=reply_msg_id)
                else:
                    await client.send_message(target_dest, message_to_send)

            except Exception as err:
                await client.send_message(command_chat_id, f"```text\n[!] CRON FAILED!\nTarget: {dest_label}\nError: {err}\n```")

        asyncio.create_task(atomic_dispatcher())
