import asyncio
import time
from datetime import datetime, timedelta
from telethon import events

def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.cron\s+([^|]+)\|([^|]+)\|(.+)'))
    async def precision_cron(event):
        time_raw = event.pattern_match.group(1).strip()
        target_raw = event.pattern_match.group(2).strip()
        message_to_send = event.pattern_match.group(3).strip()

        # Parse Time: HH:MM:SS.mmm AM/PM
        try:
            # Normalize format
            parts = time_raw.split()
            time_part = parts[0]
            ampm_part = parts[1].upper() if len(parts) > 1 else ""

            # Check if milliseconds provided
            if "." in time_part:
                hms, ms_str = time_part.split(".", 1)
                ms = int(ms_str.ljust(3, "0")[:3])
            else:
                hms = time_part
                ms = 0

            time_full_str = f"{hms} {ampm_part}".strip()
            format_str = "%I:%M:%S %p" if ampm_part else "%H:%M:%S"
            parsed_time = datetime.strptime(time_full_str, format_str)

            now = datetime.now()
            target_dt = now.replace(
                hour=parsed_time.hour,
                minute=parsed_time.minute,
                second=parsed_time.second,
                microsecond=ms * 1000
            )

            # Agar time nikal chuka hai toh kal ke liye schedule karo
            if target_dt <= now:
                target_dt += timedelta(days=1)

            target_epoch = target_dt.timestamp()

        except Exception as e:
            await event.edit(f"```text\n[!] Invalid time format: {e}\nFormat: .cron HH:MM:SS.mmm AM/PM | target | message\n```")
            return

        # Resolve Target
        try:
            if target_raw.lower() == "here":
                target_peer = await event.get_input_chat()
                dest_label = "Current Chat"
            else:
                target_peer = await client.get_input_entity(target_raw)
                dest_label = target_raw
        except Exception as e:
            await event.edit(f"```text\n[!] Target Error: {e}\n```")
            return

        card = (
            "```text\n"
            "╔════「 ⏱️ 𝗔𝗧𝗢𝗠𝗜𝗖 𝗦𝗖𝗛𝗘𝗗𝗨𝗟𝗘𝗥 ⚡ 」════╗\n"
            "║\n"
            "╠─ 👤 MASTER   :: K E S H A V\n"
            f"╠─ 🎯 TARGET   :: {dest_label}\n"
            f"╠─ ⏰ EXECUTE  :: {target_dt.strftime('%I:%M:%S')}.{ms:03d} {ampm_part}\n"
            "╠─ ⚡ SYNC     :: Microsecond Busy-Wait Lock\n"
            "║\n"
            "╚═════════════════════════════════════╝\n"
            "```"
        )
        await event.edit(card)

        # High-Precision Dual Phase Wait
        async def atomic_dispatcher():
            # Phase 1: Sleep until last 200ms
            while True:
                remaining = target_epoch - time.time()
                if remaining <= 0.2:
                    break
                await asyncio.sleep(max(remaining - 0.2, 0.05))

            # Phase 2: CPU Spin-lock (No asyncio delays for raw ms precision)
            while time.time() < target_epoch:
                pass

            # Phase 3: Instant Dispatch
            await client.send_message(target_peer, message_to_send)

        asyncio.create_task(atomic_dispatcher())
