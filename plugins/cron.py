import asyncio
from datetime import datetime, timedelta, timezone
from telethon import events

# IST Timezone fixed
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

        # Mode A: Relative countdown (e.g., in 10s)
        if time_raw.lower().startswith("in "):
            try:
                val_str = time_raw.lower().replace("in ", "").strip()
                unit = val_str[-1]
                val = float(val_str[:-1])
                if unit == 's':
                    target_dt = now_ist + timedelta(seconds=val)
                elif unit == 'm':
                    target_dt = now_ist + timedelta(minutes=val)
                elif unit == 'h':
                    target_dt = now_ist + timedelta(hours=val)
                else:
                    raise ValueError("Unknown unit")
            except Exception:
                await event.edit("```text\n[!] Invalid format. Try: .cron in 10s | here | msg\n```")
                return
        else:
            # Mode B: Exact Clock Time (e.g., 03:30 PM)
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

                # Agar time nikal gaya hai toh kal ke liye set karo
                if target_dt <= now_ist:
                    target_dt += timedelta(days=1)

            except Exception as e:
                await event.edit(f"```text\n[!] Time format error: {e}\nTry: .cron 03:30:00 PM | here | msg\n```")
                return

        wait_seconds = (target_dt - now_ist).total_seconds()
        if wait_seconds < 0:
            wait_seconds = 0

        # Safe Target Resolution (String aur ID handle)
        if target_raw.lower() == "here":
            target_dest = event.chat_id
            dest_label = "Current Chat"
        else:
            try:
                target_dest = int(target_raw)
            except ValueError:
                target_dest = target_raw
            dest_label = str(target_dest)

        card = (
            "```text\n"
            "╔════「 ⏱️ 𝗔𝗧𝗢𝗠𝗜𝗖 𝗦𝗖𝗛𝗘𝗗𝗨𝗟𝗘𝗥 ⚡ 」════╗\n"
            "║\n"
            "╠─ 👤 MASTER   :: K E S H A V\n"
            f"╠─ 🎯 TARGET   :: {dest_label}\n"
            f"╠─ ⏰ EXECUTE  :: {target_dt.strftime('%I:%M:%S %p')} (IST)\n"
            f"╠─ ⏳ DELAY    :: {round(wait_seconds, 2)}s remaining\n"
            "║\n"
            "╚═════════════════════════════════════╝\n"
            "```"
        )
        await event.edit(card)

        # Bulletproof Background Dispatcher
        async def background_dispatcher():
            try:
                if wait_seconds > 0:
                    await asyncio.sleep(wait_seconds)
                await client.send_message(target_dest, message_to_send)
            except Exception as err:
                # Agar fail hua toh user ko chat me error bhejo
                await client.send_message(command_chat_id, f"```text\n[!] CRON TASK FAILED!\nTarget: {dest_label}\nError: {err}\n```")

        # Start task without blocking the bot
        asyncio.create_task(background_dispatcher())
