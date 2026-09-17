import re
import asyncio
from telethon import events

def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.spam(?:\s+(.*))?'))
    async def spam_handler(event):
        raw_args = event.pattern_match.group(1)
        reply = await event.get_reply_message()

        if not raw_args:
            await event.edit(
                "```text\n"
                "┌───「 ⚠️ 𝗦𝗣𝗔𝗠 𝗨𝗦𝗔𝗚𝗘 」\n"
                "├─ Format :: .spam <count> <delay> <msg>\n"
                "└─ Note   :: Max limit is 20 msgs\n"
                "```"
            )
            return

        parts = raw_args.split(maxsplit=2)
        
        try:
            count = int(parts[0])
        except (IndexError, ValueError):
            await event.edit("```text\n[!] Error: Invalid message count!\n```")
            return

        # Delay parse (agar user ne '1s' ya '0.5s' likha ho to 's' strip kar dega)
        try:
            delay_str = parts[1].rstrip("sS")
            delay = float(delay_str)
            if delay < 0.1:
                delay = 0.1
        except (IndexError, ValueError):
            await event.edit("```text\n[!] Error: Invalid delay (e.g. 1 or 0.5)!\n```")
            return

        # Text extraction: ya to command argument se ya fir replied message se
        text_to_spam = ""
        if len(parts) > 2:
            text_to_spam = parts[2].strip()
        elif reply and reply.raw_text:
            text_to_spam = reply.raw_text

        if not text_to_spam and not (reply and reply.media):
            await event.edit("```text\n[!] Error: Message provide karo ya kisi msg par reply karo!\n```")
            return

        # Strict safety limit
        if count > 20:
            count = 20

        # Command trigger delete
        await event.delete()
        chat = await event.get_input_chat()

        for _ in range(count):
            if reply and not text_to_spam:
                await client.send_message(chat, reply)
            else:
                await client.send_message(chat, text_to_spam)
            await asyncio.sleep(delay)
