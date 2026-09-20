import asyncio
from telethon import events

def setup(client):

    # --- .ghost <seconds> <text> (Supports decimals e.g. 0.5s) ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ghost(?:\s+([0-9]+(?:\.[0-9]+)?))?(?:\s+(.*))?'))
    async def ghost_message(event):
        sec_str = event.pattern_match.group(1)
        text = event.pattern_match.group(2)

        if not sec_str or not text:
            await event.edit("```text\n[!] Usage: .ghost <seconds> <text>\nExample: .ghost 0.5 Secret message\n```")
            return

        try:
            wait_time = float(sec_str)
        except ValueError:
            await event.edit("```text\n[!] Invalid time format. Use seconds e.g. 0.5 or 3\n```")
            return

        await event.edit(text)
        await asyncio.sleep(wait_time)
        try:
            await event.delete()
        except Exception:
            pass
