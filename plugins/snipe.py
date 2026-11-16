import re
import time
import asyncio
from datetime import datetime, timedelta, timezone
from telethon import events

IST = timezone(timedelta(hours=5, minutes=30))

def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=re.compile(r'^\.snipe\s+([^|]+)\|([^|]+)\|(.+)', re.IGNORECASE)))
    async def handle_snipe(event):
        time_str = event.pattern_match.group(1).strip()
        target_raw = event.pattern_match.group(2).strip()
        msg_content = event.pattern_match.group(3).strip()

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
            await event.edit(f"```text\n❌ Invalid time format: {time_str}\nUse: .snipe hh:mm:ss am/pm | target_link | message\n```")
            return

        target_dt = datetime.combine(now_ist.date(), parsed_time).replace(tzinfo=IST)
        if target_dt <= now_ist:
            target_dt += timedelta(days=1)

        await event.edit(f"```text\n⏳ Pre-calculating & caching target...\nTarget Time: {target_dt.strftime('%I:%M:%S.%f')[:-3]} {target_dt.strftime('%p')} (IST)\n```")

        # 2. Robust Link & Target Resolution
        target_dest = None
        reply_to_msg_id = None

        try:
            # Match links like https://t.me/c/12345/6789 or https://t.me/groupname/6789
            link_match = re.search(r'(?:https?://)?t\.me/(?:c/(\d+)|([a-zA-Z0-9_]+))/(\d+)', target_raw)
            if link_match:
                if link_match.group(1):
                    # Private group/channel (-100 prefix required for Telethon)
                    chat_part = int("-100" + link_match.group(1))
                else:
                    # Public group/channel username
                    chat_part = link_match.group(2)
                    if not chat_part.startswith("@"):
                        chat_part = "@" + chat_part
                
                reply_to_msg_id = int(link_match.group(3))

                # Pre-fetch target message to auto-cache peer access hash & entities
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

        # Background zero-lag runner
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
                        # Active busy-wait for final 50ms
                        while time.time() < target_epoch:
                            pass
                        break

                # 4. Fire instantly as a reply to specified post
                if reply_to_msg_id:
                    await client.send_message(target_dest, msg_content, reply_to=reply_to_msg_id)
                else:
                    await client.send_message(target_dest, msg_content)

            except Exception as err:
                await client.send_message("me", f"```text\n❌ Snipe Failed!\nTarget: {target_raw}\nError: {err}\n```")

        asyncio.create_task(atomic_sniper())
