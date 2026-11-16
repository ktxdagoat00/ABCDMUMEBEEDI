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
        target_dest = None
        reply_to_msg_id = None

        try:
            # Match post links like t.me/c/12345/6789 or t.me/groupname/6789
            link_match = re.search(r't\.me/(?:c/(\d+)|([a-zA-Z0-9_]+))/(\d+)', target_raw)
            if link_match:
                if link_match.group(1):
                    chat_part = int("-100" + link_match.group(1))
                else:
                    chat_part = link_match.group(2)
                    if not chat_part.startswith("@"):
                        chat_part = "@" + chat_part
                
                reply_to_msg_id = int(link_match.group(3))

                # Fetching message caches both entity access_hash and target message ID safely
                target_msg = await client.get_messages(chat_part, ids=reply_to_msg_id)
                if target_msg:
                    target_dest = target_msg.peer_id
                else:
                    target_dest = chat_part
            else:
                if target_raw.lower() == "here":
                    target_dest = event.chat_id
                elif target_raw.startswith("-100") or target_raw.lstrip("-").isdigit():
                    target_dest = int(target_raw)
                else:
                    target_dest = target_raw
                
                # Warm up entity cache
                await client.get_entity(target_dest)

        except Exception as e:
            await event.edit(f"```text\n❌ Failed to resolve target ({target_raw}): {e}\nMake sure bot is joined in that group!\n```")
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
                    await client.send_message(target_dest, msg_content, reply_to=reply_to_msg_id)
                else:
                    await client.send_message(target_dest, msg_content)

            except Exception as err:
                await client.send_message("me", f"```text\n❌ Snipe Failed!\nTarget: {target_raw}\nError: {err}\n```")

        asyncio.create_task(atomic_sniper())
