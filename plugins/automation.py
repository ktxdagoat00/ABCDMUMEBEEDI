import asyncio
from telethon import events
from telethon.errors import FloodWaitError

CANCEL_TAGALL = False

async def run_tagall_task(client, chat, custom_msg):
    global CANCEL_TAGALL
    try:
        async for user in client.iter_participants(chat):
            if CANCEL_TAGALL:
                stop_notice = await client.send_message(chat, "```text\n[!] Tagall stopped.\n```")
                await asyncio.sleep(2)
                await stop_notice.delete()
                break

            if getattr(user, 'bot', False) or getattr(user, 'deleted', False):
                continue

            name = user.first_name or "Member"
            mention_text = f"[{name}](tg://user?id={user.id}) {custom_msg}"

            try:
                await client.send_message(chat, mention_text)
                await asyncio.sleep(1.2)
            except FloodWaitError as f:
                await asyncio.sleep(f.seconds + 1)
            except Exception:
                await asyncio.sleep(1)
    except Exception as e:
        print(f"[Tagall Error] {e}")

def setup(client):

    # --- .tagall (Isolated Async Task - Zero Lag) ---
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

        # Non-blocking background worker
        asyncio.create_task(run_tagall_task(client, chat, custom_msg))

    # --- .cancel ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.cancel$'))
    async def cancel_tagall(event):
        global CANCEL_TAGALL
        CANCEL_TAGALL = True
        await event.edit("```text\n┌───「 🛑 𝗧𝗔𝗚𝗔𝗟𝗟 𝗖𝗔𝗡𝗖𝗘𝗟𝗟𝗘𝗗 」\n└───「 Stopping background queue 」\n```")
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

        async def run_spam():
            for _ in range(count):
                try:
                    await client.send_message(chat, text)
                    await asyncio.sleep(delay)
                except FloodWaitError as f:
                    await asyncio.sleep(f.seconds + 1)
                except Exception:
                    break

        asyncio.create_task(run_spam())
