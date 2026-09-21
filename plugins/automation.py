import asyncio
from telethon import events
from telethon.tl.types import ChannelParticipantsAdmins

CANCEL_TAGALL = False

def setup(client):

    # --- .tagall <message> (Individual One-by-One Tagging) ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.tagall(?:\s+(.*))?'))
    async def tag_all(event):
        global CANCEL_TAGALL
        CANCEL_TAGALL = False

        if event.is_private:
            await event.edit("```text\n[!] This command only works in groups.\n```")
            return

        custom_msg = event.pattern_match.group(1) or "Hello everyone!"
        chat = await event.get_input_chat()
        await event.delete()

        count = 0
        async for user in client.iter_participants(chat):
            if CANCEL_TAGALL:
                stop_notice = await client.send_message(chat, "```text\n[!] Tagall successfully stopped.\n```")
                await asyncio.sleep(2)
                await stop_notice.delete()
                break

            if getattr(user, 'bot', False) or getattr(user, 'deleted', False):
                continue

            name = user.first_name or "Member"
            mention_text = f"[{name}](tg://user?id={user.id}) {custom_msg}"

            try:
                await client.send_message(chat, mention_text)
                count += 1
                await asyncio.sleep(1.2)  # Safe delay to prevent Telegram flood wait
            except Exception:
                await asyncio.sleep(2)

    # --- .cancel ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.cancel$'))
    async def cancel_tagall(event):
        global CANCEL_TAGALL
        CANCEL_TAGALL = True
        await event.edit("```text\n┌───「 🛑 𝗧𝗔𝗚𝗔𝗟𝗟 𝗖𝗔𝗡𝗖𝗘𝗟𝗟𝗘𝗗 」\n└───「 Stopping active queue 」\n```")
        await asyncio.sleep(2)
        await event.delete()

    # --- .spam <count> <delay> <text> ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.spam\s+(\d+)\s+(\d+(?:\.\d+)?)\s+(.*)'))
    async def spam_loop(event):
        count = int(event.pattern_match.group(1))
        delay = float(event.pattern_match.group(2))
        text = event.pattern_match.group(3)

        if count > 20:
            count = 20

        await event.delete()
        chat = await event.get_input_chat()

        for _ in range(count):
            await client.send_message(chat, text)
            await asyncio.sleep(delay)
