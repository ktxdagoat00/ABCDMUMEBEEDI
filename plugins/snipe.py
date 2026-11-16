import re
import time
import asyncio
from datetime import datetime, timedelta, timezone
from telethon import events

IST = timezone(timedelta(hours=5, minutes=30))

def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=re.compile(r'^\.snipe\b', re.IGNORECASE)))
    async def handle_snipe(event):
        raw_text = event.raw_text[len('.snipe'):].strip()
        parts = [p.strip() for p in raw_text.split('/')]
        
        if len(parts) < 3:
            await event.edit("```text\n❌ Format Error!\nUse: .snipe hh:mm:ss am/pm / target / message\n```")
            return

        time_str = parts[0]
        target_raw = parts[1]
        msg_content = "/".join(parts[2:])

        # 1. Parse Target Time (IST Aware)
        now_ist = datetime.now(IST)
        
        time_formats = ["%I:%M:%S %p", "%H:%M:%S", "%I:%M %p", "%H:%M"]
        parsed_time = None
        for fmt in time_formats:
            try:
                parsed_time = datetime.strptime(time_str.upper(), fmt).time()
                break
            except ValueError:
                continue
        
        if not parsed_time:
            await event.edit(f"```text\n❌ Invalid time format: {time_str}\nUse hh:mm:ss am/pm\n```")
            return

        target_dt = datetime.combine(now_ist.date(), parsed_time).replace(tzinfo=IST)
        if target_dt <= now_ist:
            target_dt += timedelta(days=1)

        await event.edit(f"```text\n⏳ Pre-calculating & caching target...\nTarget Time: {target_dt.strftime('%I:%M:%S.%f')[:-3]} {target_dt.strftime('%p')} (IST)\n```")

        # 2. Resolve Target Entity & Pre-fetch ahead of time (0 lag preparation)
        entity = None
        reply_to_msg_id = None

        try:
            link_match = re.search(r't\.me/(?:c/(\d+)|([a-zA-Z0-9_]+))/(\d+)', target_raw)
            if link_match:
                if link_match.group(1):
                    chat_part = int("-100" + link_match.group(1))
                else:
                    chat_part = link_match.group(2)
                reply_to_msg_id = int(link_match.group(3))
                entity = await client.get_entity(chat_part)
            else:
                if target_raw.startswith("-100") or target_raw.isdigit() or target_raw.startswith("-"):
                    entity = await client.get_entity(int(target_raw))
                else:
                    entity = await client.get_entity(target_raw)
        except Exception as e:
            await event.edit(f"```text\n❌ Failed to resolve target ({target_raw}): {e}\n```")
            return

        # 3. High-Precision Millisecond-Accurate Timer (Active busy-wait spin-lock)
        target_epoch = target_dt.timestamp()
        
        card = (
            "```text\n"
            "╔════「 🎯 ATOMIC PRECISION SNIPER 🎯 」════╗\n"
            "║\n"
            f"╠─ 🎯 TARGET   :: {target_raw}\n"
            f"╠─ ⏰ EXECUTE  :: {target_dt.strftime('%I:%M:%S.%f')[:-3]} {target_dt.strftime('%p')} (IST)\n"
            "╠─ ⚡️ STATUS   :: Armed & Zero-Lag Ready\n"
            "║\n"
            "╚════════════════════════════════════════════╝\n"
            "```"
        )
        await event.edit(card)

        # Background zero-lag runner so your bot stays responsive
        async def atomic_sniper():
            try:
                while True:
                    current_epoch = time.time()
                    diff = target_epoch - current_epoch
                    
                    if diff <= 0:
                        break
                    elif diff > 1.0:
                        await asyncio.sleep(diff - 0.5)
                    elif diff > 0.05:
                        await asyncio.sleep(0.01)
                    else:
                        # Active busy-wait for final 50ms to eliminate sleep jitter/lag
                        while time.time() < target_epoch:
                            pass
                        break

                # 4. Fire instantly
                if reply_to_msg_id:
                    await client.send_message(entity, msg_content, reply_to=reply_to_msg_id)
                else:
                    await client.send_message(entity, msg_content)

            except Exception as err:
                await client.send_message("me", f"```text\n❌ Snipe Failed!\nTarget: {target_raw}\nError: {err}\n```")

        asyncio.create_task(atomic_sniper())
